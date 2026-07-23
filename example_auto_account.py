#!/usr/bin/env python3
"""
Example: How to use auto-account-creation with tasks.

When you add a task with 'account_config', the scheduler will automatically
create the account if it doesn't exist yet.
"""

import json
from pathlib import Path
from app_paths import CONFIG_FILE

# Example task with embedded account config
example_config = {
    "tasks": [
        {
            "id": "task_roger_vang_walmart",
            "account_id": "roger_vang",
            "product_url": "https://www.walmart.com/ip/123456789",
            "schedule_type": "daily",
            "run_time": "09:00",
            "quantity": 1,
            "enabled": True,
            "created": "2026-07-23T00:00:00",
            "last_run": None,
            
            # NEW: Embed account details so scheduler can auto-create it if missing
            "account_config": {
                "site": "https://www.walmart.com",
                "email": "roger@example.com",
                "password": "your_password_here",
                "payment_method": "credit_card",
                "monthly_limit": 1000,
                "price_limit_per_item": 500,
                "price_limit_enabled": True,
                "quantity_limit_per_item": None,
                "shipping_address": None
            }
        }
    ]
}

print("=" * 70)
print("EXAMPLE: Task with Auto-Account Creation")
print("=" * 70)
print("\nWhen you run the scheduler with this task:")
print("1. Scheduler loads the task")
print("2. Looks for account 'roger_vang'")
print("3. Account doesn't exist (first run)")
print("4. Scheduler sees 'account_config' field in task")
print("5. Auto-creates account 'roger_vang' with those details")
print("6. Saves account to credentials.enc")
print("7. Proceeds with the purchase")
print("\nOn subsequent runs, the account exists, so it just uses it.")
print("\n" + "=" * 70)
print("Example JSON (save this to config.json):")
print("=" * 70)
print(json.dumps(example_config, indent=2))
print("\n" + "=" * 70)
print("TO USE THIS FEATURE:")
print("=" * 70)
print("\n1. OPTION A: Via CLI (edit config.json directly)")
print("   - Copy the 'account_config' section from a task")
print("   - Paste it into your task in config.json")
print("   - Update email/password with REAL credentials")
print("   - Run: python main.py run")
print("\n2. OPTION B: Via Web UI (coming soon)")
print("   - UI will have 'Advanced' section to add account_config")
print("\n" + "=" * 70)
