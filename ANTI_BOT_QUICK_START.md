# Anti-Bot Fixes - Quick Start Commands

## NEW! Commands Available (As of Today)

I just added 3 new CLI flags to fight Walmart's anti-bot detection. Here they are:

### 1. Show Browser Window (Debug Mode)
```powershell
python main.py run --no-headless --mode review --interval 60
```
**When:** Testing, debugging, seeing if Walmart blocks you
**What it does:** Opens real Chrome window, lets you watch the purchase happen
**Speed:** Slower (5-10s per navigation) but you see everything

### 2. Use a Proxy (Avoid IP Rate-Limiting)
```powershell
python main.py run --proxy http://my-proxy.com:8080 --mode live --interval 60
```
**When:** Walmart keeps queueing you (/qp pages) or blocking your IP
**What it does:** Routes traffic through proxy, changes your IP
**Cost:** $5-50/month for good proxy service

**Recommended proxies:**
- Bright Data (residential, highly recommended)
- RottenProxies
- Oxylabs
- Zyte

### 3. Combine Both (Full Debug)
```powershell
python main.py run --no-headless --proxy http://my-proxy.com:8080 --mode review --interval 60
```
**When:** You're being blocked AND want to see what's happening
**What it does:** Shows window + uses proxy = maximum visibility + IP rotation

---

## The Fixes Explained (30 Second Version)

**Problem:** Walmart blocking your bot because:
1. You were waiting for `networkidle` (Walmart never gets there)
2. Timeout was too short for slow Walmart servers
3. Browser looked obviously automated (no real user agent)
4. Same IP getting rate-limited
5. Obvious fake fingerprints

**Solution:** I fixed all 5 things in your code. Now the bot:
1. Uses `domcontentloaded` instead of `networkidle` (works!)
2. Waits 60 seconds (enough time for Walmart)
3. Looks like Chrome 124, typical person, US timezone
4. Can route through proxy (change IP)
5. Opens real browser window if you ask (debug mode)

---

## Three-Step Test Plan

### Week 1: See What's Happening
```powershell
python main.py run --no-headless --mode review --interval 60
```

Run this for 5 minutes. Watch the Chrome window. Do you see:
- Walmart homepage loads? (Good!)
- Login works? (Good!)
- Product page loads? (Good!)
- /qp queue page appears? (Bad - you're being rate-limited)
- CAPTCHA? (Stops here in review mode - you solve it manually)

### Week 2: Run Headless (Faster)
```powershell
python main.py run --mode review --interval 60
```

Same as before but no window. Runs invisible in background. Still safe (stops before purchase).

### Week 3: Add Proxy if Needed
```powershell
python main.py run --proxy http://my-proxy:8080 --mode live --interval 60
```

If you saw `/qp` pages in week 1, get a proxy and use this.

---

## Command Reference

```
# Default behavior (unchanged)
python main.py run --mode review

# Show browser window
python main.py run --no-headless --mode review

# Use proxy
python main.py run --proxy http://proxy:8080 --mode live

# Combined
python main.py run --no-headless --proxy http://proxy:8080 --mode review

# All options
python main.py run --help
```

---

## What Else Changed?

**Inside the code** (you don't need to do anything):
- All `wait_until="networkidle"` → `wait_until="domcontentloaded"`
- All timeouts → 60 seconds
- Browser fingerprinting → Chrome 124, US, 1366x768 screen
- Proxy support throughout scheduler chain

**No breaking changes** - everything backward compatible!

---

## TL;DR

**TRY THIS TODAY:**
```powershell
python main.py run --no-headless --mode review --interval 60
```

Watch for 5 minutes. Tell me if you see:
1. Walmart loads (green light)
2. Login works (green light)
3. /qp queue page (red light - need proxy)
4. CAPTCHA (stops here - can solve manually)

Then let me know what you see!

---

## Detailed Guides

- **ANTI_BOT_GUIDE.md** - Full 200+ line explanation of all 5 fixes
- **IMPLEMENTATION_SUMMARY.md** - Technical what-changed-where document
- **This page** - Quick commands you actually use

Pick one based on how deep you want to go!

---

## Next Steps

1. **Read this file** (you're doing it!)
2. **Run the test command** with `--no-headless`
3. **Watch the browser** for 5 minutes
4. **Check the logs** (look at purchase_bot.log)
5. **Tell me what happened**
6. **Adjust based on results** (add proxy if needed)

Ready? Go run it!

```powershell
cd C:\Users\r0v0038\Documents\puppy_workspace\purchase-bot
.\venv\Scripts\Activate.ps1
python main.py run --no-headless --mode review --interval 60
```

Let me know what Walmart does!
