"""Adapter interface for site-specific purchase behavior."""

from __future__ import annotations

from typing import Any, Protocol


class StoreAdapter(Protocol):
    """Contract every store adapter must satisfy."""

    name: str

    async def login(self, page: Any, account: dict[str, Any]) -> bool: ...

    async def navigate_to_product(self, page: Any, product_url: str) -> bool: ...

    async def get_item_price(self, page: Any) -> float | None: ...

    async def set_quantity(self, page: Any, quantity: int) -> int: ...

    async def add_to_cart(self, page: Any, *, dry_run: bool = False) -> bool: ...

    async def navigate_to_cart(self, page: Any) -> bool: ...

    async def checkout(self, page: Any, *, dry_run: bool = False) -> bool: ...

    async def select_shipping_address(
        self,
        page: Any,
        address: dict | None = None,
        *,
        dry_run: bool = False,
    ) -> bool: ...

    async def complete_purchase(
        self,
        page: Any,
        *,
        dry_run: bool = False,
        review_mode: bool = False,
    ) -> bool: ...
