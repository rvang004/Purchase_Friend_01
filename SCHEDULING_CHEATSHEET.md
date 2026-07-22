# Scheduling Quick Reference (Cheat Sheet)

## Pick Your Schedule in 10 Seconds

### I want to buy at EXACTLY the same time every day?
```
Schedule Type: Daily
Time: 09:00
Result: Every single day at 9:00 AM
```

### I want to buy ONCE at a specific time?
```
Schedule Type: Once
Time: 14:00
Result: One time at 2:00 PM, then never again
```

### I want to buy on CERTAIN DAYS at the same time?
```
Schedule Type: Weekly
Time: 15:00
Days: Mon,Wed,Fri
Result: Every Mon/Wed/Fri at 3:00 PM
```

### I want to buy SOMETIME BETWEEN two times (once only)?
```
Schedule Type: Once in Window
Start Time: 20:00
End Time: 22:00
Result: Once, anytime between 8:00 PM and 10:00 PM
```

### I want to buy DAILY in a time window (flexible)?
```
Schedule Type: Daily in Window
Start Time: 19:00
End Time: 21:00
Result: Every day, anytime between 7:00 PM and 9:00 PM
```

### I want to buy on CERTAIN DAYS in a time window?
```
Schedule Type: Weekly in Window
Start Time: 18:00
End Time: 20:00
Days: Tue,Thu
Result: Every Tue/Thu, anytime between 6:00 PM and 8:00 PM
```

---

## Time Format (Any of These Work)

```
24-hour format:  14:00, 20:30, 09:15
12-hour format:  2:00 PM, 8:30 PM, 9:15 AM
```

---

## Days Format

```
Comma-separated, abbreviated:
Mon,Wed,Fri
Mon,Tue,Wed,Thu,Fri,Sat,Sun

Or full names:
Monday,Wednesday,Friday
```

---

## Common Scenarios

| Need | Use | Config |
|------|-----|--------|
| Buy at 8 PM every night | Daily | Time: 20:00 |
| Buy Fri at 10 AM | Weekly | Time: 10:00, Days: Fri |
| Buy once today at 3 PM | Once | Time: 15:00 |
| Buy anytime 8-10 PM today | Once in Window | Start: 20:00, End: 22:00 |
| Buy Mon/Wed/Fri anytime 2-4 PM | Weekly in Window | Start: 14:00, End: 16:00, Days: Mon,Wed,Fri |
| Buy daily 7-9 PM (flexible) | Daily in Window | Start: 19:00, End: 21:00 |

---

## Pro Tips

**Avoid exact times** if rate-limited:
```
Instead of: Daily at 20:00
Use: Daily in Window 20:00-20:15
(Less predictable, avoids traffic)
```

**Check timezone if needed**:
```
Default: Your computer's timezone
Custom: CST, PT, America/Chicago, etc.
```

**Combine with price limits**:
```
Schedule: Daily at 9 AM
Price Limit: $50 per item (enabled)
→ Safe: Never buys over $50
```

---

## Syntax Examples

### Example 1: Flash Sale Tonight
```
Schedule Type: Once in Window
Start Time: 20:00
End Time: 23:59
→ Buys once tonight between 8 PM and 11:59 PM
```

### Example 2: Daily Habit
```
Schedule Type: Daily
Run Time: 08:00
→ Checks every day at 8 AM
```

### Example 3: Weekend Shopping
```
Schedule Type: Weekly
Run Time: 10:00
Days: Sat,Sun
→ Buys Saturdays and Sundays at 10 AM
```

### Example 4: Walmart Restock Window (Every Morning)
```
Schedule Type: Daily in Window
Start Time: 06:00
End Time: 08:00
→ Buys daily 6-8 AM (when restocks happen)
```

### Example 5: Specific Deal Days
```
Schedule Type: Weekly in Window
Start Time: 19:00
End Time: 20:00
Days: Tue,Thu
→ Buys Tue/Thu evenings 7-8 PM
```

---

## The 6 Types at a Glance

```
EXACT TIME MODES:
┌─ Once        → Run 1x at exact time
├─ Daily       → Run daily at exact time
└─ Weekly      → Run on specific days at exact time

WINDOW MODES (bot picks time within range):
┌─ Once in Window     → Run 1x anytime in window
├─ Daily in Window    → Run daily anytime in window
└─ Weekly in Window   → Run weekly anytime in window
```

---

## Testing Your Schedule

Use dry-run mode:
```powershell
python main.py run --dry-run --interval 30
```

Logs show: "Task X would run at [time]" without actually buying.

---

## Editing a Task

1. Tasks tab
2. Find task
3. Click "Edit task"
4. Change schedule
5. Save Changes

New settings apply next cycle.

---

## Remember

- **Enabled?** Make sure green badge shows "Enabled"
- **Time in future?** "Once" won't run if time already passed
- **Days for weekly?** Must have at least one day (Mon,Tue, etc.)
- **Quantity?** Set in same form (default: 1)
- **Price limit?** Add in Accounts tab if needed

---

**More details?** See SCHEDULING_GUIDE.md for full explanations.
