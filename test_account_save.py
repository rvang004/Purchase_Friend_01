#!/usr/bin/env python3
"""Quick test to verify accounts can be saved and loaded."""

from utils import CredentialManager
from app_paths import CREDENTIALS_FILE

cred_mgr = CredentialManager()

# Test 1: Add an account
print("[TEST 1] Adding test account...")
accounts = {}
accounts = cred_mgr.add_account(
    accounts,
    account_id="test_walmart",
    site="https://www.walmart.com",
    email="test@example.com",
    password="testpass123",
    payment_method="credit_card",
    monthly_limit=1000.0,
    price_limit_per_item=500.0,
)
print(f"  Accounts dict: {list(accounts.keys())}")

# Test 2: Save to disk
print("[TEST 2] Saving to disk...")
success = cred_mgr.save_credentials(accounts)
print(f"  Save success: {success}")
print(f"  File exists: {CREDENTIALS_FILE.exists()}")
print(f"  File size: {CREDENTIALS_FILE.stat().st_size if CREDENTIALS_FILE.exists() else 'N/A'} bytes")

# Test 3: Load from disk
print("[TEST 3] Loading from disk...")
loaded = cred_mgr.load_credentials()
print(f"  Loaded accounts: {list(loaded.keys())}")
print(f"  Account found: {'test_walmart' in loaded}")

if "test_walmart" in loaded:
    acc = loaded["test_walmart"]
    print(f"  Email: {acc.get('email')}")
    print(f"  Site: {acc.get('site')}")
    print(f"  Monthly limit: ${acc.get('monthly_limit')}")
    print("\n[SUCCESS] Account save/load cycle works!")
else:
    print("\n[ERROR] Account not found after load!")
