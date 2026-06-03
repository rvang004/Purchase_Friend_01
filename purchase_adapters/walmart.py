"""Walmart site adapter.

This adapter is intentionally conservative:
- no CAPTCHA bypass
- no MFA bypass
- no anti-bot evasion
- no live-site tests

It provides Walmart-specific selectors and falls back to generic actions where
safe. Real production reliability still needs validation against approved test
accounts/environments. Browser goblins do not become trustworthy by vibes.
"""

from __future__ import annotations

import logging
import re
import urllib.parse
from typing import Any

import purchase_actions as actions

logger = logging.getLogger(__name__)

AUTH_CHALLENGE_TEXT = (
    "captcha",
    "verification code",
    "two-step",
    "two step",
    "2-step",
    "multi-factor",
    "multifactor",
    "security check",
)


class WalmartStoreAdapter:
    """Adapter for Walmart retail pages."""

    name = "walmart"

    async def login(self, page: Any, account: dict[str, Any]) -> bool:
        """Submit Walmart login if a login form is present.

        If no login form is found, the adapter assumes an existing browser
        session may already be authenticated and lets the flow continue. It
        never attempts to bypass MFA/CAPTCHA/security challenges.
        """
        try:
            await page.goto(account["site"], wait_until="networkidle")
            if await self._auth_challenge_present(page):
                logger.warning("Walmart login requires manual verification")
                return False

            email = await first_visible(page, EMAIL_SELECTORS)
            if email is None:
                logger.info("No Walmart email field found; assuming existing session")
                return True

            await email.fill(account["email"])
            await click_first(page, CONTINUE_SELECTORS, required=False)
            await page.wait_for_timeout(750)

            if await self._auth_challenge_present(page):
                logger.warning("Walmart login requires manual verification after email step")
                return False

            password = await first_visible(page, PASSWORD_SELECTORS)
            if password is None:
                logger.warning("Walmart password field not found")
                return False

            await password.fill(account["password"])
            if not await click_first(page, SIGN_IN_SELECTORS, required=False):
                logger.warning("Walmart sign-in button not found")
                return False

            await page.wait_for_load_state("networkidle")
            if await self._auth_challenge_present(page):
                logger.warning("Walmart login requires manual verification after password step")
                return False

            logger.info("Walmart login submitted")
            return True
        except Exception as exc:
            logger.error("Walmart login failed: %s", exc)
            return False

    async def navigate_to_product(self, page: Any, product_url: str) -> bool:
        return await actions.navigate_to_product(page, product_url)

    async def get_item_price(self, page: Any) -> float | None:
        for selector in PRICE_SELECTORS:
            locator = await first_visible(page, [selector])
            if locator is None:
                continue
            try:
                price = parse_price_text(await locator.inner_text())
                if price is not None:
                    logger.info("Detected Walmart item price: $%s", price)
                    return price
            except Exception:
                continue

        logger.warning("Could not detect Walmart item price")
        return None

    async def set_quantity(self, page: Any, quantity: int) -> int:
        if quantity <= 1:
            return 1

        qty_input = await first_visible(page, QUANTITY_INPUT_SELECTORS)
        if qty_input is not None:
            try:
                await qty_input.fill(str(quantity))
                actual = await qty_input.input_value()
                return int(actual)
            except Exception as exc:
                logger.warning("Walmart quantity input failed: %s", exc)

        # Some Walmart pages use steppers. Click increment until requested qty.
        increment = await first_visible(page, QUANTITY_INCREMENT_SELECTORS)
        if increment is not None:
            try:
                for _ in range(quantity - 1):
                    await increment.click()
                    await page.wait_for_timeout(150)
                return quantity
            except Exception as exc:
                logger.warning("Walmart quantity stepper failed: %s", exc)

        return await actions.set_quantity(page, quantity)

    async def add_to_cart(self, page: Any, *, dry_run: bool = False) -> bool:
        button = await first_visible(page, ADD_TO_CART_SELECTORS)
        if button is None:
            return await actions.add_to_cart(page, dry_run=dry_run)
        if dry_run:
            logger.info("DRY RUN: Would click Walmart Add to cart")
            return True
        await button.click()
        await page.wait_for_timeout(1500)
        await actions.dismiss_mini_cart(page)
        return True

    async def navigate_to_cart(self, page: Any) -> bool:
        if await click_first(page, CART_LINK_SELECTORS, required=False):
            await page.wait_for_load_state("networkidle")
            return True

        try:
            parsed = urllib.parse.urlparse(page.url)
            await page.goto(f"{parsed.scheme}://{parsed.netloc}/cart", wait_until="networkidle")
            return True
        except Exception as exc:
            logger.warning("Walmart cart navigation failed: %s", exc)
            return await actions.navigate_to_cart(page)

    async def checkout(self, page: Any, *, dry_run: bool = False) -> bool:
        button = await first_visible(page, CHECKOUT_SELECTORS)
        if button is None:
            return await actions.checkout(page, dry_run=dry_run)
        if dry_run:
            logger.info("DRY RUN: Would click Walmart checkout")
            return True
        await button.click()
        await page.wait_for_load_state("networkidle")
        return True

    async def select_shipping_address(
        self,
        page: Any,
        address: dict | None = None,
        *,
        dry_run: bool = False,
    ) -> bool:
        if await self._auth_challenge_present(page):
            logger.warning("Walmart checkout requires manual verification")
            return False

        button = await first_visible(page, ADDRESS_CONFIRM_SELECTORS)
        if button is not None:
            if dry_run:
                logger.info("DRY RUN: Would confirm Walmart shipping address")
                return True
            await button.click()
            await page.wait_for_load_state("networkidle")
            return True

        return await actions.select_shipping_address(page, address, dry_run=dry_run)

    async def complete_purchase(
        self,
        page: Any,
        *,
        dry_run: bool = False,
        review_mode: bool = False,
    ) -> bool:
        if await self._auth_challenge_present(page):
            logger.warning("Walmart final purchase requires manual verification")
            return False

        button = await first_visible(page, PLACE_ORDER_SELECTORS)
        if button is None:
            return await actions.complete_purchase(page, dry_run=dry_run, review_mode=review_mode)
        if dry_run:
            logger.info("DRY RUN: Would click Walmart place order")
            return True
        if review_mode:
            logger.info("REVIEW MODE: Walmart place order button found; stopping")
            return True
        await button.click()
        await page.wait_for_load_state("networkidle")
        return True

    async def _auth_challenge_present(self, page: Any) -> bool:
        try:
            body = (await page.locator("body").inner_text(timeout=1500)).lower()
        except Exception:
            return False
        return any(text in body for text in AUTH_CHALLENGE_TEXT)


