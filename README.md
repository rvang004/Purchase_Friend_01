# 🛒 Purchase Bot

A secure, automated e-commerce purchase scheduler. Set it once, run it forever.

**Features:**
- ✅ Support for multiple e-commerce sites (Amazon, eBay, etc.)
- ✅ Multiple accounts per site with individual spending limits
- ✅ Encrypted credential storage (AES encryption via cryptography)
- ✅ Flexible scheduling (once, daily, weekly)
- ✅ Dry-run mode for testing
- ✅ Windows Task Scheduler integration
- ✅ Full logging and error handling
- ✅ Payment method tracking (card, wallet, store credit)

---

## 📋 Quick Start

### 1. **Clone & Setup**

```bash
git clone https://github.com/yourusername/purchase-bot.git
cd purchase-bot

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 2. **Add Your Accounts**

```bash
python main.py setup
```

This launches an interactive wizard where you can:
- Add accounts (email, password, payment method, spending limit)
- Configure purchase tasks (URL, schedule, timing)
- View/delete existing accounts and tasks

**Example flow:**
```
1. Add new account
Account ID: amazon_main
Website: https://www.amazon.com
Email: your-email@example.com
Password: ••••••••••
Payment method: 1 (Credit Card)
Monthly limit: 500
✅ Account saved (encrypted)
```

### 3. **Test with Dry-Run**

Before running live purchases, test your setup:

```bash
python main.py run --dry-run
```

This will:
- Load your tasks
- Navigate to product pages
- Simulate clicks **without** completing purchases
- Show you logs of what would happen

### 4. **Run the Scheduler**

```bash
python main.py run
```

The scheduler checks every 60 seconds for tasks that should run. Press `Ctrl+C` to stop.

---

## 🔐 Security

### Credential Storage
- Passwords are encrypted using **Fernet** (symmetric encryption)
- Master key stored in `.master_key` (added to `.gitignore`)
- Never commit `.master_key` or `credentials.enc`
- All decryption happens in-memory

### Best Practices
1. **Use a strong master password** (if using master password layer)
2. **Keep `.master_key` safe** — never share it
3. **Don't commit `credentials.enc`** — it's in `.gitignore`
4. **Use unique passwords** for each site when possible
5. **Review logs regularly** in `purchase_bot.log`

---

## ⏰ Scheduling Options

### Once
Runs a single time at specified time:
```
Schedule type: once
Time: 14:30
→ Runs once at 2:30 PM today
```

### Daily
Runs every day at the same time:
```
Schedule type: daily
Time: 09:00
→ Runs at 9:00 AM every day
```

### Weekly
Runs on specific days of the week:
```
Schedule type: weekly
Time: 18:00
Days: Mon,Wed,Fri
→ Runs at 6:00 PM on Monday, Wednesday, Friday
```

---

## 💳 Payment Methods

Supported payment methods per account:
- Credit Card
- Debit Card
- Digital Wallet (PayPal, Apple Pay, Google Pay, etc.)
- Store Credit

Each account can have:
- Different payment method
- Monthly spending limit
- Individual tracking of monthly spend

**Example:**
```json
{
  "account_id": "amazon_main",
  "payment_method": "credit_card",
  "monthly_limit": 500.00,
  "spent_this_month": 125.50
}
```

---

## 📁 File Structure

```
purchase-bot/
├── main.py                 # Entry point (setup/run commands)
├── cli.py                  # Interactive setup wizard
├── scheduler.py            # Task scheduling & execution
├── purchase_engine.py      # Playwright automation
├── utils.py                # Encryption & utilities
├── requirements.txt        # Dependencies
├── .gitignore             # Git ignore (credentials, keys)
├── config.json            # Purchase tasks (git ignored)
├── credentials.enc        # Encrypted accounts (git ignored)
├── .master_key            # Encryption key (git ignored)
└── purchase_bot.log       # Activity logs
```

---

## 🪟 Windows Task Scheduler Setup

Run purchases automatically on startup or at specific times using Windows Task Scheduler.

### Step 1: Create a Batch File
Create `start_purchase_bot.bat`:

```batch
@echo off
cd C:\path\to\purchase-bot
venv\Scripts\activate
python main.py run
pause
```

Replace `C:\path\to\purchase-bot` with your actual path.

### Step 2: Open Task Scheduler
1. Press `Win + R`, type `taskschd.msc`, press Enter
2. Click **Create Basic Task**
3. Name: `Purchase Bot`
4. Description: `Automated e-commerce purchases`

### Step 3: Set Trigger
1. Click **Triggers**
2. Click **New...**
3. Choose:
   - **At startup** (runs when Windows boots)
   - OR **On a schedule** (Daily/Weekly at specific time)
4. Click **OK**

### Step 4: Set Action
1. Click **Actions**
2. Click **New...**
3. Action: **Start a program**
4. Program: `C:\path\to\purchase-bot\start_purchase_bot.bat`
5. Start in: `C:\path\to\purchase-bot`
6. Click **OK**

### Step 5: Set Conditions (Optional)
1. Click **Conditions**
2. Uncheck "Start the task only if the computer is on AC power" (if on laptop)
3. Check "Wake the computer to run this task"
4. Click **OK**

### Step 6: Enable & Test
1. Click **OK** to save
2. Right-click the task → **Run** to test immediately
3. Check `purchase_bot.log` for output

---

## 📊 Logs

All activity is logged to `purchase_bot.log`:

```
2025-01-15 14:30:22 - INFO - ⏰ Checking tasks at 14:30:22
2025-01-15 14:30:22 - INFO - 🎯 Found 1 task(s) to execute
2025-01-15 14:30:23 - INFO - 🚀 Starting purchase for task task_1 using account amazon_main
2025-01-15 14:30:45 - INFO - ✅ Login successful
2025-01-15 14:30:52 - INFO - ✅ Item added to cart
2025-01-15 14:31:10 - INFO - ✅ Purchase completed!
```

Check logs to:
- Verify purchases completed
- Troubleshoot failed purchases
- Track spending per account
- Audit all automated actions

---

## 🐛 Troubleshooting

### "Config file not found"
```bash
python main.py setup
# Add at least one account and purchase task
```

### "Account not found"
- Check `config.json` for correct account ID
- Verify account was added via `python main.py setup`

### "Login failed"
- Website layout may have changed
- Check if Playwright selectors need updating
- Run with `--dry-run` to see where it fails
- Check logs for details

### "Monthly limit reached"
- Spending limit for that account exceeded
- Adjust limit: `python main.py setup` → Edit account
- Reset monthly tracking manually in `config.json`

### Scheduler not running automatically
- Verify Windows Task Scheduler task is **Enabled**
- Check that `start_purchase_bot.bat` path is correct
- Test manually first: `python main.py run`
- Check Event Viewer for task errors

---

## 🚀 Advanced Usage

### Custom Site Handler
Modify `purchase_engine.py` to handle specific site layouts:

```python
async def login(self, site_url: str, email: str, password: str) -> bool:
    if "amazon.com" in site_url:
        # Amazon-specific login logic
        pass
    elif "ebay.com" in site_url:
        # eBay-specific logic
        pass
    # Fallback to generic
