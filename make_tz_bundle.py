"""
tzkit: IANA Time Zone Database Parser & Bundle Tool

This tool downloads, parses, and converts IANA tzdata files into JSON and SQLite formats.

IANA tzdata files contain complex time zone information in a custom text format:
- Zone blocks: Define time zones and their historical changes
- Rule lines: Define daylight saving time rules  
- Link lines: Define aliases (alternative names for zones)

This tool converts all that into easy-to-use structured data.

Usage: python make_tz_bundle.py

Output:
- tzdata/combined.json: All zones with metadata and transitions
- tzdata/combined.sqlite: Normalized database tables

Note: DST (daylight saving time) status is not calculated during bundling.
Consumers should use the provided rules data to determine DST status as needed.
"""

import logging
import pathlib
import sqlite3
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import sys
from get_latest_tz import get_latest_tz_data


# =============================================================================
# DATA CLASSES - Define the structure of our parsed time zone data
# =============================================================================

@dataclass
class Transition:
    """
    Represents a single period in a time zone's history.
    
    For example, if a zone changed from UTC+8 to UTC+9 in 1988,
    that would be one transition.
    
    Note: DST status is not included - consumers should use the 
    top-level rules data to calculate DST as needed.
    """
    from_utc: str           # When this period starts (e.g., "1988 May 8")
    to_utc: Optional[str]   # When this period ends (None if ongoing)
    offset: str             # UTC offset during this period (e.g., "+09:00")
    abbr: str              # Time zone abbreviation (e.g., "JST", "KST")

@dataclass
class Zone:
    """
    Represents a complete time zone with all its historical data.
    
    Contains metadata (country, coordinates) plus a list of all
    transitions (offset changes) throughout history.
    """
    name: str                           # Zone name (e.g., "Asia/Seoul")
    country_code: str = ""              # ISO country code (e.g., "KR")
    latitude: str = ""                  # Latitude from coordinates
    longitude: str = ""                 # Longitude from coordinates
    comment: str = ""                   # Optional description
    rules: List[Transition] = field(default_factory=list)  # Historical transitions
    aliases: List[str] = field(default_factory=list)       # Alternative names


# =============================================================================
# PARSING FUNCTIONS - Convert raw tzdata files into our data structures
# =============================================================================

