r"""Playwright E2E tests against a deterministic local fake store.

Run explicitly with:
    set RUN_PLAYWRIGHT_E2E=1 && .venv\Scripts\python -m unittest tests.test_fake_store_e2e -v
"""

from __future__ import annotations

import asyncio
import os
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from purchase_artifacts import PurchaseArtifacts
from purchase_engine import PurchaseEngine


HTML = {
    "/login": """
        <html><body data-page="login">
          <h1>Fake Store Login</h1>
          <input data-testid="email" type="email" />
          <input data-testid="password" type="password" />
          <button data-testid="login-submit" onclick="location.href='/logged-in'">Sign in</button>
        </body></html>
    """,
    "/logged-in": """
        <html><body data-page="logged-in">
          <h1>Signed in</h1>
          <a href="/product/sku-1">Go to product</a>
        </body></html>
    """,
    "/product/sku-1": """
        <html><body data-testid="product-page">
          <h1>Fake Widget</h1>
          <div data-testid="price">$19.99</div>
          <input data-testid="quantity" type="number" value="1" min="1" />
          <button data-testid="add-to-cart" onclick="location.href='/cart'">Add to Cart</button>
        </body></html>
    """,
    "/cart": """
        <html><body data-testid="cart-page">
          <h1>Your Cart</h1>
          <button data-testid="checkout" onclick="location.href='/checkout'">Checkout</button>
        </body></html>
    """,
    "/checkout": """
        <html><body data-testid="checkout-page">
          <h1>Checkout</h1>
          <button data-testid="use-address">Use this address</button>
          <button data-testid="place-order" onclick="location.href='/confirmation'">Place Order</button>
        </body></html>
    """,
    "/confirmation": """
        <html><body data-testid="confirmation-page">
          <h1>Order Confirmed</h1>
          <div data-testid="order-id">ORDER-123</div>
        </body></html>
    """,
}


class FakeStoreHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = HTML.get(self.path.split("?")[0])
        if body is None:
            self.send_response(404)
            self.end_headers()
            return
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        # Keep test output clean. The fake store does not need a tiny megaphone.
        return


@unittest.skipUnless(os.getenv("RUN_PLAYWRIGHT_E2E") == "1", "set RUN_PLAYWRIGHT_E2E=1 to run Playwright E2E")
class FakeStoreE2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeStoreHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=5)

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_review_mode_stops_before_confirmation(self):
        result = asyncio.run(self._run_engine("review"))

        self.assertTrue(result["success"])
        self.assertEqual(result["adapter"], "fake_store")
        self.assertTrue(result["review_required"])
        self.assertEqual(result["item_price"], 19.99)
        self.assertIn("/checkout", result["final_url"])
        self.assertNotIn("/confirmation", result["final_url"])
        self.assertGreaterEqual(len(result["screenshots"]), 5)
        self.assertTrue(Path(result["trace_path"]).exists())

    def test_live_mode_reaches_confirmation(self):
        result = asyncio.run(self._run_engine("live"))

        self.assertTrue(result["success"])
        self.assertFalse(result["review_required"])
        self.assertIn("/confirmation", result["final_url"])
        self.assertTrue(Path(result["trace_path"]).exists())

    async def _run_engine(self, mode: str) -> dict:
        engine = PurchaseEngine(
            headless=True,
            mode=mode,
            artifacts=PurchaseArtifacts(base_dir=self.tmp_dir.name, run_id=f"fake_{mode}"),
        )
        account = {
            "id": "fake_account",
            "adapter": "fake_store",
            "site": f"{self.base_url}/login",
            "email": "roger@example.test",
            "password": "secret",
            "price_limit_enabled": True,
            "price_limit_per_item": 50,
        }
        result = {"trace_path": None}
        try:
            await engine.initialize()
            result = await engine.execute_purchase(
                account,
                f"{self.base_url}/product/sku-1",
                quantity=2,
            )
        finally:
            await engine.close()
            result["trace_path"] = engine.trace_path

        if result.get("trace_path"):
            self.assertTrue(Path(result["trace_path"]).exists())
        return result


if __name__ == "__main__":
    unittest.main()