```

### Monitoring & Alerts
Add email/Slack alerts on purchase success/failure:

```python
if result["success"]:
    send_notification(f"✅ Purchase successful: {task['id']}")
else:
    send_notification(f"❌ Purchase failed: {result['error']}")
```

### Concurrent Purchases
Scheduler runs multiple tasks concurrently using `asyncio.gather()`:
```python
results = await asyncio.gather(*[
    self.execute_task(task, dry_run=dry_run)
    for task in tasks_to_run
])
```

---

## 📝 License

Personal use. Respect e-commerce site ToS.

---

## ⚠️ Important Notes

1. **Terms of Service**: Check if your e-commerce site allows automation. Most do for legitimate purchases.
2. **Rate Limiting**: The scheduler respects site responsiveness. Don't set intervals too aggressive.
3. **Browser Detection**: Some sites may detect headless browsers. Playwright has anti-detection features enabled.
4. **Authentication**: Keep passwords up-to-date. Failed logins halt purchases.
5. **Testing**: Always use `--dry-run` first before enabling real purchases.

---

## 🤝 Contributing

Found a bug? Want to add features?
- Check existing tasks and accounts structures
- Keep code DRY and modular
- Test with `--dry-run` before committing
- Add logging for new features

---

**Made with ❤️ for automation lovers**
