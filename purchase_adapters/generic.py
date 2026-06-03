"""Generic fallback store adapter."""

from __future__ import annotations

from typing import Any

import purchase_actions as actions


class GenericStoreAdapter:
    """Adapter that delegates to the existing generic selector actions."""

    name = "generic"

    async def login(self, page: Any, account: dict[str, Any]) -> bool:
        return await actions.login(page, account["site"], account["email"], account["password"])

    async def navigate_to_product(self, page: Any, product_url: str) -> bool:
        return await actions.navigate_to_product(page, product_url)

    async def get_item_price(self, page: Any) -> float | None:
        return await actions.get_item_price(page)

    async def set_quantity(self, page: Any, quantity: int) -> int:
        return await actions.set_quantity(page, quantity)

    async def add_to_cart(self, page: Any, *, dry_run: bool = False) -> bool:
        return await actions.add_to_cart(page, dry_run=dry_run)

    async def navigate_to_cart(self, page: Any) -> bool:
        return await actions.navigate_to_cart(page)

    async def checkout(self, page: Any, *, dry_run: bool = False) -> bool:
        return await actions.checkout(page, dry_run=dry_run)

    async def select_shipping_address(
        self,
        page: Any,
        address: dict | None = None,
        *,
        dry_run: bool = False,
    ) -> bool:
        return await actions.select_shipping_address(page, address, dry_run=dry_run)

    async def complete_purchase(
        self,
        page: Any,
        *,
        dry_run: bool = False,
        review_mode: bool = False,
    ) -> bool:
        return await actions.complete_purchase(
            page,
            dry_run=dry_run,
            review_mode=review_mode,
        )