def parse_zone_files(input_dir: pathlib.Path):
    """
    Parse all the main tzdata files to extract zones, rules, and links.
    
    IANA tzdata is split across multiple files by region:
    - africa, asia, europe, etc.: Main zone data
    - backward, backzone: Compatibility and deprecated zones
    - etcetera: Special zones like UTC, GMT
    
    Each file can contain:
    - Zone blocks: Define time zones and their transitions
    - Rule lines: Define daylight saving time rules
    - Link lines: Define aliases (USA/Eastern -> America/New_York)
    
    Args:
        input_dir: Directory containing extracted tzdata files
        
    Returns:
        Dictionary mapping zone names to Zone objects
    """
    # These are all the main tzdata files we need to process
    zone_files = [
        "africa", "antarctica", "asia", "australasia", "europe",
        "northamerica", "southamerica", "etcetera", "backward", "backzone"
    ]
    
    zones: Dict[str, Zone] = {}     # Will store all parsed zones
    rules: Dict[str, list] = {}     # Store DST rules: name -> list of rule dicts
    links: Dict[str, str] = {}      # Store aliases: alias_name -> target_zone

    def parse_zone_line(parts):
        """
        Parse a Zone line from tzdata.
        
        Zone lines look like:
        Zone  Asia/Seoul  8:30  -  KST  1948 Aug 15
        
        Format: Zone ZONENAME OFFSET RULES FORMAT [UNTIL]
        - ZONENAME: The time zone name
        - OFFSET: UTC offset (e.g., "8:30" means UTC+8:30)
        - RULES: DST rule name or "-" for no DST
        - FORMAT: Abbreviation format (e.g., "KST" or "%z")
        - UNTIL: When this rule ends (optional)
        """
        name = parts[1]         # Zone name (e.g., "Asia/Seoul")
        offset = parts[2]       # UTC offset (e.g., "8:30")
        rule = parts[3]         # Rule name or "-"
        abbr = parts[4]         # Abbreviation format
        # UNTIL date is everything after the format field
        from_utc = None
        if len(parts) > 5:
            from_utc = " ".join(parts[5:])  # Join remaining parts
        # Store the rule name in the transition for later linking
        transition = Transition(
            from_utc=from_utc or "",  # Empty string if no UNTIL date
            to_utc=None,              # Will be calculated later if needed
            offset=offset,
            abbr=abbr
        )
        # Attach rule name for later linking (not in dataclass, so add as attribute)
        transition.rule_name = rule
        return name, transition

    def parse_rule_line(parts):
        """
        Parse a Rule line that defines daylight saving time rules.
        
        Rule lines look like:
        Rule  Japan  1948  only  -  Sep  10  0:00  1:00  JDT
        
        Format: Rule NAME FROM TO TYPE IN ON AT SAVE LETTER
        - NAME: Rule name (referenced by Zone lines)
        - FROM/TO: Years this rule applies
        - TYPE: Usually "-" (ignore)
        - IN: Month
        - ON: Day
        - AT: Time of day
        - SAVE: Time to add/subtract
        - LETTER: Letter to use in abbreviation
        
        Note: This is stored but not fully processed in this simple version.
        """
        name = parts[1]  # Rule name
        rule = {
            "from": parts[2],     # Start year
            "to": parts[3],       # End year  
            "type": parts[4],     # Type (usually "-")
            "in": parts[5],       # Month
            "on": parts[6],       # Day
            "at": parts[7],       # Time
            "save": parts[8],     # DST offset
            "letter": parts[9] if len(parts) > 9 else ""  # Abbreviation letter
        }
        # Store rule under its name
        if name not in rules:
            rules[name] = []
        rules[name].append(rule)

    # Process each tzdata file
    for fname in zone_files:
        fpath = input_dir / fname
        if not fpath.exists():
            logging.warning(f"Missing file: {fpath}")
            continue
            
        logging.info(f"Processing {fname}...")
        
        with fpath.open(encoding="utf-8") as f:
            current_zone = None  # Track which zone we're parsing transitions for
            
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                    
                parts = line.split()
                if not parts:
                    continue
                
                try:
                    if parts[0] == "Zone":
                        # New zone definition
                        name, transition = parse_zone_line(parts)
                        current_zone = name
                        
                        # Create zone if it doesn't exist
                        if name not in zones:
                            zones[name] = Zone(name=name)
                        
                        # Add the first transition
                        zones[name].rules.append(transition)
                        
                    elif parts[0] == "Rule":
                        # DST rule definition
                        parse_rule_line(parts)
                        
                    elif parts[0] == "Link" and len(parts) >= 3:
                        # Alias definition: Link TARGET ALIAS
                        target = parts[1]   # The real zone name
                        alias = parts[2]    # The alternative name
                        links[alias] = target
                        
                    elif parts[0] not in ["Zone", "Rule", "Link"] and current_zone:
                        # This is a continuation line for the current zone
                        # Format is the same as Zone line but without "Zone" keyword
                        # Add "Zone" and current zone name to reuse parse_zone_line
                        zone_parts = ["Zone", current_zone] + parts
                        name, transition = parse_zone_line(zone_parts)
                        zones[name].rules.append(transition)
                        
                except Exception as e:
                    logging.warning(f"Error parsing {fname}:{line_num}: {line[:50]}... - {e}")

    # Attach aliases to their target zones
    logging.info(f"Processing {len(links)} aliases...")
    for alias, target in links.items():
        if target in zones:
            zones[target].aliases.append(alias)
        else:
            # Target zone not found - create a minimal zone entry
            # This can happen with some edge cases in tzdata
            logging.warning(f"Alias {alias} -> {target}, but {target} not found. Creating minimal zone.")
            zones[target] = Zone(name=target, aliases=[alias])

    logging.info(f"Parsed {len(zones)} zones total")
    return zones, rules


