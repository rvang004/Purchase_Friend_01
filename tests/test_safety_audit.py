import asyncio
import json
import tempfile
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from models import Account, PurchaseResult, PurchaseTask
from purchase_history import PurchaseHistory
from purchase_policy import spend_amount, validate_purchase_result, validate_task_for_account
from scheduler import PurchaseScheduler


class DummyCredentialManager:
    def __init__(self):
        self.saved_accounts = None

    def load_credentials(self):
        return {}

    def save_credentials(self, accounts):
        self.saved_accounts = accounts
        return True


def account_dict(**overrides):
    data = {
        "site": "https://example.test/login",
        "email": "roger@example.test",
        "password": "secret",
        "payment_method": "credit_card",
        "monthly_limit": 100,
        "price_limit_per_item": 50,
        "price_limit_enabled": True,
        "quantity_limit_per_item": 3,
        "spent_this_month": 10,
    }
    data.update(overrides)
    return data


def task_dict(**overrides):
    data = {
        "id": "task_1",
        "account_id": "acct_1",
        "product_url": "https://example.test/product/1",
        "schedule_type": "once",
        "run_time": "09:00",
        "quantity": 2,
        "enabled": True,
        "created": "2026-06-03T08:00:00",
        "last_run": None,
    }
    data.update(overrides)
    return data


class ModelTests(unittest.TestCase):
    def test_purchase_task_validates_run_time(self):
        with self.assertRaises(ValueError):
            PurchaseTask.from_dict(task_dict(run_time="banana"))

    def test_weekly_task_requires_valid_days(self):
        with self.assertRaises(ValueError):
            PurchaseTask.from_dict(task_dict(schedule_type="weekly", days=["Funday"]))

    def test_account_parses_money_as_decimal(self):
        account = Account.from_dict("acct_1", account_dict(monthly_limit="123.45"))
        self.assertEqual(account.monthly_limit, Decimal("123.45"))


class PolicyTests(unittest.TestCase):
    def test_pre_policy_blocks_quantity_limit(self):
        account = Account.from_dict("acct_1", account_dict(quantity_limit_per_item=1))
        task = PurchaseTask.from_dict(task_dict(quantity=2))

        decision = validate_task_for_account(task, account)

        self.assertFalse(decision.allowed)
        self.assertIn("Quantity", decision.reason)

    def test_pre_policy_blocks_monthly_limit_reached(self):
        account = Account.from_dict("acct_1", account_dict(monthly_limit=10, spent_this_month=10))
        task = PurchaseTask.from_dict(task_dict())

        decision = validate_task_for_account(task, account)

        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "Monthly limit reached")

    def test_post_policy_blocks_unverified_live_price(self):
        account = Account.from_dict("acct_1", account_dict())
        task = PurchaseTask.from_dict(task_dict())
        result = PurchaseResult.from_engine_result(
            task,
            "acct_1",
            {"success": True, "product_url": task.product_url, "timestamp": "2026-06-03T09:00:00"},
            dry_run=False,
        )

        decision = validate_purchase_result(account, result)

        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "Price could not be verified")

    def test_spend_amount_uses_order_total(self):
        task = PurchaseTask.from_dict(task_dict())
        result = PurchaseResult.from_engine_result(
            task,
            "acct_1",
            {
                "success": True,
                "product_url": task.product_url,
                "timestamp": "2026-06-03T09:00:00",
                "item_price": 20,
                "quantity": 2,
                "order_total": 45.25,
            },
            dry_run=False,
        )

        self.assertEqual(spend_amount(result), Decimal("45.25"))


class HistoryTests(unittest.TestCase):
    def test_history_records_jsonl_events(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            history = PurchaseHistory(str(Path(tmp_dir) / "history.jsonl"))
            history.record_policy_block(task_id="task_1", account_id="acct_1", reason="Nope")

            events = history.read_events()

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "policy_block")
        self.assertEqual(events[0]["error"], "Nope")


class SchedulerTests(unittest.TestCase):
    def test_check_if_should_run_validates_schedule(self):
        scheduler = PurchaseScheduler(
            accounts={},
            cred_manager=DummyCredentialManager(),
            history=PurchaseHistory("unused.jsonl"),
        )
        due = scheduler.check_if_should_run(task_dict(run_time="09:30"), datetime(2026, 6, 3, 9, 30))

        self.assertTrue(due)

    def test_execute_task_blocks_before_browser_when_quantity_exceeds_limit(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            history = PurchaseHistory(str(Path(tmp_dir) / "history.jsonl"))
            scheduler = PurchaseScheduler(
                accounts={"acct_1": account_dict(quantity_limit_per_item=1)},
                cred_manager=DummyCredentialManager(),
                history=history,
            )

            with patch("scheduler.run_purchase") as mocked_run:
                result = asyncio.run(scheduler.execute_task(task_dict(quantity=2)))

            self.assertFalse(result["success"])
            mocked_run.assert_not_called()
            self.assertEqual(history.read_events()[0]["event_type"], "policy_block")

    def test_execute_task_records_success_and_updates_monthly_spend(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cred_manager = DummyCredentialManager()
            history = PurchaseHistory(str(Path(tmp_dir) / "history.jsonl"))
            accounts = {"acct_1": account_dict(spent_this_month=10)}
            scheduler = PurchaseScheduler(
                accounts=accounts,
                cred_manager=cred_manager,
                history=history,
            )

            async def fake_run_purchase(account, product_url, quantity=1, dry_run=False):
                return {
                    "success": True,
                    "account_id": account["id"],
                    "product_url": product_url,
                    "timestamp": "2026-06-03T09:00:00",
                    "item_price": 20,
                    "quantity": quantity,
                    "order_total": 40,
                    "error": None,
                }

            raw_task = task_dict(quantity=2)
            with patch("scheduler.run_purchase", side_effect=fake_run_purchase):
                result = asyncio.run(scheduler.execute_task(raw_task, dry_run=False))

            self.assertTrue(result["success"])
            self.assertIsNotNone(raw_task["last_run"])
            self.assertEqual(accounts["acct_1"]["spent_this_month"], 50.0)
            self.assertIs(cred_manager.saved_accounts, accounts)
            events = history.read_events()
            self.assertEqual(events[-1]["event_type"], "purchase_result")
            self.assertEqual(events[-1]["order_total"], 40.0)

    def test_execute_task_dry_run_does_not_update_spend(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cred_manager = DummyCredentialManager()
            history = PurchaseHistory(str(Path(tmp_dir) / "history.jsonl"))
            accounts = {"acct_1": account_dict(spent_this_month=10)}
            scheduler = PurchaseScheduler(
                accounts=accounts,
                cred_manager=cred_manager,
                history=history,
            )

            async def fake_run_purchase(account, product_url, quantity=1, dry_run=False):
                return {
                    "success": True,
                    "product_url": product_url,
                    "timestamp": "2026-06-03T09:00:00",
                    "item_price": 20,
                    "quantity": quantity,
                    "error": None,
                }

            with patch("scheduler.run_purchase", side_effect=fake_run_purchase):
                result = asyncio.run(scheduler.execute_task(task_dict(quantity=2), dry_run=True))

            self.assertTrue(result["success"])
            self.assertEqual(accounts["acct_1"]["spent_this_month"], 10)
            self.assertIsNone(cred_manager.saved_accounts)


if __name__ == "__main__":
    unittest.main()
