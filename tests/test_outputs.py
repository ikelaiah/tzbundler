"""
Unit tests for verifying the output of tzbundler.
This script checks the generated JSON and SQLite files for correctness.
"""

import json
import sqlite3
import os
import pathlib
import pytest


# Determine project root for consistent tzdata paths
def get_project_root():
    current = pathlib.Path(__file__).resolve()
    if current.parent.name == 'tests':
        # If running from tests/, project root is parent of tests
        return current.parent.parent
    else:
        # Otherwise, use the current file's directory
        return current.parent

# Set up base directory for all file operations
PROJECT_ROOT = get_project_root()

# =============================================================================
# CONFIGURATION - File paths
# =============================================================================

# Filename for the output JSON file
OUTPUT_JSON_FILE = str(PROJECT_ROOT / "tzdata" / "combined.json")

# Filename for the output SQLite file
OUTPUT_SQLITE_FILE = str(PROJECT_ROOT / "tzdata" / "combined.sqlite")


# ===================== CI/pytest test functions =====================
def test_output_files_exist():
    assert pathlib.Path(OUTPUT_JSON_FILE).exists(), "combined.json not found!"
    assert pathlib.Path(OUTPUT_SQLITE_FILE).exists(), "combined.sqlite not found!"

def test_json_structure():
    with open(OUTPUT_JSON_FILE) as f:
        data = json.load(f)
    # Top-level keys
    assert "timezones" in data, "Missing 'timezones' key in JSON"
    assert "rules" in data, "Missing 'rules' key in JSON"
    assert "windows_mapping" in data, "Missing 'windows_mapping' key in JSON"
    assert "_version" in data, "Missing '_version' key in JSON"
    # Timezones
    timezones = data["timezones"]
    assert len(timezones) > 300, f"Too few timezones: {len(timezones)}"
    # Known zones
    for zone in ["America/New_York", "Europe/London", "Asia/Tokyo", "Australia/Sydney", "America/Los_Angeles"]:
        assert zone in timezones, f"Missing expected zone: {zone}"
    # Sample zone structure
    sydney = timezones["Australia/Sydney"]
    for field in ["country_code", "coordinates", "comment", "transitions", "aliases", "win_names"]:
        assert field in sydney, f"Missing field '{field}' in Australia/Sydney"
    # Transition structure
    assert sydney["transitions"], "Australia/Sydney has no transitions"
    transition = sydney["transitions"][0]
    for field in ["from_utc", "to_utc", "offset", "abbr", "rule_name"]:
        assert field in transition, f"Missing field '{field}' in transition"

def test_json_windows_mappings():
    with open(OUTPUT_JSON_FILE) as f:
        data = json.load(f)
    windows_mapping = data["windows_mapping"]
    assert len(windows_mapping) > 50, f"Too few Windows mappings: {len(windows_mapping)}"
    assert "Korea Standard Time" in windows_mapping, "Missing Korea Standard Time"
    assert "Asia/Seoul" in windows_mapping["Korea Standard Time"], "Korea Standard Time should map to Asia/Seoul"
    seoul = data["timezones"].get("Asia/Seoul", {})
    win_names = seoul.get("win_names", [])
    assert "Korea Standard Time" in win_names, "Asia/Seoul should have Korea Standard Time in win_names"

def test_json_rules():
    with open(OUTPUT_JSON_FILE) as f:
        data = json.load(f)
    rules = data["rules"]
    assert len(rules) > 10, f"Too few rule sets: {len(rules)}"
    assert "US" in rules, "Missing US rule set"
    us_rules = rules["US"]
    assert us_rules, "US rules should not be empty"
    rule = us_rules[0]
    for field in ["from", "to", "type", "in", "on", "at", "save", "letter"]:
        assert field in rule, f"Missing field '{field}' in rule"

def test_sqlite_structure():
    conn = sqlite3.connect(OUTPUT_SQLITE_FILE)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]
    for t in ["zones", "transitions", "rules", "windows_mapping"]:
        assert t in tables, f"Missing table: {t}. Found: {tables}"
    # Count records
    cur.execute("SELECT COUNT(*) FROM zones")
    zone_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM transitions")
    transition_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM rules")
    rules_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM windows_mapping")
    windows_count = cur.fetchone()[0]
    assert zone_count >= 400, f"Zone count seems low: {zone_count}"
    assert transition_count >= zone_count, f"Transition count seems low: {transition_count}"
    assert windows_count >= 50, f"Windows mapping count seems low: {windows_count}"
    # Sample zones
    cur.execute("""
        SELECT name, country_code, latitude, longitude 
        FROM zones 
        WHERE name IN ('America/New_York', 'Europe/London', 'Asia/Tokyo')
        ORDER BY name
    """)
    sample_zones = cur.fetchall()
    assert sample_zones, "Sample zones not found in SQLite"
    # Transitions for one zone
    cur.execute("""
        SELECT COUNT(*), MIN(from_utc), MAX(from_utc)
        FROM transitions 
        WHERE zone_name = 'America/New_York'
    """)
    count, min_date, max_date = cur.fetchone()
    assert count > 0, "No transitions for America/New_York"
    # Windows mapping
    cur.execute("""
        SELECT COUNT(*) FROM windows_mapping 
        WHERE windows_name = 'Korea Standard Time'
    """)
    korea_mappings = cur.fetchone()[0]
    assert korea_mappings > 0, "No Korea Standard Time mappings in SQLite"
    conn.close()

def test_file_sizes():
    json_size = pathlib.Path(OUTPUT_JSON_FILE).stat().st_size
    sqlite_size = pathlib.Path(OUTPUT_SQLITE_FILE).stat().st_size
    assert json_size >= 100_000, f"JSON file seems unusually small: {json_size} bytes"
    assert json_size <= 10_000_000, f"JSON file seems unusually large: {json_size} bytes"
    assert sqlite_size > 0, "SQLite file is empty"


# =============================================================================
# SCRIPT ENTRY POINT - Allow running this file directly
# =============================================================================

if __name__ == "__main__":
    # Run tests manually if pytest not available
    try:
        test_output_files_exist()
        print("✅ Output files exist test passed")
    except Exception as e:
        print(f"❌ Output files exist test failed: {e}")

    try:
        test_json_structure()
        print("✅ JSON structure test passed")
    except Exception as e:
        print(f"❌ JSON structure test failed: {e}")

    try:
        test_json_windows_mappings()
        print("✅ JSON windows mappings test passed")
    except Exception as e:
        print(f"❌ JSON windows mappings test failed: {e}")

    try:
        test_json_rules()
        print("✅ JSON rules test passed")
    except Exception as e:
        print(f"❌ JSON rules test failed: {e}")

    try:
        test_sqlite_structure()
        print("✅ SQLite structure test passed")
    except Exception as e:
        print(f"❌ SQLite structure test failed: {e}")

    try:
        test_file_sizes()
        print("✅ File sizes test passed")
    except Exception as e:
        print(f"❌ File sizes test failed: {e}")