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
```

## 📂 Input Files


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
        "abbr": "KST"
      }
    ],
    "aliases": ["ROK"]
  },
  "_version": "2025b"
}
```

### 💾 SQLite Database (`combined.sqlite`)
Two normalized tables:

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

**Examples**

```sql
-- Get all transitions for Australia/Sydney
SELECT * FROM transitions WHERE zone_name = 'Australia/Sydney';

-- List all countries with more than one time zone
SELECT country_code, COUNT(*) FROM zones GROUP BY country_code HAVING COUNT(*) > 1;
```


## How Parsing Works


### Zone Block Example

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

| Line | from_utc (UNTIL)         | offset   | rule        | abbr (FORMAT) | is_dst | to_utc |
|------|--------------------------|----------|-------------|---------------|--------|--------|
| Zone Asia/Baku 3:19:24 - LMT 1924 May 2 | "1924 May 2" | "3:19:24" | "-"         | "LMT"         | False  | None   |
| 3:00 - %z 1957 Mar              | "1957 Mar" | "3:00"    | "-"         | "%z"         | False  | None   |
| 4:00 RussiaAsia %z 1991 Mar 31 2:00s | "1991 Mar 31 2:00s" | "4:00" | "RussiaAsia" | "%z"         | False  | None   |
| 3:00 RussiaAsia %z 1992 Sep lastSun 2:00s | "1992 Sep lastSun 2:00s" | "3:00" | "RussiaAsia" | "%z"         | False  | None   |
| 4:00 - %z 1996                  | "1996"    | "4:00"    | "-"         | "%z"         | False  | None   |
| 4:00 EUAsia %z 1997             | "1997"    | "4:00"    | "EUAsia"    | "%z"         | False  | None   |
| 4:00 Azer %z                    | ""        | "4:00"    | "Azer"      | "%z"         | False  | None   |

Each line becomes:

```python
transition = Transition(
    from_utc="1924 May 2",  # or whatever UNTIL value is present
    to_utc=None,            # (not parsed in this block)
    offset="3:19:24",
    is_dst=False,           # (can be set based on rules, but default False here)
    abbr="LMT"              # or "%z", etc.
)
zone.rules.append(transition)
```
Repeat for each line.

#### 3. Resulting Data Structure

```python
Zone(
    name="Asia/Baku",
    country_code="",      # filled later from zone1970.tab
    latitude="",          # filled later from zone1970.tab
    longitude="",         # filled later from zone1970.tab
    comment="",           # filled later from zone1970.tab
    rules=[
        Transition(from_utc="1924 May 2", offset="3:19:24", is_dst=False, abbr="LMT", to_utc=None),
        Transition(from_utc="1957 Mar", offset="3:00", is_dst=False, abbr="%z", to_utc=None),
        Transition(from_utc="1991 Mar 31 2:00s", offset="4:00", is_dst=False, abbr="%z", to_utc=None),
        Transition(from_utc="1992 Sep lastSun 2:00s", offset="3:00", is_dst=False, abbr="%z", to_utc=None),
        Transition(from_utc="1996", offset="4:00", is_dst=False, abbr="%z", to_utc=None),
        Transition(from_utc="1997", offset="4:00", is_dst=False, abbr="%z", to_utc=None),
        Transition(from_utc="", offset="4:00", is_dst=False, abbr="%z", to_utc=None),
    ],
    aliases=[]
)
```

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