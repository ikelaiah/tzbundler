# 🕐 How to Calculate DST Status

One of the most common questions is: **"How do I determine if DST is active for a specific date and timezone?"**

This section provides practical examples using the tzbundler output.

## 🎯 Quick Example: Sydney on May 23, 2030

**Question:** Is DST active in Sydney, Australia on May 23, 2030? What's the UTC offset?

**Answer:** No, DST is not active. The offset is UTC+10:00 (AEST).

### Step-by-Step Walkthrough

```python
import json
from datetime import datetime, date

# Load your tzbundler output
with open('combined.json', 'r') as f:
    tzdata = json.load(f)

# 1. Find the timezone data
sydney = tzdata['timezones']['Australia/Sydney']
print(f"Base offset: {sydney['transitions'][-1]['offset']}")  # +10:00
print(f"Rule set: {sydney['transitions'][-1]['rule_name']}")  # "AN"
```

```python
# 2. Check the DST rules for the "AN" rule set
an_rules = tzdata['rules']['AN']

# Find the current rules (2008 to max)
current_rules = [rule for rule in an_rules if rule['from'] == '2008' and rule['to'] == 'max']

for rule in current_rules:
    print(f"{rule['in']} {rule['on']}: save {rule['save']} (letter: {rule['letter']})")

# Output:
# Apr Sun>=1: save 0 (letter: S)     <- DST ends (Standard Time)
# Oct Sun>=1: save 1:00 (letter: D)  <- DST starts (Daylight Time)
```

```python
# 3. Calculate the specific dates for 2030
def first_sunday_on_or_after(year, month, day):
    """Find first Sunday on or after the given date"""
    d = date(year, month, day)
    days_ahead = 6 - d.weekday()  # Sunday is 6
    if days_ahead < 0:  # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days=days_ahead)

dst_end_2030 = first_sunday_on_or_after(2030, 4, 1)    # April 7, 2030
dst_start_2030 = first_sunday_on_or_after(2030, 10, 1) # October 6, 2030

test_date = date(2030, 5, 23)

print(f"DST ends: {dst_end_2030}")     # 2030-04-07
print(f"DST starts: {dst_start_2030}") # 2030-10-06
print(f"Test date: {test_date}")       # 2030-05-23

# 4. Determine DST status
is_dst = dst_start_2030 <= test_date or test_date < dst_end_2030

print(f"DST active: {is_dst}")  # False (May 23 is between Apr 7 and Oct 6)
print(f"Offset: UTC+10:00")     # Base offset (no DST offset added)
print(f"Abbreviation: AEST")    # AE%sT with %s = "S" for Standard
```

## 🌍 Understanding the Data Structure

### Transitions
Each timezone has a list of **transitions** - periods when the rules changed:

```json
{
  "from_utc": "",           // When this period starts (empty = current)
  "offset": "+10:00",       // Base UTC offset 
  "abbr": "AE%sT",         // Abbreviation format (%s replaced by rule letter)
  "rule_name": "AN"        // Which DST rule set to use
}
```

### Rules
**Rules** define when DST starts and ends:

```json
{
  "from": "2008",           // Rule applies from year 2008
  "to": "max",             // Rule applies until further notice
  "in": "Apr",             // In April
  "on": "Sun>=1",          // First Sunday on or after April 1
  "save": "0",             // Save 0 hours (Standard Time)
  "letter": "S"            // Use "S" in abbreviation format
}
```

### Common Rule Patterns

| Pattern | Meaning | Example |
|---------|---------|---------|
| `Sun>=1` | First Sunday on or after the 1st | First Sunday in April |
| `lastSun` | Last Sunday of the month | Last Sunday in October |
| `8` | Specific day of month | 8th day of month |
| `save: "1:00"` | Add 1 hour (DST active) | Daylight time |
| `save: "0"` | Add 0 hours (Standard time) | Standard time |

## 🔧 Simple DST Calculator Function

Here's a reusable function for basic DST calculations:

```python
def is_dst_active(timezone_name, target_date, tzdata):
    """
    Simple DST calculator for common cases.
    
    Args:
        timezone_name: e.g., "Australia/Sydney"
        target_date: datetime.date object
        tzdata: Loaded JSON from tzbundler
    
    Returns:
        dict: {'is_dst': bool, 'offset': str, 'abbr': str}
    """
    if timezone_name not in tzdata['timezones']:
        return {'is_dst': False, 'offset': 'UTC+00:00', 'abbr': 'UTC'}
    
    zone = tzdata['timezones'][timezone_name]
    
    # Find the current transition (last one)
    current_transition = zone['transitions'][-1]
    base_offset = current_transition['offset']
    abbr_format = current_transition['abbr']
    rule_name = current_transition['rule_name']
    
    if not rule_name or rule_name == '-':
        # No DST rules, always standard time
        return {
            'is_dst': False,
            'offset': base_offset,
            'abbr': abbr_format.replace('%s', '')
        }
    
    # Get the DST rules
    rules = tzdata['rules'].get(rule_name, [])
    
    # Find current rules (simplified - looks for 2008 to max pattern)
    dst_rules = [r for r in rules if r['from'] <= str(target_date.year) <= r.get('to', '9999')]
    
    # Basic DST calculation (this is simplified!)
    # For a complete implementation, you'd need to handle all IANA date formats
    dst_active = False
    dst_letter = 'S'  # Default to Standard
    
    for rule in dst_rules:
        if rule['save'] != '0' and rule['save'] != '0:00':
            # This is a DST rule
            if rule['in'] in ['Mar', 'Apr', 'Sep', 'Oct']:  # Common DST months
                # Simplified check - real implementation would calculate exact dates
                dst_active = True
                dst_letter = rule['letter']
                break
    
    # Format abbreviation
    abbr = abbr_format.replace('%s', dst_letter)
    
    return {
        'is_dst': dst_active,
        'offset': base_offset,  # Simplified - should add DST offset
        'abbr': abbr
    }

# Example usage
result = is_dst_active('Australia/Sydney', date(2030, 5, 23), tzdata)
print(f"DST: {result['is_dst']}, Offset: {result['offset']}, Abbr: {result['abbr']}")
```

## 🌐 Common Timezones Quick Reference

| Timezone | DST Rule | Summer Period | Winter Offset | Summer Offset |
|----------|----------|---------------|---------------|---------------|
| `Australia/Sydney` | AN | Oct-Apr | UTC+10 (AEST) | UTC+11 (AEDT) |
| `America/New_York` | US | Mar-Nov | UTC-5 (EST) | UTC-4 (EDT) |
| `Europe/London` | EU | Mar-Oct | UTC+0 (GMT) | UTC+1 (BST) |
| `America/Los_Angeles` | US | Mar-Nov | UTC-8 (PST) | UTC-7 (PDT) |

## 💡 Pro Tips

1. **Southern Hemisphere:** DST typically runs October → April (summer)
2. **Northern Hemisphere:** DST typically runs March → October/November (summer)
3. **Rule Letters:** `S` = Standard, `D` = Daylight, `T` = Time
4. **Abbreviation Formats:** `%s` gets replaced by the rule letter
5. **Always verify:** Use the rules data rather than assuming patterns

## 🔗 For Production Use

For production applications, consider using established libraries that handle all edge cases:

- **Python:** `pytz`, `zoneinfo` (Python 3.9+)
- **JavaScript:** `date-fns-tz`, `luxon`
- **Java:** `java.time.ZoneId`
- **Go:** `time.LoadLocation()`

The tzbundler output is perfect for:
- Research and analysis
- Custom DST logic
- Cross-platform data exchange
- Educational purposes
- Building timezone libraries

---

This guide shows simplified examples. For production use, you'll need to handle all IANA date/time formats, leap years, historical changes, and edge cases. The rules data in tzbundler gives you everything needed for a complete implementation!