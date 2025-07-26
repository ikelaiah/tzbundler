
# 🌏 tzbundler: IANA Time Zone Database Parser and Bundler

[![Version](https://img.shields.io/badge/version-1.0-blueviolet.svg)](https://github.com/ikelaiah/tzbundler/releases)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![IANA tzdata](https://img.shields.io/badge/IANA-tzdata%202025b-green.svg)](https://www.iana.org/time-zones)

<p align="center">
  <img src="assets/logo-v3.png" alt="tzbundler logo" style="max-height:256px;">
</p>


**Version: 1.0**

A Python tool that parses IANA tzdata files and converts them into machine-readable formats (JSON and SQLite). Perfect for applications, research, or data analysis involving time zones. Includes Windows timezone mappings for cross-platform compatibility.

Or you can simply use the pre-generated bundle from `tzdata/` folder or [the Releases page](https://github.com/ikelaiah/tzbundler/releases).
## 🗂️ Table of Contents

- [🌏 tzbundler: IANA Time Zone Database Parser and Bundler](#-tzbundler-iana-time-zone-database-parser-and-bundler)
  - [🗂️ Table of Contents](#️-table-of-contents)
  - [🎯 Who Should Use tzbundler?](#-who-should-use-tzbundler)
  - [✨ Features](#-features)
  - [🚀 Quick Start](#-quick-start)
  - [🚀 Quick Start - Alternative](#-quick-start---alternative)
  - [📊 Data Model](#-data-model)
    - [Zone](#zone)
    - [🔄 Transition](#-transition)
    - [📏 Rule](#-rule)
  - [📁 Input Files](#-input-files)
  - [📤 Output Files](#-output-files)
    - [📝 JSON Format (`combined.json`)](#-json-format-combinedjson)
    - [💾 SQLite Database (`combined.sqlite`)](#-sqlite-database-combinedsqlite)
      - [zones](#zones)
      - [transitions](#transitions)
      - [rules](#rules)
      - [windows\_mapping](#windows_mapping)
  - [🪟 Windows Timezone Support](#-windows-timezone-support)
    - [Example Usage](#example-usage)
    - [SQL Query Examples for Windows Mappings](#sql-query-examples-for-windows-mappings)
  - [❓ How to Use the Rules (DST Logic)](#-how-to-use-the-rules-dst-logic)
    - [Pseudocode Example](#pseudocode-example)
    - [Language-Agnostic Output](#language-agnostic-output)
    - [Additional SQL Query Examples](#additional-sql-query-examples)
  - [❓ How Parsing Works](#-how-parsing-works)
    - [Zone Block Example (from tzdata source)](#zone-block-example-from-tzdata-source)
      - [1. Zone Block Structure](#1-zone-block-structure)
      - [2. Parsing Steps](#2-parsing-steps)
      - [3. Output Structure (JSON)](#3-output-structure-json)
      - [4. Notes](#4-notes)
      - [5. Summary](#5-summary)
    - [Data Processing Flow](#data-processing-flow)
  - [🗄️ File Structure](#️-file-structure)
  - [💡 Use Cases](#-use-cases)
  - [📦 Installation \& Requirements](#-installation--requirements)
  - [⚙️ Important Design Decision](#️-important-design-decision)
  - [🛡️ Error Handling and Robustness](#️-error-handling-and-robustness)
  - [🔗 Resources](#-resources)
  - [🤝 Contributing](#-contributing)
  - [📝 License](#-license)

## 🎯 Who Should Use tzbundler?

- App developers who need reliable time zone handling
- Researchers working on temporal/historical datasets
- Anyone who wants a cross-language-compatible tzdata format (e.g. for Python, Free Pascal, JS)
- Developers needing Windows timezone compatibility

## ✨ Features

- **Simple one-command operation**: Just run `python make_tz_bundle.py`
- **Multiple output formats**: JSON and SQLite database
- **Complete data extraction**: Zones, transitions, rules, and aliases
- **Windows timezone support**: Official Windows timezone mappings from Unicode CLDR
- **Rich metadata**: Country codes, coordinates, and comments
- **Version tracking**: Automatically includes tzdata version info
- **Consumer-driven DST logic**: Raw rule data provided for flexible DST calculations

## 🚀 Quick Start

```bash
python make_tz_bundle.py
```

This single command will:

1. Fetch the latest IANA tzdata
2. Download Windows timezone mappings from Unicode CLDR
3. Extract and parse all files
4. Generate `combined.json` and `combined.sqlite` in the `tzdata/` folder

## 🚀 Quick Start - Alternative

Use the pre-generated `.json` or `.sqlite` bundle from `tzdata/` folder or [the Releases page](https://github.com/ikelaiah/tzbundler/releases).

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
    win_names: List[str]            # Windows timezone names
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
| **Windows Mappings** | `windowsZones.xml` | Windows-IANA timezone mappings from Unicode CLDR |

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
      "aliases": ["ROK"],
      "win_names": ["Korea Standard Time"]
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
  "windows_mapping": {
    "Korea Standard Time": ["Asia/Seoul"]
  },
  "_version": "2025b"
}
```

### 💾 SQLite Database (`combined.sqlite`)

Four normalized tables:

#### zones

- `name` (TEXT PRIMARY KEY)
- `country_code` (TEXT)
- `latitude` (TEXT)
- `longitude` (TEXT)
- `comment` (TEXT)

#### transitions  

- `zone_name` (TEXT)
- `from_utc` (TEXT)
- `to_utc` (TEXT)
- `offset` (TEXT)
- `abbr` (TEXT)
- `rule_name` (TEXT)

#### rules

- `rule_name` (TEXT)
- `from_year` (TEXT)
- `to_year` (TEXT)
- `type` (TEXT)
- `in_month` (TEXT)
- `on_day` (TEXT)
- `at_time` (TEXT)
- `save` (TEXT)
- `letter` (TEXT)

#### windows_mapping

- `windows_name` (TEXT) - Windows timezone name
- `iana_name` (TEXT) - IANA timezone name

## 🪟 Windows Timezone Support

tzbundler includes official Windows timezone mappings from the Unicode CLDR project:

- **Bidirectional mappings**: IANA ↔ Windows timezone names
- **Authoritative source**: Uses the official Unicode CLDR windowsZones.xml
- **Cross-platform compatibility**: Perfect for applications that need to work with both IANA and Windows timezones

### Example Usage

```python
# Find Windows name for IANA timezone
asia_seoul_windows = timezones["Asia/Seoul"]["win_names"]  # ["Korea Standard Time"]

# Find IANA zones for Windows timezone
korea_iana_zones = windows_mapping["Korea Standard Time"]  # ["Asia/Seoul"]
```

### SQL Query Examples for Windows Mappings

```sql
-- Find Windows timezone name for an IANA zone
SELECT z.name, wm.windows_name 
FROM zones z 
JOIN windows_mapping wm ON z.name = wm.iana_name 
WHERE z.name = 'Asia/Seoul';

-- List all Windows timezones and their IANA equivalents
SELECT windows_name, GROUP_CONCAT(iana_name, ', ') as iana_zones
FROM windows_mapping 
GROUP BY windows_name;

-- Find zones that have Windows mappings
SELECT z.name, z.country_code 
FROM zones z 
WHERE EXISTS (SELECT 1 FROM windows_mapping wm WHERE wm.iana_name = z.name);
```

## ❓ How to Use the Rules (DST Logic)

> [!Important] 
> **tzbundler provides raw rule data - DST calculations are your responsibility**.

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

### Additional SQL Query Examples

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

## ❓ How Parsing Works

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
      "aliases": [],
      "win_names": ["Azerbaijan Standard Time"]
    }
  },
  "rules": {
    "RussiaAsia": [ ... ],
    "EUAsia": [ ... ],
    "Azer": [ ... ]
  },
  "windows_mapping": {
    "Azerbaijan Standard Time": ["Asia/Baku"]
  },
  "_version": "2025b"
}
```

#### 4. Notes

- The `abbr` field is `"LMT"` or `"%z"` (which means the abbreviation is determined by rules).
- The `rule_name` field (e.g., `"RussiaAsia"`, `"EUAsia"`, `"Azer"`) is used to look up DST rules.
- The `from_utc` field is the UNTIL value (when this transition ends).
- Metadata (`country_code`, `latitude`, etc.) is added later from `zone1970.tab`.
- Windows timezone names are added from the Unicode CLDR mappings.
- **DST calculations are left to consumers** using the rules data.

#### 5. Summary

Each line in the zone block becomes a `Transition` in the `Zone.transitions` list. The zone itself is created once, and metadata is attached later. DST status must be calculated by consumers using the provided rules.

### Data Processing Flow

```txt
Raw tzdata files → Parse zones/rules/links → Enrich with metadata → Add Windows mappings → Output JSON/SQLite
```

## 🗄️ File Structure

```txt
tzdata_raw/         # Downloaded raw files
├── africa          # African timezone data
├── asia            # Asian timezone data
├── europe          # European timezone data
├── ...             # Other region files
├── zone1970.tab    # Metadata
├── version         # tzdata version
└── windowsZones.xml # Windows timezone mappings
tzdata/             # Processed output
├── combined.json
└── combined.sqlite  
```

## 💡 Use Cases

- **Cross-Platform Applications**: Handle both IANA and Windows timezone identifiers
- **Data Analysis**: Research time zone changes and patterns  
- **Historical Analysis**: Track offset changes over time
- **Compliance**: Ensure accurate time zone handling
- **Custom DST Logic**: Implement domain-specific DST calculations
- **Migration Projects**: Convert between Windows and IANA timezone systems

## 📦 Installation & Requirements

```python
# Required Python packages
requests>=2.25.0    # For downloading tzdata and Windows mappings
```

Clone and run:

```bash
git clone https://github.com/ikelaiah/tzbundler.git
cd tzbundler
pip install -r requirements.txt
python make_tz_bundle.py
```

## ⚙️ Important Design Decision

**tzbundler does not pre-calculate DST status.** Instead, it provides:

- ✅ Raw transition data (offsets, dates, abbreviations)
- ✅ Complete DST rule definitions  
- ✅ Rule names linked to transitions
- ✅ Windows timezone mappings
- ❌ Pre-calculated DST boolean flags

**Why?** This design:

- Avoids bundler bugs affecting DST calculations
- Allows consumers to implement DST logic that fits their needs
- Enables caching and on-demand DST computation
- Keeps complex temporal logic out of the data extraction layer
- Provides maximum flexibility for cross-platform compatibility

## 🛡️ Error Handling and Robustness

The tool includes comprehensive error handling:

- **Network issues**: Gracefully handles connection failures and provides troubleshooting tips
- **File corruption**: Validates downloaded archives and provides cleanup on failure
- **Parsing errors**: Logs problematic lines but continues processing
- **Missing files**: Warns about missing files but continues with available data
- **Partial downloads**: Detects and handles incomplete downloads

## 🔗 Resources

- [IANA Time Zone Database](https://www.iana.org/time-zones)
- [tzdata Format Documentation](https://data.iana.org/time-zones/theory.html)
- [tzdata Theory File](https://data.iana.org/time-zones/theory.html) (Essential for DST implementation)
- [Unicode CLDR WindowsZones](https://github.com/unicode-org/cldr/blob/main/common/supplemental/windowsZones.xml)

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📝 License

[MIT License](LICENSE.md)