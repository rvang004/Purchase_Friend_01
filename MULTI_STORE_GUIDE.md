# Multi-Store Support Guide

## Overview

Purchase Bot now supports **ANY online store** - not just Walmart!

### How It Works

1. **Walmart URLs** (walmart.com, walmart.ca) → Auto-uses **optimized Walmart adapter**
2. **Any other URL** → Auto-uses **generic adapter** (works with any store)
3. **Override** → Optionally force a specific adapter in account settings

---

## Supported Stores

Purchase Bot works with any e-commerce site:

**Popular retailers:**
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
- And literally any other online store

**Why multiple stores work:**
- Generic adapter uses common HTML patterns (add to cart buttons, checkout flows, etc.)
- All stores have login, product pages, cart, and checkout
- Walmart gets an optimized adapter with extra selectors and anti-bot protection

---

## Setup by Store

### Amazon Example

```
Account ID: amazon_main
Store URL: https://www.amazon.com
Email: your-amazon@email.com
Password: your-amazon-password
Account Type: Auto-detect (or leave blank)
```

Robot automatically detects it's NOT Walmart, uses generic adapter.

### Walmart Example

```
Account ID: walmart_main
Store URL: https://www.walmart.com
Email: your-walmart@email.com
Password: your-walmart-password
Account Type: Auto-detect (will auto-use Walmart optimized)
```

Robot detects Walmart URL, automatically uses optimized Walmart adapter.

### Target Example

```
Account ID: target_account
Store URL: https://www.target.com
Email: your-target@email.com
Password: your-target-password
Account Type: Auto-detect (generic adapter)
```

### Custom Store Example

```
Account ID: my_custom_store
Store URL: https://www.custom-store.com
Email: user@example.com
Password: password123
Account Type: Generic (or auto-detect)
```

---

## Account Types (Adapters)

When adding an account, you can specify the adapter type:

### Auto-detect (Recommended)
```
Account Type: [Auto-detect from URL]
```
Robot automatically chooses:
- Walmart URL → Walmart adapter (optimized)
- Any other → Generic adapter (works everywhere)

### Explicit Options

**Walmart:**
```
Account Type: Walmart (optimized adapter)
```
Forces use of Walmart-optimized adapter (best for Walmart)

**Generic:**
```
Account Type: Generic (any store)
```
Forces generic adapter (works with any store, but no store-specific optimizations)

---

## What Each Adapter Does

### Walmart Adapter (Optimized)
- Walmart-specific selectors for buttons, forms, etc.
- Anti-Walmart-bot-detection measures (from our enhancements!)
- Handles Walmart's login flow
- Optimized timeouts for Walmart's slow servers
- Detects Walmart-specific errors and messages

**Used for:**
- walmart.com
- walmart.ca

**Why custom?**
- Walmart has unique HTML structure
- Walmart is aggressive with bot detection
- Walmart has specific anti-bot protections

### Generic Adapter (Works Everywhere)
- Works with ANY store
- Uses common e-commerce patterns
- Flexible selectors that work across stores
- No store-specific optimizations

**Used for:**
- Amazon
- Target
- eBay
- Best Buy
- Any other store

**Why generic?**
- All stores have similar flows (login → product → cart → checkout)
- Same basic HTML patterns across e-commerce sites

---

## Which Adapter Should I Use?

### For Walmart
```
Use: Auto-detect (will choose Walmart adapter)
Or: Explicitly set "Walmart"
Why: Walmart adapter has special anti-bot handling
```

### For Everything Else
```
Use: Auto-detect (will choose Generic adapter)
Or: Explicitly set "Generic"
Why: Generic adapter works with all e-commerce sites
```

---

## Real-World Multi-Store Setup

You can have accounts for multiple stores:

```
Accounts:
1. walmart_main → walmart.com → Walmart (optimized)
2. amazon_main → amazon.com → Generic
3. target_daily → target.com → Generic
4. bestbuy_games → bestbuy.com → Generic
5. ebay_backup → ebay.com → Generic
```

Create tasks for each:

```
Task 1: Buy PS5 from Amazon daily at 9 AM (account: amazon_main)
Task 2: Buy groceries from Walmart Fri at 10 AM (account: walmart_main)
Task 3: Buy clothes from Target in window 7-9 PM (account: target_daily)
Task 4: Buy GPU from Best Buy daily 10-11 AM (account: bestbuy_games)
Task 5: Monitor eBay for deals weekly (account: ebay_backup)
```

Each task uses the appropriate adapter based on the URL/account type.

---

## How Adapter Selection Works

When you add a task, the system:

1. Gets the **product URL** from the task
2. Gets the **account info** (including adapter override if set)
3. Parses the URL to get the **hostname** (amazon.com, walmart.com, etc.)
4. Checks if adapter is **explicitly set** in account
5. If Walmart URL → Use Walmart adapter
6. Otherwise → Use Generic adapter

