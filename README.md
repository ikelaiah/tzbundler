
# 🌏 tzbundler: IANA Time Zone Database Parser and Bundler

[![Version](https://img.shields.io/badge/version-1.0-blueviolet.svg)](https://github.com/ikelaiah/tzbundler/releases)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![IANA tzdata](https://img.shields.io/badge/IANA-tzdata%202025b-green.svg)](https://www.iana.org/time-zones)

<p align="center">
  <img src="assets/logo-v3-320.png" alt="tzbundler logo" style="max-width:100%; height:auto;">
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
  - [🚀 Quick Start - Just Download!](#-quick-start---just-download)
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
    - [How to Determine DST Status for a Date](#how-to-determine-dst-status-for-a-date)
      - [Step 1: Find the Active Transition](#step-1-find-the-active-transition)
      - [Step 2: Check for DST Rules](#step-2-check-for-dst-rules)
      - [Step 3: Find Applicable Rules for Your Year](#step-3-find-applicable-rules-for-your-year)
      - [Step 4: Calculate Rule Dates](#step-4-calculate-rule-dates)
      - [Step 5: Apply Hemisphere Logic](#step-5-apply-hemisphere-logic)
      - [Step 6: Handle Edge Cases](#step-6-handle-edge-cases)
    - [Example: Australia/Sydney on May 23, 2030](#example-australiasydney-on-may-23-2030)
  - [🗄️ File Structure](#️-file-structure)
  - [🧪 Testing](#-testing)
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
- Anyone who wants a cross-language-compatible tzdata format
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
python run_tzbundler.py
```

This single command will:

1. Fetch the latest IANA tzdata
2. Download Windows timezone mappings from Unicode CLDR
3. Extract and parse all files
4. Generate `combined.json` and `combined.sqlite` in the `tzdata/` folder

## 🚀 Quick Start - Just Download!

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

> **Important:**  
> tzbundler provides raw rule data—**you must calculate DST status yourself** using the rules and transitions.

### How to Determine DST Status for a Date

To determine if DST is active for a specific zone and date (e.g., "Australia/Sydney" on May 23, 2030):

#### Step 1: Find the Active Transition

- Get the **current transition** for your zone (usually the last one in the transitions array)
- This gives you the base UTC offset and rule name

#### Step 2: Check for DST Rules  

- If `rule_name` is `null` or `"-"`: **No DST** (fixed offset zone)
- Otherwise, get the rule set: `tzdata['rules'][rule_name]`

#### Step 3: Find Applicable Rules for Your Year

- Look for rules where: `from_year <= target_year <= to_year`
- You'll typically find **two types**:
  - **DST start rule**: `save` > 0 (e.g., `"1:00"`)
  - **DST end rule**: `save` = 0 (e.g., `"0"`)

#### Step 4: Calculate Rule Dates

Parse the IANA date specifications:

- `"lastSun"` = Last Sunday of the month
- `"Sun>=8"` = First Sunday on or after the 8th
- `"15"` = 15th day of the month

#### Step 5: Apply Hemisphere Logic

- **Northern Hemisphere** (US/Europe): DST typically Mar-Nov
  - `DST active = start_date <= target_date < end_date`
- **Southern Hemisphere** (Australia): DST typically Oct-Apr  
  - `DST active = target_date >= start_date OR target_date < end_date`

#### Step 6: Handle Edge Cases

- **Ambiguous times**: When clocks "fall back", some times occur twice
- **Invalid times**: When clocks "spring forward", some times don't exist  
- **Time suffixes**: `s`=standard, `u`/`g`/`z`=UTC, `w`=wall (default)

### Example: Australia/Sydney on May 23, 2030

```python
# 1. Active transition
transition = tzdata['timezones']['Australia/Sydney']['transitions'][-1]
# Result: offset="+10:00", rule_name="AN"

# 2. Get DST rules
an_rules = tzdata['rules']['AN']

# 3. Find 2030 rules
current_rules = [r for r in an_rules if r['from'] <= '2030' <= r.get('to', '9999')]
# DST ends: Apr Sun>=1 (April 7, 2030)  
# DST starts: Oct Sun>=1 (October 6, 2030)

# 4. Check date
test_date = May 23, 2030
# May 23 is AFTER April 7 (DST end) and BEFORE October 6 (DST start)
# Therefore: DST is NOT active

# 5. Result
is_dst = False
offset = "+10:00"  # Base offset only
abbreviation = "AEST"  # AE%sT with %s="S" for Standard


## 🕐 How to Calculate DST Status (Detailed)

See [How to Calculate DST Status](docs/how-to-calculate-dst-status.md)

## ❓ How Parsing Works (Detailed)

See [How Parsing Works](docs/how-parsing-works.md)

### Data Processing Flow

```txt
Raw tzdata files → Parse zones/rules/links → Enrich with metadata → Add Windows mappings → Output JSON/SQLite
```

## 🗄️ File Structure

```txt
assets/                 # Project assets (e.g., logos)
docs/                   # Documentation
example/                # Example data and usage
tests/                  # Unified and supporting test scripts
├── test_tzbundler.py   # Unified test suite for all outputs
└── test_windowsZones.py
tzbundler/              # Main package source code
├── __init__.py
├── get_latest_tz.py
└── make_tz_bundle.py
tzdata/                 # Processed output
├── combined.json
└── combined.sqlite
tzdata_raw/             # Downloaded raw IANA and CLDR files
CHANGELOG.md            # Release notes
CONTRIBUTING.md         # Contribution guidelines
LICENSE                 # License file
README.md               # Project documentation
requirements.txt        # Python dependencies
run_tests.py            # Entry point to run all tests
run_tzbundler.py        # Main script to generate tzdata bundles
setup.py                # Package setup
```

## 🧪 Testing

You can run all tests in two ways:

**With pytest (recommended for CI and automation):**

```bash
pytest tests/test_tzbundler.py
```

**Or using the provided entry point script:**

```bash
python run_tests.py
```

This will run all major tests (JSON, SQLite, consistency, and structure) and print a summary.

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
python run_tzbundler.py
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

---

**Built with ❤️ for developers who need reliable timezone data**