"""Site adapter selection for purchase automation."""

from .base import StoreAdapter
from .fake_store import FakeStoreAdapter
from .generic import GenericStoreAdapter
from .selector import select_adapter

__all__ = [
    "FakeStoreAdapter",
    "GenericStoreAdapter",
    "StoreAdapter",
    "select_adapter",
]
