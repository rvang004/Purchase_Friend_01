"""Adapter selection helpers."""

from __future__ import annotations

import urllib.parse
from typing import Any

from .base import StoreAdapter
from .fake_store import FakeStoreAdapter
from .generic import GenericStoreAdapter


FAKE_STORE_HOSTS = {"127.0.0.1", "localhost"}


def select_adapter(account: dict[str, Any], product_url: str) -> StoreAdapter:
    """Select a site adapter from account metadata and URL.

    Real production adapters should be explicit via account["adapter"]. The
    localhost shortcut exists for deterministic fake-store E2E tests only.
    """
    adapter_name = str(account.get("adapter", "")).strip().lower()
    if adapter_name == "fake_store":
        return FakeStoreAdapter()

    parsed = urllib.parse.urlparse(product_url)
    if parsed.hostname in FAKE_STORE_HOSTS:
        return FakeStoreAdapter()

    return GenericStoreAdapter()
