"""
Task scheduler for running purchases at specified times.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from models import Account, PurchaseResult, PurchaseTask
from purchase_engine import run_purchase
from purchase_history import PurchaseHistory
from purchase_policy import spend_amount, validate_purchase_result, validate_task_for_account
from utils import CredentialManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("purchase_bot.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class PurchaseScheduler:
    """Manages scheduled purchase execution."""

    def __init__(
        self,
        config_file: str = "config.json",
        cred_file: str = "credentials.enc",
        history_file: str = "purchase_history.jsonl",
        *,
        cred_manager: CredentialManager | None = None,
        accounts: dict[str, dict[str, Any]] | None = None,
        history: PurchaseHistory | None = None,
    ):
        self.config_file = config_file
        self.cred_manager = cred_manager or CredentialManager(cred_file=cred_file)
        self.accounts = accounts if accounts is not None else self.cred_manager.load_credentials()
        self.history = history or PurchaseHistory(history_file)

    def load_config(self) -> dict[str, Any]:
        """Load purchase tasks config."""
        if not Path(self.config_file).exists():
            logger.error("Config file not found: %s", self.config_file)
            return {"tasks": []}

        with open(self.config_file, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def save_config(self, config: dict[str, Any]) -> None:
        """Save updated config."""
        with open(self.config_file, "w", encoding="utf-8") as handle:
            json.dump(config, handle, indent=2)

    def validate_task(self, raw_task: dict[str, Any]) -> PurchaseTask | None:
        """Validate a raw config task, logging bad configs without crashing."""
        try:
            return PurchaseTask.from_dict(raw_task)
        except ValueError as exc:
            task_id = str(raw_task.get("id", "unknown"))
            account_id = raw_task.get("account_id")
            logger.error("Invalid task %s: %s", task_id, exc)
            self.history.record_policy_block(
                task_id=task_id,
                account_id=account_id,
                reason=f"Invalid task: {exc}",
            )
            return None

    def check_if_should_run(self, raw_task: dict[str, Any], current_time: datetime) -> bool:
        """Check if a task should run at the current time."""
        task = self.validate_task(raw_task)
        if task is None or not task.enabled:
            return False

        task_time = datetime.strptime(task.run_time, "%H:%M").time()
        current_date = current_time.date()

        if task.schedule_type == "once":
            return current_time.time() >= task_time and task.last_run is None

        if task.schedule_type == "daily":
            time_matches = (
                current_time.hour == task_time.hour
                and current_time.minute == task_time.minute
            )
            return time_matches and task.last_run_date != current_date

        if task.schedule_type == "weekly":
            weekday_matches = current_time.strftime("%a") in task.days
            time_matches = (
                current_time.hour == task_time.hour
                and current_time.minute == task_time.minute
            )
            return weekday_matches and time_matches and task.last_run_date != current_date

        return False

    async def execute_task(
        self,
        raw_task: dict[str, Any],
        dry_run: bool = False,
        mode: str | None = None,
    ) -> dict[str, Any]:
        """Execute a single purchase task with validation, policy, and audit."""
        run_mode = self._resolve_mode(mode, dry_run)
        audit_dry_run = run_mode != "live"
        task = self.validate_task(raw_task)
        if task is None:
            return {"success": False, "error": "Invalid task"}

        account_data = self.accounts.get(task.account_id)
        account = self._load_account(task.account_id, account_data)
        decision = validate_task_for_account(task, account)
        if not decision.allowed:
            logger.warning("Task %s blocked: %s", task.id, decision.reason)
            self.history.record_policy_block(
                task_id=task.id,
                account_id=task.account_id,
                reason=decision.reason,
                dry_run=audit_dry_run,
            )
            return {"success": False, "error": decision.reason}

        logger.info("Starting purchase for task %s using account %s", task.id, task.account_id)
        engine_account = dict(account_data or {})
        engine_account["id"] = task.account_id

        raw_result = await run_purchase(
            engine_account,
            task.product_url,
            quantity=task.quantity,
            dry_run=run_mode == "dry-run",
            mode=run_mode,
        )
        result = PurchaseResult.from_engine_result(
            task,
            task.account_id,
            raw_result,
            dry_run=audit_dry_run,
        )

        post_decision = validate_purchase_result(account, result)
        if not post_decision.allowed:
            logger.error("Purchase blocked/failed for %s: %s", task.id, post_decision.reason)
            self.history.record_policy_block(
                task_id=task.id,
                account_id=task.account_id,
                reason=post_decision.reason,
                dry_run=audit_dry_run,
            )
            if result.success:
                raw_result = {**raw_result, "success": False, "error": post_decision.reason}
                result = PurchaseResult.from_engine_result(
                    task,
                    task.account_id,
                    raw_result,
                    dry_run=audit_dry_run,
                )
        else:
            logger.info("Purchase policy passed for task %s", task.id)

        self.history.record_result(result)

        if result.success:
            logger.info("Purchase successful: %s", task.id)
            raw_task["last_run"] = datetime.now().isoformat()
            self._update_monthly_spend(task.account_id, result)
        else:
            logger.error("Purchase failed: %s", result.error)

        return result.to_dict()

    async def run_once(self, dry_run: bool = False, mode: str | None = None) -> None:
        """
        Single check cycle — loads tasks, runs whatever is due, then exits.
        Used by GitHub Actions so the workflow doesn't run forever.
        """
        config = self.load_config()
        current_time = datetime.now()

        logger.info("One-shot check at %s", current_time.strftime("%H:%M:%S"))
        await self._execute_due_tasks(config, current_time, dry_run=dry_run, mode=mode)

    async def run_scheduler(
        self,
        interval: int = 60,
        dry_run: bool = False,
        mode: str | None = None,
    ) -> None:
        """
        Main scheduler loop.

        Args:
            interval: Check interval in seconds
            dry_run: If True, simulate purchases without completing them
        """
        logger.info("Purchase scheduler started")

        try:
            while True:
                config = self.load_config()
                current_time = datetime.now()

                logger.info("Checking tasks at %s", current_time.strftime("%H:%M:%S"))
                await self._execute_due_tasks(config, current_time, dry_run=dry_run, mode=mode)
                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as exc:
            logger.error("Scheduler error: %s", exc)
            raise

    async def _execute_due_tasks(
        self,
        config: dict[str, Any],
        current_time: datetime,
        *,
        dry_run: bool,
        mode: str | None = None,
    ) -> None:
        run_mode = self._resolve_mode(mode, dry_run)
        tasks_to_run = [
            task for task in config.get("tasks", [])
            if self.check_if_should_run(task, current_time)
        ]

        if not tasks_to_run:
            logger.info("No tasks due right now")
            return

        logger.info("Found %s task(s) to execute", len(tasks_to_run))

        # Sequential execution avoids same-account spend races. Boring? Yes.
        # Accidentally overspending through concurrency? No thanks.
        results = []
        for task in tasks_to_run:
            results.append(await self.execute_task(task, dry_run=dry_run, mode=run_mode))

        self.save_config(config)
        success_count = sum(1 for result in results if result.get("success"))
        logger.info("Execution complete: %s/%s successful", success_count, len(results))

    @staticmethod
    def _resolve_mode(mode: str | None, dry_run: bool) -> str:
        if dry_run:
            return "dry-run"
        return mode or "live"

    def _load_account(self, account_id: str, account_data: dict[str, Any] | None) -> Account | None:
        if account_data is None:
            logger.error("Account '%s' not found", account_id)
            return None
        try:
            return Account.from_dict(account_id, account_data)
        except ValueError as exc:
            logger.error("Invalid account %s: %s", account_id, exc)
            return None

    def _update_monthly_spend(self, account_id: str, result: PurchaseResult) -> None:
        amount = spend_amount(result)
        if amount <= 0:
            return

        account_data = self.accounts.get(account_id)
        if account_data is None:
            return

        current_spend = Account.from_dict(account_id, account_data).spent_this_month
        new_spend = current_spend + amount
        account_data["spent_this_month"] = float(new_spend)

        if self.cred_manager.save_credentials(self.accounts):
            logger.info("Updated monthly spend for %s: $%s", account_id, new_spend)
        else:
            logger.error("Failed to save updated spend for %s", account_id)


async def main() -> None:
    """CLI entry point for scheduler."""
    parser = argparse.ArgumentParser(description="Purchase Bot Scheduler")
    parser.add_argument("--dry-run", action="store_true", help="Alias for --mode dry-run")
    parser.add_argument("--mode", choices=["dry-run", "review", "live"], default="review")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    args = parser.parse_args()

    scheduler = PurchaseScheduler()
    await scheduler.run_scheduler(interval=args.interval, dry_run=args.dry_run, mode=args.mode)


if __name__ == "__main__":
    asyncio.run(main())
