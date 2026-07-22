# Purchase Bot Scheduling Guide

This guide explains how to schedule purchases using all 6 schedule types. The UI now makes it crystal clear!

---

## Quick Decision Tree

**"I want to buy at exactly 3:00 PM every day"**
→ Use **Daily**

**"I want to buy once at 8:00 PM tonight"**
→ Use **Once**

**"I want to buy every Monday, Wednesday, Friday at 9:00 AM"**
→ Use **Weekly**

**"I want to buy sometime between 5:00 PM and 7:00 PM (bot picks the best time)"**
→ Use **Daily in Window**

**"I want to buy sometime between 7:00 PM and 10:00 PM, but only once"**
→ Use **Once in Window**

**"I want to buy sometime between 8:00 PM and 9:00 PM on Tuesdays and Thursdays"**
→ Use **Weekly in Window**

---

## The 6 Schedule Types (Detailed)

### 1. Once - Buy One Time at Exact Time

**What it does:** Runs exactly one time at the specified time, then never again.

**Use cases:**
- Limited-time product drop at 3:00 PM today
- Pre-order opens at 8:00 AM tomorrow
- Flash sale ends at 6:00 PM

**Configuration:**
- Schedule Type: **Once**
- Time: **14:00** (2:00 PM)

**Example:**
```
Schedule Type: Once
Run Time: 14:00 (or 2:00 PM)

Result: Bot runs once at 2:00 PM today. After that, task is done.
```

**Important:** The task won't run if the specified time has already passed today. The scheduler checks if it's "at or after" the time.

---

### 2. Daily - Buy Every Day at Exact Time

**What it does:** Runs every single day at the same time.

**Use cases:**
- Stock check every morning at 8:00 AM
- Daily restock event at noon
- Regular automated shopping at 5:30 PM

**Configuration:**
- Schedule Type: **Daily**
- Time: **08:00** (8:00 AM)

**Example:**
```
Schedule Type: Daily
Run Time: 08:00

Result: Bot runs at 8:00 AM today, tomorrow, next week, forever.
```

---

### 3. Weekly - Buy on Specific Days at Exact Time

**What it does:** Runs on selected days of the week at the same time.

**Use cases:**
- Monday/Wednesday/Friday deals at 3:00 PM
- Walmart Rollback restocks on specific days
- Weekly preferred shopping schedule

**Configuration:**
- Schedule Type: **Weekly**
- Time: **15:00** (3:00 PM)
- Days: **Mon,Wed,Fri**

**Example:**
```
Schedule Type: Weekly
Run Time: 15:00
Days: Mon,Wed,Fri

Result: Bot runs at 3:00 PM every Monday, Wednesday, and Friday.
Skips Tue, Thu, Sat, Sun.
```

**Format for Days:**
- Comma-separated: `Mon,Wed,Fri`
- Full names: `Monday,Wednesday,Friday`
- Mix works: `Mon,Wednesday,Fri`
- All days: `Mon,Tue,Wed,Thu,Fri,Sat,Sun`

---

### 4. Once in Window - Buy Once Between Two Times

**What it does:** Runs one time anytime between start and end time. Bot picks the best moment.

**Use cases:**
- "Sometime between 8:00 PM and 10:00 PM tonight"
- Limited inventory - bot waits for optimal moment
- Avoid exact time that others might target

**Configuration:**
- Schedule Type: **Once in Window**
- Start Time: **20:00** (8:00 PM, earliest)
- End Time: **22:00** (10:00 PM, latest)

**Example:**
```
Schedule Type: Once in Window
Start Time: 20:00
End Time: 22:00

Result: Bot runs exactly once, sometime between 8:00 PM and 10:00 PM.
After running once, never runs again (regardless of when within window).
```

**Good for:**
- "Run sometime this evening"
- Beating exact-time traffic (others auto-buy at 8:00 PM sharp)
- Waiting for best price within a window

---

### 5. Daily in Window - Buy Daily Between Two Times

**What it does:** Every day, runs once anytime between start and end time.

**Use cases:**
- Check inventory daily between 7:00 PM and 9:00 PM
- Buy during daily restock window (always happens 6-8 PM)
- Flexible daily purchasing

