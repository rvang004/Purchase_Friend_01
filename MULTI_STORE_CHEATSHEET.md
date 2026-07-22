# Multi-Store Cheat Sheet (Do This!)

## 30-Second Setup

### Step 1: Add Walmart Account (Same As Before)
```
Account ID: walmart_main
Store URL: https://www.walmart.com
Email: your-walmart-email@example.com
Password: your-walmart-password
Account Type: [Auto-detect] ← Just leave blank
Click: Add Account
```
Done! Uses **Walmart adapter** (optimized)

### Step 2: Add Amazon Account (New!)
```
Account ID: amazon_main
Store URL: https://www.amazon.com
Email: your-amazon-email@example.com
Password: your-amazon-password
Account Type: [Auto-detect] ← Just leave blank
Click: Add Account
```
Done! Uses **Generic adapter** (works great with Amazon)

### Step 3: Add More Stores (Optional)
```
Same pattern for Target, Best Buy, eBay, etc.
Just change the URL and login
Account Type always: [Auto-detect]
```

### Step 4: Create Tasks
```
Account: walmart_main
Product: https://www.walmart.com/ip/12345
Schedule: Daily @ 9 AM
Click: Add Task

Account: amazon_main
Product: https://www.amazon.com/dp/B0123456/
Schedule: Weekly Mon,Fri @ 10 AM
Click: Add Task
```

Done! Bot runs each task with the right adapter!

---

## Real Quick Comparison

| Store | Account Type | What Happens |
|-------|--------------|--------------|
| Walmart | [Auto-detect] | Walmart adapter (optimized!) |
| Amazon | [Auto-detect] | Generic adapter (works great!) |
| Target | [Auto-detect] | Generic adapter (works great!) |
| eBay | [Auto-detect] | Generic adapter (works great!) |
| ANY store | [Auto-detect] | Generic adapter (works everywhere!) |

**Always pick [Auto-detect]** - it's perfect!

---

## My Setup

Copy this if you want the exact same thing:

```
Accounts:
1. walmart_main → Walmart (optimized)
2. amazon_main → Amazon (generic)
3. target_weekly → Target (generic)

Tasks:
1. Walmart groceries @ 9 AM daily (walmart_main)
2. Amazon books Mon/Wed/Fri @ 10 AM (amazon_main)
3. Target clothes Fri 7-9 PM window (target_weekly)

Result: 3 stores, auto-buy, scheduler handles all!
```

---

## What Changed in UI?

**Before:** "Walmart only"
**After:** "Any store works!"

That's it. Everything else same. Just more options now.

---

## One Thing to Know

Walmart gets **special optimized adapter**:
- Extra anti-bot tricks
- Better success rate
- Longer timeouts
- Walmart-specific selectors

Everything else gets **generic adapter**:
- Works with Amazon, Target, eBay, etc.
- Very reliable
- Slightly faster
- Same features as Walmart

**You don't pick** - it's automatic based on URL!

---

## Testing

```powershell
# Test before buying
python main.py run --dry-run --interval 30

# Watch browser
python main.py run --no-headless --mode review --interval 30

# Go live!
python main.py run --mode live --interval 60
```

---

## That's Literally It

1. Add account (any store)
2. Leave Account Type blank
3. Create task
4. Schedule it
5. Bot buys from any store!

Multi-store from day 1. No thinking required. Done!

---

## FAQ

**Q: Do I have to do anything different?**
A: Nope! Same UI, just works with more stores now.

**Q: Will Walmart still work?**
A: Better than ever! Auto-uses optimized adapter.

**Q: Can I use 5 different stores?**
A: Yes! Create 5 accounts, create tasks for each.

**Q: What if my store breaks?**
A: Use `--no-headless` mode to see what's happening.

**Q: Do I override the adapter?**
A: Almost never. [Auto-detect] is perfect.

---

## Supported Stores (Tested)

- Walmart (optimized adapter)
- Amazon (generic adapter)
- Target (generic adapter)
- Best Buy (generic adapter)
- eBay (generic adapter)
- Costco (generic adapter)
- Home Depot (generic adapter)
- And any other e-commerce store!

---

**TL;DR:** Works with ANY store now. Just use normally. [Auto-detect] everything. Done!

See MULTI_STORE_GUIDE.md for full details if needed.