def parse_price_text(text: str) -> float | None:
    """Parse a Walmart price string into a float for existing result schema."""
    normalized = text.replace(",", " ").replace("\n", " ")
    match = re.search(r"\$?\s*(\d+(?:\s\d{3})*(?:\.\d{2})?)", normalized)
    if not match:
        return None
    value = match.group(1).replace(" ", "")
    try:
        return float(value)
    except ValueError:
        return None


async def first_visible(page: Any, selectors: list[str], *, timeout: int = 1000) -> Any | None:
    for selector in selectors:
        try:
            locator = page.locator(selector).first()
            if await page.locator(selector).count() and await locator.is_visible(timeout=timeout):
                return locator
        except Exception:
            continue
    return None


async def click_first(page: Any, selectors: list[str], *, required: bool = True) -> bool:
    locator = await first_visible(page, selectors)
    if locator is None:
        return not required
    await locator.click()
    return True


EMAIL_SELECTORS = [
    'input[type="email"]',
    'input[name="email"]',
    'input[autocomplete="email"]',
    'input[data-automation-id*="email" i]',
]
PASSWORD_SELECTORS = [
    'input[type="password"]',
    'input[name="password"]',
    'input[autocomplete="current-password"]',
]
CONTINUE_SELECTORS = [
    'button:has-text("Continue")',
    'button:has-text("Next")',
    'button[type="submit"]',
]
SIGN_IN_SELECTORS = [
    'button:has-text("Sign in")',
    'button:has-text("Sign In")',
    'button[type="submit"]',
]
PRICE_SELECTORS = [
    '[data-testid="price-wrap"] [itemprop="price"]',
    '[data-testid="price-wrap"]',
    '[data-automation-id="product-price"]',
    '[itemprop="price"]',
    'span[class*="price" i]',
]
QUANTITY_INPUT_SELECTORS = [
    'input[data-testid*="quantity" i]',
    'input[aria-label*="quantity" i]',
    'input[name*="quantity" i]',
]
QUANTITY_INCREMENT_SELECTORS = [
    'button[aria-label*="increase quantity" i]',
    'button[aria-label*="increment" i]',
    'button:has-text("+")',
]
ADD_TO_CART_SELECTORS = [
    'button[data-testid="add-to-cart-button"]',
    'button[data-automation-id="add-to-cart"]',
    'button[aria-label*="Add to cart" i]',
    'button:has-text("Add to cart")',
]
CART_LINK_SELECTORS = [
    'a[data-testid="cart-link"]',
    'a[href="/cart"]',
    'a[href*="/cart"]',
    'button[aria-label*="cart" i]',
]
CHECKOUT_SELECTORS = [
    'button[data-testid="checkout-button"]',
    'button[data-automation-id="checkout"]',
    'button:has-text("Continue to checkout")',
    'button:has-text("Checkout")',
]
ADDRESS_CONFIRM_SELECTORS = [
    'button:has-text("Use this address")',
    'button:has-text("Deliver to this address")',
    'button:has-text("Continue")',
]
PLACE_ORDER_SELECTORS = [
    'button[data-testid="place-order-button"]',
    'button[data-automation-id="place-order"]',
    'button:has-text("Place order")',
    'button:has-text("Place Order")',
]
