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
    name: str                   # e.g., "Asia/Seoul"
    country_code: str           # e.g., "KR" 
    latitude: str               # from coordinates
    longitude: str              # from coordinates  
    comment: str                # optional description
    rules: List[Transition]     # historical transitions
    aliases: List[str]          # alternative names
```


### 🔄 Transition
Represents a period in a zone's history (offset changes, DST periods, etc.).

```python
@dataclass  
class Transition:
    from_utc: str              # when this period starts
    to_utc: Optional[str]      # when this period ends
    offset: str                # UTC offset (e.g., "+09:00")
    is_dst: bool               # daylight saving time active
    abbr: str                  # abbreviation (e.g., "KST", "JST")
    rule_name: Optional[str]   # name of DST rule set (if any)
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
    },
    ...
  ],
  ...
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
  "Asia/Seoul": {
    "country_code": "KR",
    "coordinates": "+3733+12658", 
    "comment": "",
    "rules": [
      {
        "from_utc": "1904 Dec",
        "to_utc": "1932",
        "offset": "+08:30",
        "is_dst": false,
        "abbr": "KST",
        "rule_name": null
      },
      {
        "from_utc": "1948 May 8",
        "to_utc": "1948 Sep 12",
        "offset": "+09:00",
        "is_dst": true,
        "abbr": "KDT",
        "rule_name": "Korea"
      }
    ],
    "aliases": ["ROK"]
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
      },
      ...
    ],
    ...
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
- `is_dst` (BOOLEAN)
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

To determine if DST is in effect for a given zone and date:

1. **Find the relevant transition** for the zone and date (by checking `from_utc`/`to_utc`).
2. If the transition's `rule_name` is not `null` or `"-"`, look up the rule set in the `rules` table/object.
3. Apply the rule logic for the given year/month/day/time to determine if DST is active and what the abbreviation should be.

### Pseudocode Example

```python
# Given: zone_name, date (as datetime), all transitions, all rules
def is_dst(zone_name, date, transitions, rules):
    # 1. Find the transition for this date
    for t in transitions[zone_name]:
        if t['from_utc'] <= date < (t['to_utc'] or '9999-12-31'):
            rule_name = t.get('rule_name')
            if not rule_name or rule_name == '-':
                return t['is_dst']
            # 2. Find the rule set
            rule_set = rules.get(rule_name, [])
            # 3. Apply rule logic (see IANA tzdata Theory)
            for rule in rule_set:
                # Check if rule applies for this year/month/day/time
                # (Implement full logic as per tzdata spec)
                pass
            # If no rule matches, fallback to transition's is_dst
            return t['is_dst']
    return False
```

For a full implementation, see the [IANA tzdata Theory file](https://data.iana.org/time-zones/theory.html) or use a reference library.

### Language-Agnostic Output

- All data is exported as standard JSON arrays/objects and SQLite tables.
- No language-specific types or code required.
- You can load and use the data in Python, Ruby, JavaScript, Pascal, LISP, etc.

**Tip:** The rules table/object is a direct mapping of the IANA Rule lines, so you can implement DST logic in any language using this data.

**Examples**

```sql
-- Get all transitions for Australia/Sydney
SELECT * FROM transitions WHERE zone_name = 'Australia/Sydney';

-- List all countries with more than one time zone
SELECT country_code, COUNT(*) FROM zones GROUP BY country_code HAVING COUNT(*) > 1;
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

| Line | from_utc (UNTIL)         | offset   | rule        | abbr (FORMAT) | is_dst | to_utc | rule_name |
|------|--------------------------|----------|-------------|---------------|--------|--------|-----------|
| Zone Asia/Baku 3:19:24 - LMT 1924 May 2 | "1924 May 2" | "3:19:24" | "-"         | "LMT"         | False  | None   | null      |
| 3:00 - %z 1957 Mar              | "1957 Mar" | "3:00"    | "-"         | "%z"         | False  | None   | null      |
| 4:00 RussiaAsia %z 1991 Mar 31 2:00s | "1991 Mar 31 2:00s" | "4:00" | "RussiaAsia" | "%z"         | False  | None   | "RussiaAsia" |
| 3:00 RussiaAsia %z 1992 Sep lastSun 2:00s | "1992 Sep lastSun 2:00s" | "3:00" | "RussiaAsia" | "%z"         | False  | None   | "RussiaAsia" |
| 4:00 - %z 1996                  | "1996"    | "4:00"    | "-"         | "%z"         | False  | None   | null      |
| 4:00 EUAsia %z 1997             | "1997"    | "4:00"    | "EUAsia"    | "%z"         | False  | None   | "EUAsia"  |
| 4:00 Azer %z                    | ""        | "4:00"    | "Azer"      | "%z"         | False  | None   | "Azer"    |

Each line becomes:

```python
transition = Transition(
    from_utc="1924 May 2",  # or whatever UNTIL value is present
    to_utc=None,            # (not parsed in this block)
    offset="3:19:24",
    is_dst=False,           # (can be set based on rules, but default False here)
    abbr="LMT",            # or "%z", etc.
    rule_name=None          # or the rule name if present
)
zone.rules.append(transition)
```
Repeat for each line.

#### 3. Output Structure (JSON)

In your output, all time zones are grouped under a `"timezones"` root key, and all rules under a `"rules"` root key:

```json
{
  "timezones": {
    "Asia/Baku": {
      "country_code": "AZ",
      "latitude": "+4023",
      "longitude": "+04951",
      "comment": "",
      "rules": [
        {
          "from_utc": "1924 May 2",
          "to_utc": null,
          "offset": "3:19:24",
          "is_dst": false,
          "abbr": "LMT",
          "rule_name": null
        },
        ...
      ],
      "aliases": []
    },
    ...
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
- The `rule_name` field (e.g., `"RussiaAsia"`, `"EUAsia"`, `"Azer"`) is used to look up DST rules, which can affect `is_dst` and `abbr` if you implement full rule parsing.
- The `from_utc` field is the UNTIL value (when this transition ends).
- Metadata (`country_code`, `latitude`, etc.) is added later from `zone1970.tab`.
- All time zones are now under the `"timezones"` key, and all rules under `"rules"` for clarity and normalization.

#### 5. Summary

Each line in the zone block becomes a `Transition` in the `Zone.rules` list. The zone itself is created once, and metadata is attached later. The output is grouped under `"timezones"` and `"rules"` in the JSON for easy, language-agnostic use.

#### 4. Notes

- The `abbr` field is `"LMT"` or `"%z"` (which means the abbreviation is determined by rules).
- The `rule` field (e.g., `"RussiaAsia"`, `"EUAsia"`, `"Azer"`) is used to look up DST rules, which can affect `is_dst` and `abbr` if you implement full rule parsing.
- The `from_utc` field is the UNTIL value (when this transition ends).
- Metadata (`country_code`, `latitude`, etc.) is added later from `zone1970.tab`.

#### 5. Summary 

Each line in the zone block becomes a `Transition` in the `Zone.rules` list. The zone itself is created once, and metadata is attached later.

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

## Resources

- [IANA Time Zone Database](https://www.iana.org/time-zones)
- [tzdata Format Documentation](https://data.iana.org/time-zones/theory.html)

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License


[MIT License](LICENSE.md)