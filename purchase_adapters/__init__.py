"""Site adapter selection for purchase automation."""

from .base import StoreAdapter
from .fake_store import FakeStoreAdapter
from .generic import GenericStoreAdapter
from .selector import select_adapter
from .walmart import WalmartStoreAdapter

__all__ = [
    "FakeStoreAdapter",
    "GenericStoreAdapter",
    "StoreAdapter",
    "WalmartStoreAdapter",
    "select_adapter",
]
