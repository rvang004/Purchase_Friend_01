# Walmart Anti-Bot Detection Bypass Guide

This guide explains the **5 critical anti-bot evasion tactics** now built into your purchase-bot!

## What Changed?

Your bot was getting blocked by Walmart because:
- **`networkidle` waits forever** — Walmart continuously loads background scripts, so `networkidle` never completes
- **Default 30s timeout is too short** — Walmart is slow; pages need 60+ seconds
- **Headless browser is detectable** — Walmart looks for Chrome/Chromium without a real display
- **Rate limiting via IP** — Same IP hammering Walmart gets flagged
- **Obvious automation signs** — No user agent, no realistic viewport, no natural delays

---

## The 5 Fixes

### 1. Swap `networkidle` → `domcontentloaded` (CRITICAL)

**Problem:** Your old code waited for `networkidle`, which never happens on Walmart.

**Solution:** All navigation now uses `wait_until="domcontentloaded"` instead. DOM content loads quickly (1-3s), and we don't wait for background scripts.

**Files Modified:**
- `purchase_adapters/walmart.py` - All `page.goto()` calls
- `purchase_actions.py` - All `page.goto()` calls
- Where: Login, product page, cart, checkout

**Before:**
```python
await page.goto("https://www.walmart.com", wait_until="networkidle")  # HANGS!
```

**After:**
```python
await page.goto("https://www.walmart.com", wait_until="domcontentloaded", timeout=60000)  # Works!
```

---

### 2. Increase Timeout to 60 Seconds

**Problem:** Walmart's servers are slow. Default 30s timeout = instant failure.

**Solution:** All navigation now has `timeout=60000` (60 seconds). If the page doesn't respond in 60s, we gracefully skip it instead of hanging forever.

**Files Modified:**
- `purchase_adapters/walmart.py`
- `purchase_actions.py`

**Example:**
```python
await page.goto(url, wait_until="domcontentloaded", timeout=60000)
```

---

### 3. Use Non-Headless Browser (Show the Window!)

**Problem:** Walmart detects headless browsers via missing GPU, unusual process listing, etc.

**Solution:** You can now run with `--no-headless` to open a **real browser window** that Walmart can't easily detect as automated.

**Usage:**

```powershell
# See the browser window while testing
python main.py run --no-headless --mode review --interval 60

# Or in scheduler:
python main.py run --no-headless --interval 60
```

**How It Works:**
- Default: `--headless` (fast, runs in background)
- Debug: `--no-headless` (slow, shows Chrome window, good for troubleshooting)
- Walmart sees a real browser → harder to block

---

### 4. Rotate IP / Avoid Rate Limiting

**Problem:** If you keep hitting Walmart from the same IP, it rate-limits you (`/qp` queue page).

**Solution:** Use `--proxy` to route through a proxy with a different IP.

**Usage:**

```powershell
# With a proxy (e.g., http://my-proxy.com:8080)
python main.py run --proxy http://my-proxy.com:8080 --interval 60

# If you don't have a proxy, skip this for now
python main.py run --interval 60
```

**Proxy Format:**
```
--proxy http://user:pass@proxy.com:8080
--proxy http://proxy.com:3128
--proxy socks5://proxy.com:1080
```

**Note:** Proxy is optional. If Walmart still queues you after 5 minutes, get a proxy service (RottenProxies, Bright Data, etc.).

---

### 5. Realistic Browser Fingerprinting

**Problem:** Walmart checks for:
- Missing user agent
- Weird viewport (too small or too large)
- Mismatched timezone
- No JavaScript support (obviously)

**Solution:** Browser now launches with:
- **Realistic user agent:** Chrome 124 on Windows 10
- **Standard viewport:** 1366×768 (typical laptop screen)
- **US timezone:** America/Chicago (helpful for matching Walmart region)
- **Locale:** en-US

**Files Modified:**
- `purchase_engine.py` - Browser context initialization

**Code:**
```python
context_args = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "viewport": {"width": 1366, "height": 768},
    "locale": "en-US",
    "timezone_id": "America/Chicago",
}
```

---

## How to Use

### Quick Start (Review Mode)

```powershell
# 1. Start the scheduler in REVIEW mode (stops before final purchase)
cd C:\Users\r0v0038\Documents\puppy_workspace\purchase-bot
.\venv\Scripts\Activate.ps1
python main.py run --mode review --interval 60

# 2. It will run purchases UP TO the final "Place Order" button
# 3. Check the screenshots in artifacts/ to verify everything worked
# 4. If it looks good, switch to --mode live
```

### Debug Mode (Non-Headless)

