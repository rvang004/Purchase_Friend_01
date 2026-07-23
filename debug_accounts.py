#!/usr/bin/env python3
"""Debug script to check which accounts exist."""

import json
from utils import CredentialManager
from app_paths import CREDENTIALS_FILE

cred_mgr = CredentialManager()
accounts = cred_mgr.load_credentials()

print("=" * 60)
print("CURRENT ACCOUNTS IN DATABASE")
print("=" * 60)

if not accounts:
    print("\n  [NO ACCOUNTS FOUND]\n")
else:
    for account_id, account_data in accounts.items():
        print(f"\nAccount ID: '{account_id}'")
        print(f"  Site: {account_data.get('site')}")
        print(f"  Email: {account_data.get('email')}")
        print(f"  Payment Method: {account_data.get('payment_method')}")
        print(f"  Monthly Limit: ${account_data.get('monthly_limit')}")

print("\n" + "=" * 60)
print(f"Total accounts: {len(accounts)}")
print("=" * 60)

# Also check config for tasks
try:
    from pathlib import Path
    from app_paths import CONFIG_FILE
    if CONFIG_FILE.exists():
        config = json.loads(CONFIG_FILE.read_text())
        print(f"\nTasks in config: {len(config.get('tasks', []))}")
        for task in config.get('tasks', []):
            print(f"  - Task '{task.get('id')}' uses account: '{task.get('account_id')}'")
except Exception as e:
    print(f"\nCouldn't load config: {e}")
