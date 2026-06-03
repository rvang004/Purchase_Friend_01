"""Validated domain models for Purchase Bot.

These are intentionally stdlib-only. Pydantic is lovely, but adding a new
runtime dependency before the project truly needs it would be peak yak-shaving.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

VALID_SCHEDULE_TYPES = {"once", "daily", "weekly"}
VALID_WEEKDAYS = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}


def parse_money(value: Any, *, default: Decimal | None = None) -> Decimal:
    """Parse money values safely as Decimal."""
    if value is None:
        if default is not None:
            return default
        raise ValueError("money value is required")

    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid money value: {value!r}") from exc

    if amount < Decimal("0"):
        raise ValueError("money value cannot be negative")
    return amount.quantize(Decimal("0.01"))


def money_to_json(value: Decimal | None) -> float | None:
    """Convert Decimal money to JSON-friendly float."""
    return None if value is None else float(value)


def parse_optional_datetime(value: Any) -> datetime | None:
    """Parse ISO datetime/date-ish strings into datetime when possible."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        raise ValueError("datetime value must be an ISO string")

    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        # Backward compatibility for old configs storing YYYY-MM-DD only.
        try:
            return datetime.fromisoformat(f"{value}T00:00:00")
        except ValueError as exc:
            raise ValueError(f"invalid ISO datetime: {value!r}") from exc


@dataclass(frozen=True)
class ShippingAddress:
    """Optional checkout address."""

    full_name: str = ""
    line1: str = ""
    line2: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    country: str = "US"

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ShippingAddress | None":
        if not data:
            return None
        return cls(
            full_name=str(data.get("full_name", "")).strip(),
            line1=str(data.get("line1", "")).strip(),
            line2=str(data.get("line2", "")).strip(),
            city=str(data.get("city", "")).strip(),
            state=str(data.get("state", "")).strip(),
            zip_code=str(data.get("zip_code", "")).strip(),
            country=str(data.get("country", "US")).strip() or "US",
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "full_name": self.full_name,
            "line1": self.line1,
            "line2": self.line2,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "country": self.country,
        }


@dataclass(frozen=True)
class Account:
    """Validated account settings without exposing behavior."""

    id: str
    site: str
    email: str
    password: str
    payment_method: str
    monthly_limit: Decimal
    price_limit_per_item: Decimal | None = None
    price_limit_enabled: bool = True
    quantity_limit_per_item: int | None = None
    shipping_address: ShippingAddress | None = None
    spent_this_month: Decimal = Decimal("0.00")

    @classmethod
    def from_dict(cls, account_id: str, data: dict[str, Any]) -> "Account":
        if not account_id:
            raise ValueError("account id is required")
        if not data.get("site"):
            raise ValueError(f"account {account_id}: site is required")
        if not data.get("email"):
            raise ValueError(f"account {account_id}: email is required")

        qty_limit = data.get("quantity_limit_per_item")
        if qty_limit in ("", None):
            qty_limit = None
        else:
            qty_limit = int(qty_limit)
            if qty_limit < 1:
                raise ValueError("quantity limit must be at least 1")

        price_limit = data.get("price_limit_per_item")
        parsed_price_limit = None if price_limit in ("", None) else parse_money(price_limit)

        return cls(
            id=account_id,
            site=str(data["site"]).strip(),
            email=str(data["email"]).strip(),
            password=str(data.get("password", "")),
            payment_method=str(data.get("payment_method", "credit_card")),
            monthly_limit=parse_money(data.get("monthly_limit", "0")),
            price_limit_per_item=parsed_price_limit,
            price_limit_enabled=bool(data.get("price_limit_enabled", True)),
            quantity_limit_per_item=qty_limit,
            shipping_address=ShippingAddress.from_dict(data.get("shipping_address")),
            spent_this_month=parse_money(data.get("spent_this_month", "0")),
        )