**Configuration:**
- Schedule Type: **Daily in Window**
- Start Time: **19:00** (7:00 PM)
- End Time: **21:00** (9:00 PM)

**Example:**
```
Schedule Type: Daily in Window
Start Time: 19:00
End Time: 21:00

Result: Bot runs once each day, sometime between 7:00 PM and 9:00 PM.
Each day, it picks a new time within the window.
Runs forever (daily).
```

**Behavior:**
- Day 1: Bot runs at 7:43 PM
- Day 2: Bot runs at 8:15 PM
- Day 3: Bot runs at 7:52 PM
- (Each day, a different time within the window)

---

### 6. Weekly in Window - Buy Weekly Between Two Times

**What it does:** On selected days, runs once anytime between start and end time.

**Use cases:**
- "Run on Mon/Wed/Fri between 5:00-7:00 PM"
- Weekly restocks that happen sometime in a window
- Flexible weekly purchasing on specific days

**Configuration:**
- Schedule Type: **Weekly in Window**
- Start Time: **17:00** (5:00 PM)
- End Time: **19:00** (7:00 PM)
- Days: **Mon,Wed,Fri**

**Example:**
```
Schedule Type: Weekly in Window
Start Time: 17:00
End Time: 19:00
Days: Mon,Wed,Fri

Result: Every Monday, Wednesday, and Friday, bot runs once
between 5:00 PM and 7:00 PM. Skips other days.
```

**Behavior:**
- Monday: Runs at 5:45 PM
- Tuesday: Skips (not in days list)
- Wednesday: Runs at 6:12 PM
- Thursday: Skips
- Friday: Runs at 5:33 PM
- etc.

---

## Time Format Examples

The bot accepts multiple time formats:

```
Exact Times:
- 14:00 (24-hour format)
- 14:30 (with minutes)
- 2:00 PM (12-hour format)
- 2:30 PM (12-hour with minutes)
- 11:15 PM (evening time)
- 9:00 AM (morning time)

All of these work and mean the same thing!
```

---

## Timezone Support (Optional)

By default, times are relative to your computer's timezone.

If you want to specify a different timezone:

```
Timezone: CST (Central Standard Time)
Or: America/Chicago
Or: CT (abbreviation)
```

**Common timezone abbreviations:**
- **CST / CT** → America/Chicago (Central)
- **EST / ET** → America/New_York (Eastern)
- **PST / PT** → America/Los_Angeles (Pacific)
- **MST / MT** → America/Denver (Mountain)

**Or use full timezone names:**
- America/New_York
- Europe/London
- Asia/Tokyo
- Australia/Sydney

---

## Real-World Examples

### Example 1: Daily 9-to-5 Shopper
```
Schedule Type: Daily
Run Time: 09:00

Every morning at 9:00 AM, bot checks inventory and buys if available.
```

### Example 2: Weekend Deal Hunter
```
Schedule Type: Weekly
Run Time: 09:00
Days: Sat,Sun

Every Saturday and Sunday at 9:00 AM, bot tries to buy.
Skips weekdays.
```

### Example 3: Walmart Restock Window (Changes Often)
```
Schedule Type: Daily in Window
Start Time: 07:00
End Time: 09:00

Walmart often restocks between 7-9 AM. Bot checks daily in that window,
avoids exact timing traffic.
```

### Example 4: Limited-Time Flash Sale (Tonight Only)
```
Schedule Type: Once in Window
Start Time: 20:00
End Time: 23:59

Sale happens sometime tonight 8 PM-midnight.
Bot tries once, picking best moment in window.
```

### Example 5: Micro-Drops on Specific Days
```
Schedule Type: Weekly in Window
Start Time: 14:00
End Time: 14:15
Days: Mon,Thu

Inventory drops for 15 minutes on Monday and Thursday, 2-2:15 PM.
Bot tries Mon and Thu between 2-2:15 PM.
```

### Example 6: Pre-Order at Exact Time
```
Schedule Type: Once
Run Time: 10:00

Pre-order goes live at 10:00 AM sharp.
Bot buys exactly at 10:00 AM (or just after).
```