def parse_zone1970_tab(input_dir: pathlib.Path) -> Dict[str, Dict]:
    """
    Parse zone1970.tab to get metadata for each time zone.
    
    This file contains tab-separated data like:
    AD	+4230+00131	Europe/Andorra
    AE	+2518+05518	Asia/Dubai
    AF	+3431+06912	Asia/Kabul
    
    Format: COUNTRY_CODE COORDINATES ZONE_NAME [COMMENT]
    - COUNTRY_CODE: ISO 3166 country code
    - COORDINATES: Latitude+longitude in ±DDMM±DDDMM format
    - ZONE_NAME: Time zone name
    - COMMENT: Optional description
    
    Args:
        input_dir: Directory containing zone1970.tab
        
    Returns:
        Dictionary mapping zone names to metadata dictionaries
    """
    tab_path = input_dir / "zone1970.tab"
    metadata = {}
    
    if not tab_path.exists():
        logging.warning(f"Missing zone1970.tab: {tab_path}")
        return metadata
    
    logging.info("Parsing zone1970.tab for metadata...")
    
    with tab_path.open(encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            # Skip comments and empty lines
            if line.startswith("#") or not line.strip():
                continue
                
            # Split on tabs
            parts = line.strip().split("\t")
            if len(parts) < 3:
                logging.warning(f"Invalid line in zone1970.tab:{line_num}: {line.strip()}")
                continue
                
            country_code = parts[0]     # e.g., "KR"
            coords = parts[1]           # e.g., "+3733+12658"
            tzid = parts[2]             # e.g., "Asia/Seoul"
            comment = parts[3] if len(parts) > 3 else ""  # Optional comment
            
            metadata[tzid] = {
                "country_code": country_code,
                "coordinates": coords,
                "comment": comment
            }
    
    logging.info(f"Found metadata for {len(metadata)} zones")
    return metadata


def parse_version(input_dir: pathlib.Path) -> str:
    """
    Read the tzdata version from the version file.
    
    The version file contains a single line like "2025a" indicating
    the tzdata release version.
    
    Args:
        input_dir: Directory containing version file
        
    Returns:
        Version string (e.g., "2025a") or "unknown" if file missing
    """
    version_path = input_dir / "version"
    if version_path.exists():
        version = version_path.read_text().strip()
        logging.info(f"Found tzdata version: {version}")
        return version
    else:
        logging.warning("No version file found")
        return "unknown"


def merge_rules_and_metadata(zones: Dict[str, Zone], metadata: Dict[str, Dict], rules: Dict[str, list]) -> Dict[str, Zone]:
    """
    Enhance zone objects with metadata from zone1970.tab.
    
    This adds country codes, coordinates, and comments to each zone.
    The coordinates are parsed into separate latitude and longitude.
    
    Args:
        zones: Dictionary of parsed zones
        metadata: Dictionary of metadata from zone1970.tab
        
    Returns:
        Updated zones dictionary with metadata merged in
    """
    logging.info("Merging metadata with zones...")
    
    metadata_found = 0
    for name, zone in zones.items():
        meta = metadata.get(name)
        if meta:
            metadata_found += 1
            zone.country_code = meta["country_code"]
            zone.comment = meta["comment"]
            # Parse coordinates from format like "+3733+12658"
            coords = meta["coordinates"]
            if coords and len(coords) >= 4:
                mid = len(coords) // 2
                zone.latitude = coords[:mid]
                zone.longitude = coords[mid:]
        # For each transition, attach the rule name if present and not "-"
        for t in zone.rules:
            rule_name = getattr(t, "rule_name", None)
            if rule_name and rule_name != "-":
                t.rule_name = rule_name
            else:
                t.rule_name = None
    logging.info(f"Added metadata to {metadata_found}/{len(zones)} zones")
    return zones


# =============================================================================
# OUTPUT FUNCTIONS - Write parsed data to JSON and SQLite formats
# =============================================================================

def write_combined_json(zones: Dict[str, Zone], rules: Dict[str, list], version: str, output_path: pathlib.Path):
    """
    Write all zone data to a combined JSON file.
    
    The JSON structure separates raw transition data from DST rules:
    {
      "timezones": {
        "Asia/Seoul": {
          "country_code": "KR",
          "coordinates": "+3733+12658",
          "comment": "",
          "rules": [ { transition objects } ],
          "aliases": [ "ROK" ]
        }
      },
      "rules": {
        "US": [ { rule objects } ]
      },
      "_version": "2025a"
    }
    
    Consumers should use the rules data to determine DST status rather
    than relying on precalculated DST information in transitions.
    
    Args:
        zones: Dictionary of all parsed zones
        rules: Dictionary of all DST rules
        version: tzdata version string
        output_path: Where to write the JSON file
    """
    logging.info("Writing JSON output...")
    
    # Build the output dictionary with 'timezones' and 'rules' at the root
    out = {
        "timezones": {},
        "rules": rules,
        "_version": version
    }
    for name, zone in zones.items():
        out["timezones"][name] = {
            "country_code": zone.country_code,
            "coordinates": f"{zone.latitude}{zone.longitude}",
            "comment": zone.comment,
            "rules": [
                {**t.__dict__, "rule_name": getattr(t, "rule_name", None)} for t in zone.rules
            ],
            "aliases": zone.aliases
        }
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    logging.info(f"Wrote JSON with {len(zones)} zones and {len(rules)} rule sets to: {output_path}")


def write_combined_sqlite(zones: Dict[str, Zone], rules: Dict[str, list], version: str, output_path: pathlib.Path):
    """
    Write all zone data to a SQLite database with normalized tables.
    
    Creates three tables:
    - zones: One row per zone with metadata
    - transitions: One row per transition (can be many per zone)
    - rules: One row per DST rule definition
    
    This normalized structure makes it easy to query and analyze the data.
    Consumers should use the rules table to calculate DST status.
    
    Args:
        zones: Dictionary of all parsed zones
        rules: Dictionary of all DST rules
        version: tzdata version string (not stored currently)
        output_path: Where to write the SQLite file
    """
    logging.info("Writing SQLite output...")
    
    # Connect to database (creates file if it doesn't exist)
    conn = sqlite3.connect(str(output_path))
    cur = conn.cursor()
    
    # Create zones table - one row per time zone
    cur.execute("""
        CREATE TABLE IF NOT EXISTS zones (
            name TEXT PRIMARY KEY,          -- Zone name (e.g., "Asia/Seoul")
            country_code TEXT,              -- ISO country code (e.g., "KR")
            latitude TEXT,                  -- Latitude from coordinates
            longitude TEXT,                 -- Longitude from coordinates
            comment TEXT                    -- Optional description
        )
    """)
    # Create transitions table - one row per transition
    # Note: is_dst removed - consumers should calculate from rules
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transitions (
            zone_name TEXT,                 -- References zones.name
            from_utc TEXT,                  -- When this transition starts
            to_utc TEXT,                    -- When this transition ends
            offset TEXT,                    -- UTC offset during this period
            abbr TEXT,                      -- Time zone abbreviation
            rule_name TEXT                  -- Name of DST rule set (nullable)
        )
    """)
    # Create rules table - one row per rule definition
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rules (
            rule_name TEXT,     -- Name of the rule set
            from_year TEXT,
            to_year TEXT,
            type TEXT,
            in_month TEXT,
            on_day TEXT,
            at_time TEXT,
            save TEXT,
            letter TEXT
        )
    """)
    zones_inserted = 0
    transitions_inserted = 0
    rules_inserted = 0
    for name, zone in zones.items():
        cur.execute("INSERT OR REPLACE INTO zones VALUES (?, ?, ?, ?, ?)",
                   (name, zone.country_code, zone.latitude, zone.longitude, zone.comment))
        zones_inserted += 1
        for transition in zone.rules:
            cur.execute("INSERT INTO transitions VALUES (?, ?, ?, ?, ?, ?)",
                       (name, transition.from_utc, transition.to_utc, 
                        transition.offset, transition.abbr, getattr(transition, "rule_name", None)))
            transitions_inserted += 1
    # Insert all rules
    for rule_name, rule_list in rules.items():
        for rule in rule_list:
            cur.execute("INSERT INTO rules VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (rule_name, rule["from"], rule["to"], rule["type"], rule["in"], rule["on"], rule["at"], rule["save"], rule["letter"]))
            rules_inserted += 1
    conn.commit()
    conn.close()
    logging.info(f"Wrote SQLite with {zones_inserted} zones, {transitions_inserted} transitions, and {rules_inserted} rules to: {output_path}")


# =============================================================================
# MAIN FUNCTION - Orchestrate the entire process
# =============================================================================

def main():
    """
    Main function that orchestrates the entire tzdata processing pipeline:
    
    1. Download latest tzdata from IANA
    2. Parse all zone files
    3. Parse metadata
    4. Merge everything together
    5. Write JSON and SQLite outputs
    
    Note: DST calculations are left to consumers who can use the rules data.
    """
    print("tzkit: IANA Time Zone Database Parser")
    print("=====================================")
    
    # Step 1: Download and extract the latest tzdata
    print("1. Downloading latest tzdata from IANA...")
    if not get_latest_tz_data():
        print("❌ Failed to fetch the latest timezone data.")
        print("   Please check your internet connection or the IANA website.")
        sys.exit(1)
    print("✅ Download complete")
    
    # Set up paths
    input_dir = pathlib.Path("tzdata_raw")   # Where extracted files are
    output_dir = pathlib.Path("tzdata")      # Where to put our outputs
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    try:
        # Step 2: Parse version info
        print("2. Reading tzdata version...")
        version = parse_version(input_dir)
        # Step 3: Parse all zone files and rules
        print("3. Parsing zone files and rules...")
        zones, rules = parse_zone_files(input_dir)
        # Step 4: Parse metadata
        print("4. Parsing metadata...")
        metadata = parse_zone1970_tab(input_dir)
        # Step 5: Merge everything together
        print("5. Merging data...")
        zones = merge_rules_and_metadata(zones, metadata, rules)
        # Step 6: Write outputs
        print("6. Writing outputs...")
        write_combined_json(zones, rules, version, output_dir / "combined.json")
        write_combined_sqlite(zones, rules, version, output_dir / "combined.sqlite")
        print(f"✅ Complete! Processed {len(zones)} zones from tzdata {version}")
        print(f"📁 Output files in: {output_dir}")
        print(f"   - combined.json: {(output_dir / 'combined.json').stat().st_size // 1024}KB")
        print(f"   - combined.sqlite: {(output_dir / 'combined.sqlite').stat().st_size // 1024}KB")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        logging.exception("Full error details:")
        sys.exit(1)


if __name__ == "__main__":
    main()