@dataclass
class PurchaseTask:
    """Validated purchase task."""

    id: str
    account_id: str
    product_url: str
    schedule_type: str
    run_time: str
    quantity: int = 1
    enabled: bool = True
    created: str | None = None
    last_run: str | None = None
    days: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PurchaseTask":
        task_id = str(data.get("id", "")).strip()
        if not task_id:
            raise ValueError("task id is required")

        schedule_type = str(data.get("schedule_type", "once")).strip()
        if schedule_type not in VALID_SCHEDULE_TYPES:
            raise ValueError(f"task {task_id}: invalid schedule_type {schedule_type!r}")

        run_time = str(data.get("run_time", "")).strip()
        try:
            datetime.strptime(run_time, "%H:%M")
        except ValueError as exc:
            raise ValueError(f"task {task_id}: run_time must be HH:MM") from exc

        quantity = int(data.get("quantity", 1))
        if quantity < 1:
            raise ValueError(f"task {task_id}: quantity must be at least 1")

        account_id = str(data.get("account_id", "")).strip()
        product_url = str(data.get("product_url", "")).strip()
        if not account_id:
            raise ValueError(f"task {task_id}: account_id is required")
        if not product_url:
            raise ValueError(f"task {task_id}: product_url is required")

        days = [str(day).strip() for day in data.get("days", []) if str(day).strip()]
        if schedule_type == "weekly":
            invalid_days = [day for day in days if day not in VALID_WEEKDAYS]
            if not days:
                raise ValueError(f"task {task_id}: weekly tasks require days")
            if invalid_days:
                raise ValueError(f"task {task_id}: invalid weekly days {invalid_days}")

        last_run = data.get("last_run")
        parse_optional_datetime(last_run)

        return cls(
            id=task_id,
            account_id=account_id,
            product_url=product_url,
            schedule_type=schedule_type,
            run_time=run_time,
            quantity=quantity,
            enabled=bool(data.get("enabled", True)),
            created=data.get("created"),
            last_run=last_run,
            days=days,
        )

    def to_dict(self) -> dict[str, Any]:
        data = {
            "id": self.id,
            "account_id": self.account_id,
            "product_url": self.product_url,
            "schedule_type": self.schedule_type,
            "run_time": self.run_time,
            "quantity": self.quantity,
            "enabled": self.enabled,
            "created": self.created,
            "last_run": self.last_run,
        }
        if self.days:
            data["days"] = self.days
        return data

    @property
    def last_run_date(self):
        parsed = parse_optional_datetime(self.last_run)
        return parsed.date() if parsed else None


@dataclass(frozen=True)
class PurchaseResult:
    """Normalized result for audit/history."""

    task_id: str
    account_id: str
    success: bool
    product_url: str
    timestamp: str
    error: str | None = None
    item_price: Decimal | None = None
    quantity: int = 1
    order_total: Decimal | None = None
    dry_run: bool = False

    @classmethod
    def from_engine_result(
        cls,
        task: PurchaseTask,
        account_id: str,
        result: dict[str, Any],
        *,
        dry_run: bool,
    ) -> "PurchaseResult":
        quantity = int(result.get("quantity") or task.quantity)
        item_price = result.get("item_price")
        parsed_price = None if item_price in (None, "") else parse_money(item_price)
        order_total = result.get("order_total")
        parsed_total = None if order_total in (None, "") else parse_money(order_total)
        if parsed_total is None and parsed_price is not None:
            parsed_total = (parsed_price * Decimal(quantity)).quantize(Decimal("0.01"))

        return cls(
            task_id=task.id,
            account_id=account_id,
            success=bool(result.get("success", False)),
            product_url=str(result.get("product_url") or task.product_url),
            timestamp=str(result.get("timestamp") or datetime.now().isoformat()),
            error=result.get("error"),
            item_price=parsed_price,
            quantity=quantity,
            order_total=parsed_total,
            dry_run=dry_run,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "account_id": self.account_id,
            "success": self.success,
            "product_url": self.product_url,
            "timestamp": self.timestamp,
            "error": self.error,
            "item_price": money_to_json(self.item_price),
            "quantity": self.quantity,
            "order_total": money_to_json(self.order_total),
            "dry_run": self.dry_run,
        }