```powershell
# See what Walmart is doing in real-time
python main.py run --no-headless --mode review --interval 60

# Watch the browser window:
# - See if Walmart is loading
# - See if login works
# - See if buttons are clickable
# - Catch anti-bot pages (/qp, CAPTCHA, etc.)
```

### Production Mode (Headless + Proxy)

```powershell
# If you have a proxy and want fully automated purchasing:
python main.py run --proxy http://my-proxy.com:8080 --mode live --interval 60

# Without proxy (if you're not being rate-limited):
python main.py run --mode live --interval 60
```

---

## Troubleshooting

### "Page timeout after 60s"
- Walmart is slow or blocking your IP
- **Solution:** Increase timeout further (edit code) or add `--proxy`

### "Stuck on /qp (queue page)"
- IP is rate-limited
- **Solution:** Use `--proxy` to change IP

### "Login fails"
- Session might be expired
- **Solution:** Run with `--no-headless` to debug, manually log in, keep session

### "Add to Cart button not found"
- Selectors changed (Walmart updates their HTML regularly)
- **Solution:** Report the selector and we'll update `purchase_adapters/walmart.py`

### "CAPTCHA appears"
- Walmart triggered security check
- **Solution:**
  - Use `--mode review` to stop before purchase
  - Manually solve CAPTCHA in browser window
  - In review mode, click "Continue" after manual verification

---

## Performance Impact

| Mode | Speed | Detection Risk | Headless? |
|------|-------|-----------------|-----------|
| Headless (default) | Fast (2-5s per nav) | Medium | Yes |
| Non-Headless | Slower (5-10s per nav) | Lower | No |
| With Proxy | Slightly slower | Lower | Flexible |

**Recommendation:**
- **Testing:** Use `--no-headless --mode review` to debug
- **Production:** Use `--headless --mode live` (faster) + `--proxy` (if rate-limited)

---

## Command Reference

```powershell
# All available options for scheduler
python main.py run [OPTIONS]

OPTIONS:
  --mode {dry-run,review,live}    Execution mode (default: review)
                                   - dry-run: No actions, just log
                                   - review: Stop before final purchase
                                   - live: Full automation
  
  --interval SECONDS              How often to check (default: 60)
  
  --headless                       Run headless browser (default)
  
  --no-headless                    Show browser window (slower, debug mode)
  
  --proxy URL                      HTTP proxy URL
                                   Example: http://proxy.com:8080
  
  --once                           Run one check and exit (GitHub Actions)
  
  --dry-run                        Alias for --mode dry-run

# Examples:
python main.py run --mode review --interval 60
python main.py run --no-headless --mode review  # Debug with visible window
python main.py run --proxy http://my-proxy:8080 --mode live
python main.py run --once --mode dry-run  # Single check (CI/CD)
```

---

## What's NOT Changed

This bot **still refuses to:**
- Bypass CAPTCHA (requires manual intervention)
- Bypass multi-factor authentication (you verify in browser)
- Disable JavaScript protections
- Spoof payment methods
- Scrape competitor sites

These protections **keep the bot legal and safe.**

---

## Files Modified

1. **purchase_engine.py**
   - Added `proxy` parameter
   - Browser context now includes realistic fingerprinting (user agent, viewport, locale, timezone)

2. **purchase_adapters/walmart.py**
   - Replaced all `wait_until="networkidle"` with `wait_until="domcontentloaded"`
   - Added `timeout=60000` to all navigation
   - Wrapped `wait_for_load_state("load")` in try-except to gracefully handle timeouts

3. **purchase_actions.py**
   - Same changes as walmart.py

4. **scheduler.py**
   - `execute_task()` now accepts `headless` and `proxy` parameters
   - `run_once()` and `run_scheduler()` accept and pass through these parameters
   - `_execute_due_tasks()` passes to `execute_task()`

5. **main.py**
   - Added `--headless` / `--no-headless` arguments
   - Added `--proxy` argument
   - Pass these to scheduler methods

---

## Next Steps

1. **Test in review mode:**
   ```powershell
   python main.py run --no-headless --mode review --interval 60
   ```

2. **Watch the browser window** for 5 minutes (one check cycle)

3. **Check logs** for errors:
   ```
   If you see "domcontentloaded" messages = GOOD
   If you see "networkidle timeout" = BAD (shouldn't happen now)
   ```

4. **If it works**, switch to headless for faster execution:
   ```powershell
   python main.py run --mode review --interval 60
   ```

5. **If Walmart rate-limits you** (404, /qp, etc.), add a proxy:
   ```powershell
   python main.py run --proxy http://your-proxy:8080 --mode review --interval 60
   ```

---

Good luck, Roger! Your bot just got **way sneakier**. 

For questions or if Walmart breaks these selectors again, ping me!
