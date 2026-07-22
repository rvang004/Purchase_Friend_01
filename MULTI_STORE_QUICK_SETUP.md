# Multi-Store Quick Setup

## TL;DR

Purchase Bot works with **ANY online store**. Just use it like normal - it auto-detects which adapter to use!

---

## Quick Examples

### Walmart
```
Account ID: walmart_main
Store URL: https://www.walmart.com
Email: your-email@walmart.com
Password: your-password
Account Type: [Auto-detect] ← Automatically uses Walmart adapter
```

### Amazon
```
Account ID: amazon_main
Store URL: https://www.amazon.com
Email: your-email@amazon.com
Password: your-password
Account Type: [Auto-detect] ← Automatically uses Generic adapter
```

### Target
```
Account ID: target_main
Store URL: https://www.target.com
Email: your-email@target.com
Password: your-password
Account Type: [Auto-detect] ← Automatically uses Generic adapter
```

### Any Store
```
Account ID: my_store
Store URL: https://www.any-store.com
Email: user@example.com
Password: password
Account Type: [Auto-detect] ← Automatically uses Generic adapter
```

---

## How It Works

**Walmart URLs:**
```
walmart.com or walmart.ca
↓
Auto-uses Walmart adapter (optimized with anti-bot protection)
```

**Any Other URL:**
```
amazon.com, target.com, bestbuy.com, ebay.com, etc.
↓
Auto-uses Generic adapter (works everywhere)
```

**Create tasks the same way:**
```
Account: amazon_main
Product URL: https://www.amazon.com/dp/B0ABCD1234/
Schedule: Daily at 9 AM
→ Bot buys from Amazon daily at 9 AM
```

---

## Account Type Options

| Option | Use Case |
|--------|----------|
| Auto-detect (default) | Perfect for everything. Let it choose! |
| Walmart | Force Walmart adapter even if not Walmart URL |
| Generic | Force Generic adapter for any store |

**Just leave as "Auto-detect" and it works perfectly.**

---

## Supported Stores

Works with ANY of these (and many more):
- Amazon
- Walmart
- Target
- Best Buy
- eBay
- Costco
- Home Depot
- Lowe's
- GameStop
- Zappos
- Your-Custom-Store.com
- Literally any e-commerce site with login + checkout

---

## Multi-Store Setup Example

```
Accounts Tab:
─────────────────────────────────────────────
1. walmart_main
   Walmart (optimized) | Price cap ON | $1000/mo limit

2. amazon_main  
   Generic | Price cap ON | $500/mo limit

3. target_weekly
   Generic | Price cap ON | $200/mo limit

4. bestbuy_gaming
   Generic | Price cap ON | $1000/mo limit
```

Create tasks for each:
```
Tasks Tab:
─────────────────────────────────────────────
Task 1: Walmart Groceries (account: walmart_main)
        Schedule: Daily @ 9 AM
        Product: https://www.walmart.com/ip/12345

Task 2: Amazon Books (account: amazon_main)
        Schedule: Weekly Mon,Thu @ 10 AM
        Product: https://www.amazon.com/dp/B123456789

Task 3: Target Clothing (account: target_weekly)
        Schedule: Friday 5-7 PM window
        Product: https://www.target.com/p/-/A-001234567

Task 4: Best Buy GPU (account: bestbuy_gaming)
        Schedule: Daily 10-11 AM window
        Product: https://www.bestbuy.com/site/123456789
```

Bot automatically runs purchases on schedule, using the right adapter for each store!

---

## Key Points

1. **Auto-detect is your friend** - Just leave Account Type blank
2. **Walmart gets special treatment** - Walmart adapter auto-activates for walmart.com URLs
3. **Everything else works** - Generic adapter handles Amazon, Target, eBay, etc.
4. **Create separate accounts** - One per store you want to buy from
5. **Adapter is per-task** - Based on product URL, not account
6. **All anti-bot features work** - Use `--no-headless`, `--proxy`, `--mode review` for all stores

---

## What's Different?

**Walmart:**
- Walmart adapter (extra optimizations, anti-bot detection)
- Longer timeouts (Walmart is slow)
- Special selectors for Walmart HTML
- Optimized for Walmart's bot detection

**Everything Else:**
- Generic adapter (works with any store)
- Standard timeouts
- Generic e-commerce selectors
- Works great!

**Both get:**
- Scheduling (exact time, windows, weekly, etc.)
- Price limits
- Quantity limits
- Spending limits
- Proxy support
- Headless/visible browser options

---

## Testing Your Multi-Store Setup

1. **Add accounts** for each store
2. **Add tasks** for each account
3. **Use dry-run mode** to test without buying:
   ```
   python main.py run --dry-run --interval 30
   ```
4. **Watch logs** to see tasks running
5. **Try review mode** to see browser:
   ```
   python main.py run --no-headless --mode review --interval 30
   ```
6. **Go live** when confident:
   ```
   python main.py run --mode live --interval 60
   ```

---

## Common Setup

**Home Setup (3 stores):**
```
- walmart_groceries (daily 9 AM)
- amazon_books (weekly)
- target_clothes (window 7-9 PM)
```

**Business Setup (2 stores):**
```
- walmart_supplies (daily 8 AM)
- amazon_business (weekly 9 AM)
```

**Gamer Setup (2 stores):**
```
- bestbuy_gpu (daily 10-11 AM window, high price limit)
- gamestop_games (weekly 9 AM)
```

---

## That's It!

1. Add account with store login
2. Leave Account Type as "Auto-detect"
3. Add tasks with product URLs
4. Let bot run on schedule

Bot automatically picks Walmart adapter for Walmart, Generic for everything else. Done!

Read MULTI_STORE_GUIDE.md for full details and troubleshooting.