---

## Tips & Tricks

### Tip 1: Avoid Exact Times
If thousands of people are buying at exactly 8:00 PM, use a **window** instead:

```
AVOID (too predictable):
Schedule Type: Daily
Run Time: 20:00

USE (less traffic):
Schedule Type: Daily in Window
Start Time: 20:00
End Time: 20:15
```

The window-based approach makes the bot less predictable to rate limiters.

---

### Tip 2: Use Offset Schedules
If your item restocks at 8:00 PM but you want to avoid auto-buyer traffic:

```
Instead of running at 8:00 PM exactly:
Schedule Type: Daily in Window
Start Time: 20:00
End Time: 20:30

Bot runs sometime between 8-8:30 PM, avoiding exact-time collision.
```

---

### Tip 3: Weekly Schedules Save Resources
If you only need to buy on certain days, use **Weekly** instead of **Daily**:

```
WASTES TIME (checks every day, only buys 2x/week):
Schedule Type: Daily
Run Time: 09:00

EFFICIENT (only checks on relevant days):
Schedule Type: Weekly
Run Time: 09:00
Days: Mon,Fri
```

---

### Tip 4: Combine with Price Limits
Set a schedule + price limit for safety:

```
Schedule: Daily at 9:00 AM
Account: walmart_main
Price Limit: $25 per item (enabled)

Result: Every day at 9 AM, bot tries to buy.
But if price is over $25, it skips (safe!).
```

---

## Editing a Schedule

To change when a task runs:

1. Go to **Tasks** tab
2. Find the task
3. Click **"Edit task"** (expandable section)
4. Change Schedule Type, Time, Days, etc.
5. Click **"Save Changes"**

The task is updated immediately. Current schedule continues, new settings apply next cycle.

---

## Disabling vs. Deleting

**Disable** = Stop running, but keep the task saved.
```
Use when: You want to pause temporarily.
→ Task still exists, just doesn't run.
→ Can re-enable anytime.
```

**Delete** = Permanently remove the task.
```
Use when: You never want this task again.
→ Task is gone, can't be recovered.
```

---

## Troubleshooting

**Q: Why didn't my "Once" task run?**
A: The specified time already passed today. "Once" runs once at the specified time. If it's 3:00 PM and your "Once" task is set for 2:00 PM, it won't run (already past). Set it for tomorrow or use a different time.

**Q: My "Weekly" task didn't run on Monday. Why?**
A: Make sure "Mon" is in the Days field. If Days is empty, the task is invalid. Always set at least one day for weekly tasks.

**Q: Should I use 24-hour or 12-hour time?**
A: Both work! "14:00" and "2:00 PM" are identical. Pick whichever you're comfortable with.

**Q: Can I buy at 2:30 AM?**
A: Yes! The time can be any hour:minute. "02:30" works fine for 2:30 AM.

**Q: Does the window mode actually help avoid rate limits?**
A: Probably yes! Instead of every bot hitting at 8:00:00 PM sharp, windows spread requests across a time range. Makes you look more human, less coordinated with other bots.

---

## Summary Table

| Schedule | Exact Time? | Recurring? | Weekly Days? | Best For |
|----------|-----------|-----------|--------------|----------|
| Once | Yes | No | N/A | One-time drops, pre-orders |
| Daily | Yes | Yes | N/A | Regular daily shopping |
| Weekly | Yes | Yes | Yes | Weekly deals on specific days |
| Once in Window | No (picks time) | No | N/A | One-time, avoid exact traffic |
| Daily in Window | No (picks time) | Yes | N/A | Daily within a time range |
| Weekly in Window | No (picks time) | Yes | Yes | Weekly within a time range |

---

## Need Help?

- **Time format wrong?** Try "14:00" or "2:00 PM" (both work)
- **Task not running?** Check if enabled (green badge), time is future, days include today
- **Want to test?** Use `--dry-run` mode to simulate without buying
- **Logs?** Check `purchase_bot.log` for detailed execution history

You're all set! Schedule your tasks and let the bot do the work.
