# 🌐 tzkit: IANA Time Zone Database Parser

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![IANA tzdata](https://img.shields.io/badge/IANA-tzdata%202025b-green.svg)](https://www.iana.org/time-zones)

A Python tool that parses IANA tzdata files and converts them into machine-readable formats (JSON and SQLite). Perfect for applications, research, or data analysis involving time zones.

Or you can simply use the pre-generated bundle from `tzdata/` folder or [the Releases page](https://github.com/ikelaiah/tzkit/releases).

## 🎯 Who Should Use tzkit?

- App developers who need reliable time zone handling
- Researchers working on temporal/historical datasets
- Anyone who wants a cross-language-compatible tzdata format (e.g. for Python, Free Pascal, JS)

## ✨ Features

- **Simple one-command operation**: Just run `python make_tz_bundle.py`
- **Multiple output formats**: JSON and SQLite database
- **Complete data extraction**: Zones, transitions, rules, and aliases
- **Rich metadata**: Country codes, coordinates, and comments
- **Version tracking**: Automatically includes tzdata version info
- **Consumer-driven DST logic**: Raw rule data provided for flexible DST calculations

## 🚀 Quick Start

```bash
python make_tz_bundle.py
```

This single command will:

1. Fetch the latest IANA tzdata
2. Extract and parse all files
3. Generate `combined.json` and `combined.sqlite` in the `tzdata/` folder

## 🚀 Quick Start - Alternative

Use the pre-generated `.json` or `.sqlite` bundle from `tzdata/` folder or [the Releases page](https://github.com/ikelaiah/tzkit/releases).

## 📊 Data Model

### Zone
Represents a time zone with its complete history and metadata.

```python
@dataclass
class Zone:
    name: str                       # e.g., "Asia/Seoul"
    country_code: str               # e.g., "KR" 
    latitude: str                   # from coordinates
    longitude: str                  # from coordinates  
    comment: str                    # optional description
    transitions: List[Transition]   # historical transitions
    aliases: List[str]              # alternative names
```

### 🔄 Transition
Represents a period in a zone's history (offset changes, DST periods, etc.).

> **Note**: DST status is not pre-calculated. Consumers should use the rules data to determine DST as needed.

```python
@dataclass  
class Transition:
    from_utc: str              # when this period starts
    to_utc: Optional[str]      # when this period ends
    offset: str                # UTC offset (e.g., "+09:00")
    abbr: str                  # abbreviation (e.g., "KST", "JST")
    # rule_name: Optional[str] # attached as attribute during parsing
```

### 📏 Rule

Represents a single DST rule definition (from a Rule line in tzdata).

```json
"rules": {
  "Japan": [
    {
      "from": "1948",
      "to": "only",
      "type": "-",
      "in": "Sep",
      "on": "10",
      "at": "0:00",
      "save": "1:00",
      "letter": "D"
    }
  ]
}
```

## 📁 Input Files

The tool processes these IANA tzdata files:

| File Category | Files | Contains |
|---------------|-------|----------|
| **Zone Data** | `africa`, `antarctica`, `asia`, `australasia`, `europe`, `northamerica`, `southamerica` | Zone blocks, Rule lines, Link lines |
| **Additional** | `etcetera`, `backward`, `backzone` | Extra zones and compatibility aliases |
| **Metadata** | `zone1970.tab` | Country codes, coordinates, comments |
| **Version** | `version` | tzdata release version |

## 📤 Output Files

### 📝 JSON Format (`combined.json`)

```json
{
  "timezones": {
    "Asia/Seoul": {
      "country_code": "KR",
      "coordinates": "+3733+12658", 
      "comment": "",
      "transitions": [
        {
          "from_utc": "1904 Dec",
          "to_utc": null,
          "offset": "+08:30",
          "abbr": "KST",
          "rule_name": null
        },
        {
          "from_utc": "1948 May 8",
          "to_utc": null,
          "offset": "+09:00",
          "abbr": "KDT",
          "rule_name": "Korea"
        }
      ],
      "aliases": ["ROK"]
    }
  },
  "rules": {
    "Korea": [
      {
        "from": "1948",
        "to": "only",
        "type": "-",
        "in": "May",
        "on": "8",
        "at": "0:00",
        "save": "1:00",
        "letter": "D"
      }
    ]
  },
  "_version": "2025b"
}
```

### 💾 SQLite Database (`combined.sqlite`)
Three normalized tables:

**🗄️ zones**
- `name` (TEXT PRIMARY KEY)
- `country_code` (TEXT) 
- `latitude` (TEXT)
- `longitude` (TEXT)
- `comment` (TEXT)

**transitions**  
- `zone_name` (TEXT)
- `from_utc` (TEXT)
- `to_utc` (TEXT)
- `offset` (TEXT)
- `abbr` (TEXT)
- `rule_name` (TEXT)

**rules**
- `rule_name` (TEXT)
- `from_year` (TEXT)
- `to_year` (TEXT)
- `type` (TEXT)
- `in_month` (TEXT)
- `on_day` (TEXT)
- `at_time` (TEXT)
- `save` (TEXT)
- `letter` (TEXT)

## 🧠 How to Use the Rules (DST Logic)

**tzkit provides raw rule data - DST calculations are your responsibility.**

To determine if DST is in effect for a given zone and date:

1. **Find the relevant transition** for the zone and date (by checking `from_utc`/`to_utc`).
2. If the transition's `rule_name` is not `null` or `"-"`, look up the rule set in the `rules` table/object.
3. Apply the rule logic for the given year/month/day/time to determine if DST is active and what the abbreviation should be.

### Pseudocode Example

```python
def calculate_dst_status(zone_name, target_date, transitions, rules):
    """
    Calculate DST status for a given zone and date.
    
    Note: This is a simplified example. Full implementation requires
    complex date/time parsing and rule application logic.
    """
    # 1. Find the active transition for this date
    for transition in transitions[zone_name]:
        if transition_applies_to_date(transition, target_date):
            rule_name = transition.get('rule_name')
            
            # No DST rule applies
            if not rule_name or rule_name == '-':
                return False, transition['abbr']
            
            # 2. Apply the DST rules
            rule_set = rules.get(rule_name, [])
            for rule in rule_set:
                if rule_applies_to_date(rule, target_date):
                    # DST is active if save > 0
                    is_dst = rule['save'] != '0:00'
                    # Calculate abbreviation using rule['letter']
                    abbr = apply_format_with_letter(transition['abbr'], rule['letter'])
                    return is_dst, abbr
            
            # No matching rule found
            return False, transition['abbr']
    
    return False, "UTC"  # Fallback

# Helper functions (you need to implement these)
def transition_applies_to_date(transition, date): pass
def rule_applies_to_date(rule, date): pass  
def apply_format_with_letter(format_str, letter): pass
```

For a complete implementation, see the [IANA tzdata Theory file](https://data.iana.org/time-zones/theory.html) or use a reference library like `pytz` or `dateutil`.

### Language-Agnostic Output

- All data is exported as standard JSON arrays/objects and SQLite tables.
- No language-specific types or code required.
- You can load and use the data in Python, Ruby, JavaScript, Pascal, LISP, etc.

**Tip:** The rules table/object is a direct mapping of the IANA Rule lines, so you can implement DST logic in any language using this data.

### SQL Query Examples

```sql
-- Get all transitions for Australia/Sydney
SELECT * FROM transitions WHERE zone_name = 'Australia/Sydney';

-- List all countries with more than one time zone
SELECT country_code, COUNT(*) FROM zones GROUP BY country_code HAVING COUNT(*) > 1;

-- Find zones that use a specific DST rule
SELECT DISTINCT zone_name FROM transitions WHERE rule_name = 'US';

-- Get all DST rules for a specific rule set
SELECT * FROM rules WHERE rule_name = 'US' ORDER BY from_year;
```

## How Parsing Works

### Zone Block Example (from tzdata source)

```text
Zone    Asia/Baku    3:19:24 -    LMT    1924 May 2
                     3:00    -    %z     1957 Mar  
                     4:00    RussiaAsia %z 1991 Mar 31 2:00s
                     3:00    RussiaAsia %z 1992 Sep lastSun 2:00s
                     4:00    -    %z     1996
                     4:00    EUAsia %z  1997
                     4:00    Azer   %z
```

#### 1. Zone Block Structure

- The first line starts with `Zone` and the zone name (`Asia/Baku`).
- The following indented lines (no `Zone` keyword) are *continuations*—each describes a new period (transition) in the zone's history.

#### 2. Parsing Steps

**a. Create a `Zone` object:**

```python
zone = Zone(name="Asia/Baku")
```

**b. For each line (including the first), create a `Transition`:**

| Line | from_utc (UNTIL) | offset | rule | abbr (FORMAT) | rule_name |
|------|------------------|--------|------|---------------|-----------|
| Zone Asia/Baku 3:19:24 - LMT 1924 May 2 | "1924 May 2" | "3:19:24" | "-" | "LMT" | null |
| 3:00 - %z 1957 Mar | "1957 Mar" | "3:00" | "-" | "%z" | null |
| 4:00 RussiaAsia %z 1991 Mar 31 2:00s | "1991 Mar 31 2:00s" | "4:00" | "RussiaAsia" | "%z" | "RussiaAsia" |
| 3:00 RussiaAsia %z 1992 Sep lastSun 2:00s | "1992 Sep lastSun 2:00s" | "3:00" | "RussiaAsia" | "%z" | "RussiaAsia" |
| 4:00 - %z 1996 | "1996" | "4:00" | "-" | "%z" | null |
| 4:00 EUAsia %z 1997 | "1997" | "4:00" | "EUAsia" | "%z" | "EUAsia" |
| 4:00 Azer %z | "" | "4:00" | "Azer" | "%z" | "Azer" |

Each line becomes:

```python
transition = Transition(
    from_utc="1924 May 2",  # UNTIL value (when this transition ends)
    to_utc=None,            # Calculated later if needed
    offset="3:19:24",
    abbr="LMT"             # or "%z" (determined by rules)
)
# Attach rule name as attribute
transition.rule_name = "RussiaAsia"  # or None if "-"
zone.transitions.append(transition)
```

#### 3. Output Structure (JSON)

```json
{
  "timezones": {
    "Asia/Baku": {
      "country_code": "AZ",
      "latitude": "+4023",
      "longitude": "+04951",
      "comment": "",
      "transitions": [
        {
          "from_utc": "1924 May 2",
          "to_utc": null,
          "offset": "3:19:24",
          "abbr": "LMT",
          "rule_name": null
        }
      ],
      "aliases": []
    }
  },
  "rules": {
    "RussiaAsia": [ ... ],
    "EUAsia": [ ... ],
    "Azer": [ ... ]
  },
  "_version": "2025b"
}
```

#### 4. Notes

- The `abbr` field is `"LMT"` or `"%z"` (which means the abbreviation is determined by rules).
- The `rule_name` field (e.g., `"RussiaAsia"`, `"EUAsia"`, `"Azer"`) is used to look up DST rules.
- The `from_utc` field is the UNTIL value (when this transition ends).
- Metadata (`country_code`, `latitude`, etc.) is added later from `zone1970.tab`.
- **DST calculations are left to consumers** using the rules data.

#### 5. Summary

Each line in the zone block becomes a `Transition` in the `Zone.transitions` list. The zone itself is created once, and metadata is attached later. DST status must be calculated by consumers using the provided rules.

### Data Processing Flow

```
Raw tzdata files → Parse zones/rules/links → Enrich with metadata → Output JSON/SQLite
```

## File Structure

```
tzdata_raw/     # Downloaded raw files
tzdata/         # Processed output
├── combined.json
└── combined.sqlite  
```

## Use Cases

![Use Cases](https://img.shields.io/badge/💼-Use%20Cases-blueviolet.svg)

- **Application Development**: Integrate comprehensive time zone data
- **Data Analysis**: Research time zone changes and patterns  
- **Historical Analysis**: Track offset changes over time
- **Compliance**: Ensure accurate time zone handling
- **Custom DST Logic**: Implement domain-specific DST calculations

## Installation & Requirements

```python
# Required Python packages
requests>=2.25.0    # For downloading tzdata
```

Clone and run:
```bash
git clone https://github.com/yourusername/tzkit.git
cd tzkit
pip install -r requirements.txt
python make_tz_bundle.py
```

## Important Design Decision

**tzkit does not pre-calculate DST status.** Instead, it provides:

- ✅ Raw transition data (offsets, dates, abbreviations)
- ✅ Complete DST rule definitions  
- ✅ Rule names linked to transitions
- ❌ Pre-calculated DST boolean flags

**Why?** This design:
- Avoids bundler bugs affecting DST calculations
- Allows consumers to implement DST logic that fits their needs
- Enables caching and on-demand DST computation
- Keeps complex temporal logic out of the data extraction layer

## Resources

- [IANA Time Zone Database](https://www.iana.org/time-zones)
- [tzdata Format Documentation](https://data.iana.org/time-zones/theory.html)
- [tzdata Theory File](https://data.iana.org/time-zones/theory.html) (Essential for DST implementation)

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE.md)