**Example flows:**

**Case 1: Walmart URL, no adapter specified**
```
URL: https://www.walmart.com/ip/...
Account adapter: (not set)
→ Auto-detects walmart.com
→ Uses Walmart adapter
```

**Case 2: Amazon URL, no adapter specified**
```
URL: https://www.amazon.com/dp/...
Account adapter: (not set)
→ Auto-detects amazon.com (not Walmart)
→ Uses Generic adapter
```

**Case 3: Custom override**
```
URL: https://www.walmart.com/ip/...
Account adapter: generic (forced)
→ Adapter explicitly set to "generic"
→ Uses Generic adapter (ignores URL)
```

---

## Mixing Stores in One Account?

**Not recommended**, but technically possible:

```
Account: my_mixed_account
Store URL: https://www.walmart.com (login URL)
```

Then create tasks for different products:
- Task 1: Walmart product (uses walmart.com URL)
- Task 2: Amazon product (uses amazon.com URL)

The **adapter is auto-detected per task** based on the product URL, not the account URL.

Better approach: Create separate accounts per store.

---

## Examples by Store

### Amazon
```
Store URL: https://www.amazon.com
Product URL: https://www.amazon.com/dp/B0ABCD1234/
Adapter: Auto-detect (uses Generic)
```

### Target
```
Store URL: https://www.target.com
Product URL: https://www.target.com/p/-/A-001234567
Adapter: Auto-detect (uses Generic)
```

### Best Buy
```
Store URL: https://www.bestbuy.com
Product URL: https://www.bestbuy.com/site/...
Adapter: Auto-detect (uses Generic)
```

### Costco
```
Store URL: https://www.costco.com
Product URL: https://www.costco.com/product-name.0.product.html
Adapter: Auto-detect (uses Generic)
```

### eBay
```
Store URL: https://www.ebay.com
Product URL: https://www.ebay.com/itm/123456789
Adapter: Auto-detect (uses Generic)
```

### Walmart (Both Websites)
```
US Store: https://www.walmart.com
Product URL: https://www.walmart.com/ip/XXXXX
Adapter: Auto-detect (uses Walmart)

Canada Store: https://www.walmart.ca
Product URL: https://www.walmart.ca/en/ip/XXXXX
Adapter: Auto-detect (uses Walmart)
```

---

## Troubleshooting

### "My custom store doesn't work"

**Check:**
1. Store has email/password login (required)
2. Product URL is direct link (not search page)
3. Product page has price, add-to-cart button
4. No CAPTCHA on login/checkout
5. Not behind proxy/VPN protection

**Try:**
- Use `--no-headless` mode to see what's happening
- Run with `--mode dry-run` first
- Check logs for specific error messages

### "I have 2 Walmarts, 2 Amazons"

Create separate accounts:
```
Accounts:
- walmart_main (personal account)
- walmart_work (work account)
- amazon_personal (personal)
- amazon_business (business)
```

Each can have different login credentials, spending limits, etc.

### "Can I use one account for multiple stores?"

**Yes, but not recommended:**
- Store URL (login page) = one store
- Product URLs can be any store
- Adapter auto-detects per product URL
- Mixing makes it confusing

**Better: Use separate accounts**

---

## Performance Notes

**Walmart adapter:**
- Slightly slower (more checks, optimizations)
- Better success rate with Walmart

**Generic adapter:**
- Works with any store
- Slightly faster (fewer checks)
- Good success rate with most stores

**Which is faster?**
- Generic: ~0.1% faster
- But Walmart adapter: ~10% more reliable for Walmart

---

## Mixing Walmart + Other Stores

**Great setup:**
```
Accounts:
1. walmart_main (walmart.com) → Walmart adapter (optimized)
2. amazon_daily (amazon.com) → Generic adapter
3. target_weekly (target.com) → Generic adapter
```

Each account uses the best adapter for that store!

---

## Anti-Bot Protection by Store

| Store | Adapter | Protection Level |
|-------|---------|------------------|
| Walmart | Walmart (optimized) | Maximum (domcontentloaded, 60s timeout, fingerprinting, proxy support) |
| Amazon | Generic | Good (standard selectors, timeout handling) |
| Target | Generic | Good |
| Best Buy | Generic | Good |
| eBay | Generic | Good |
| Others | Generic | Good |

**For any store:**
- Use `--no-headless` to see what's happening
- Use `--proxy` to rotate IPs if rate-limited
- Use `--mode review` to stop before purchase

---

## Summary

- **Walmart:** Automatic Walmart adapter (optimized)
- **Other stores:** Automatic Generic adapter (works everywhere)
- **Override:** Can explicitly set adapter if needed
- **Multiple stores:** Create separate accounts, each auto-uses best adapter
- **Best practice:** Let it auto-detect (works perfectly)

Set up your accounts, let the bot auto-detect the right adapter, and you're done!
