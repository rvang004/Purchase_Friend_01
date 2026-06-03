"""Deterministic adapter for the local fake store E2E tests."""

from __future__ import annotations

import logging
import re
import urllib.parse
from typing import Any

logger = logging.getLogger(__name__)


class FakeStoreAdapter:
    """Adapter for tests/fixtures/fake_store pages.

    This is intentionally boring and selector-stable. Real stores can be chaos;
    tests should not be. Tests that flake are just bugs wearing tap shoes.
    """

    name = "fake_store"

    async def login(self, page: Any, account: dict[str, Any]) -> bool:
        try:
            await page.goto(account["site"], wait_until="networkidle")
            await page.locator('[data-testid="email"]').fill(account["email"])
            await page.locator('[data-testid="password"]').fill(account["password"])
            await page.locator('[data-testid="login-submit"]').click()
            await page.wait_for_load_state("networkidle")
            return "logged-in" in page.url
        except Exception as exc:
            logger.error("Fake store login failed: %s", exc)
            return False

    async def navigate_to_product(self, page: Any, product_url: str) -> bool:
        try:
            await page.goto(product_url, wait_until="networkidle")
            return await page.locator('[data-testid="product-page"]').count() == 1
        except Exception as exc:
            logger.error("Fake store product navigation failed: %s", exc)
            return False

    async def get_item_price(self, page: Any) -> float | None:
        try:
            text = await page.locator('[data-testid="price"]').inner_text()
            match = re.search(r"\d+\.?\d*", text.replace(",", ""))
            return float(match.group()) if match else None
        except Exception as exc:
            logger.error("Fake store price extraction failed: %s", exc)
            return None

    async def set_quantity(self, page: Any, quantity: int) -> int:
        if quantity <= 1:
            return 1
        try:
            qty = page.locator('[data-testid="quantity"]')
            await qty.fill(str(quantity))
            value = await qty.input_value()
            return int(value)
        except Exception as exc:
            logger.error("Fake store quantity set failed: %s", exc)
            return 1

    async def add_to_cart(self, page: Any, *, dry_run: bool = False) -> bool:
        try:
            button = page.locator('[data-testid="add-to-cart"]')
            if await button.count() != 1:
                return False
            if dry_run:
                return True
            await button.click()
            await page.wait_for_load_state("networkidle")
            return "/cart" in page.url
        except Exception as exc:
            logger.error("Fake store add-to-cart failed: %s", exc)
            return False

    async def navigate_to_cart(self, page: Any) -> bool:
        try:
            await page.goto(self._base_url(page.url) + "/cart", wait_until="networkidle")
            return await page.locator('[data-testid="cart-page"]').count() == 1
        except Exception as exc:
            logger.error("Fake store cart navigation failed: %s", exc)
            return False

    async def checkout(self, page: Any, *, dry_run: bool = False) -> bool:
        try:
            button = page.locator('[data-testid="checkout"]')
            if await button.count() != 1:
                return False
            if dry_run:
                return True
            await button.click()
            await page.wait_for_load_state("networkidle")
            return "/checkout" in page.url
        except Exception as exc:
            logger.error("Fake store checkout failed: %s", exc)
            return False

    async def select_shipping_address(
        self,
        page: Any,
        address: dict | None = None,
        *,
        dry_run: bool = False,
    ) -> bool:
        try:
            button = page.locator('[data-testid="use-address"]')
            if await button.count() != 1:
                return True
            if dry_run:
                return True
            await button.click()
            await page.wait_for_timeout(100)
            return True
        except Exception as exc:
            logger.error("Fake store address selection failed: %s", exc)
            return False

    async def complete_purchase(
        self,
        page: Any,
        *,
        dry_run: bool = False,
        review_mode: bool = False,
    ) -> bool:
        try:
            button = page.locator('[data-testid="place-order"]')
            if await button.count() != 1:
                return False
            if dry_run or review_mode:
                return True
            await button.click()
            await page.wait_for_load_state("networkidle")
            return "/confirmation" in page.url
        except Exception as exc:
            logger.error("Fake store complete purchase failed: %s", exc)
            return False

    @staticmethod
    def _base_url(url: str) -> str:
        parsed = urllib.parse.urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
