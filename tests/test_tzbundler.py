"""
Unified test suite for tzbundler output validation.
This script checks the generated JSON and SQLite files for correctness.

Can be run with pytest or standalone:
    pytest tests/test_tzbundler.py
    python tests/test_tzbundler.py
"""

import json
import sqlite3
import pathlib
import pytest


# =============================================================================
# CONFIGURATION - File paths
# =============================================================================

def get_project_root():
    """Get project root directory from test file location"""
    current = pathlib.Path(__file__).resolve()
    if current.parent.name == 'tests':
        return current.parent.parent
    else:
        return current.parent

PROJECT_ROOT = get_project_root()
OUTPUT_JSON_FILE = PROJECT_ROOT / "tzdata" / "combined.json"
OUTPUT_SQLITE_FILE = PROJECT_ROOT / "tzdata" / "combined.sqlite"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_json_data():
    """Load and return JSON data, skip test if file doesn't exist"""
    if not OUTPUT_JSON_FILE.exists():
        pytest.skip(f"No combined.json found at {OUTPUT_JSON_FILE} - run tzbundler first")
    
    with open(OUTPUT_JSON_FILE) as f:
        return json.load(f)

def get_sqlite_connection():
    """Get SQLite connection, skip test if file doesn't exist"""
    if not OUTPUT_SQLITE_FILE.exists():
        pytest.skip(f"No combined.sqlite found at {OUTPUT_SQLITE_FILE} - run tzbundler first")
    
    return sqlite3.connect(OUTPUT_SQLITE_FILE)


# =============================================================================
# FILE EXISTENCE TESTS
# =============================================================================

def test_output_files_exist():
    """Test that both output files were created"""
    assert OUTPUT_JSON_FILE.exists(), f"combined.json not found at {OUTPUT_JSON_FILE}"
    assert OUTPUT_SQLITE_FILE.exists(), f"combined.sqlite not found at {OUTPUT_SQLITE_FILE}"


def test_file_sizes_reasonable():
    """Test that output files have reasonable sizes"""
    json_size = OUTPUT_JSON_FILE.stat().st_size
    sqlite_size = OUTPUT_SQLITE_FILE.stat().st_size
    
    # JSON should be 100KB - 10MB
    assert 100_000 <= json_size <= 10_000_000, f"JSON file size unusual: {json_size:,} bytes"
    
    # SQLite should exist and have some content
    assert sqlite_size > 50_000, f"SQLite file too small: {sqlite_size:,} bytes"


# =============================================================================
# JSON STRUCTURE TESTS
# =============================================================================

def test_json_top_level_structure():
    """Test that JSON has all required top-level keys"""
    data = load_json_data()
    
    required_keys = ["timezones", "rules", "windows_mapping", "_version"]
    for key in required_keys:
        assert key in data, f"Missing top-level key: {key}"
    
    # Check data types
    assert isinstance(data["timezones"], dict), "timezones should be a dict"
    assert isinstance(data["rules"], dict), "rules should be a dict"
    assert isinstance(data["windows_mapping"], dict), "windows_mapping should be a dict"
    assert isinstance(data["_version"], str), "_version should be a string"


def test_json_timezone_counts():
    """Test that we have a reasonable number of timezones"""
    data = load_json_data()
    timezones = data["timezones"]
    
    assert len(timezones) >= 400, f"Too few timezones: {len(timezones)}"
    assert len(timezones) <= 1000, f"Too many timezones: {len(timezones)}"


def test_json_expected_zones_exist():
    """Test that well-known timezones are present"""
    data = load_json_data()
    timezones = data["timezones"]
    
    # Core zones that should definitely exist
    required_zones = [
        "America/New_York",
        "Europe/London", 
        "Asia/Tokyo",
        "Australia/Sydney",
        "America/Los_Angeles"
    ]
    
    # UTC zones - check for common variations
    utc_zones = [
        "UTC",
        "Etc/UTC", 
        "Etc/Universal",
        "Universal"
    ]
    
    # Test required zones
    for zone in required_zones:
        assert zone in timezones, f"Missing required timezone: {zone}"
    
    # Test that at least one UTC variant exists
    utc_found = any(zone in timezones for zone in utc_zones)
    assert utc_found, f"No UTC timezone found. Checked: {utc_zones}. Available UTC-like zones: {[z for z in timezones.keys() if 'UTC' in z or 'Universal' in z]}"


def test_json_timezone_structure():
    """Test that timezone objects have correct structure"""
    data = load_json_data()
    sydney = data["timezones"]["Australia/Sydney"]
    
    required_fields = ["country_code", "coordinates", "comment", "transitions", "aliases", "win_names"]
    for field in required_fields:
        assert field in sydney, f"Missing field '{field}' in Australia/Sydney"
    
    # Check data types
    assert isinstance(sydney["country_code"], str), "country_code should be string"
    assert isinstance(sydney["coordinates"], str), "coordinates should be string"
    assert isinstance(sydney["comment"], str), "comment should be string"
    assert isinstance(sydney["transitions"], list), "transitions should be list"
    assert isinstance(sydney["aliases"], list), "aliases should be list"
    assert isinstance(sydney["win_names"], list), "win_names should be list"


def test_json_transition_structure():
    """Test that transition objects have correct structure"""
    data = load_json_data()
    sydney = data["timezones"]["Australia/Sydney"]
    
    assert len(sydney["transitions"]) > 0, "Australia/Sydney should have transitions"
    
    transition = sydney["transitions"][0]
    required_fields = ["to_utc", "offset", "abbr", "rule_name"]
    for field in required_fields:
        assert field in transition, f"Missing field '{field}' in transition"


# =============================================================================
# WINDOWS MAPPING TESTS
# =============================================================================

def test_json_windows_mappings_exist():
    """Test that Windows timezone mappings are present"""
    data = load_json_data()
    windows_mapping = data["windows_mapping"]
    
    assert len(windows_mapping) >= 50, f"Too few Windows mappings: {len(windows_mapping)}"


def test_json_windows_mapping_bidirectional():
    """Test that Windows mappings are bidirectionally consistent"""
    data = load_json_data()
    windows_mapping = data["windows_mapping"]
    timezones = data["timezones"]
    
    # Test specific known mapping
    assert "Korea Standard Time" in windows_mapping, "Missing Korea Standard Time"
    korea_zones = windows_mapping["Korea Standard Time"]
    assert "Asia/Seoul" in korea_zones, "Korea Standard Time should map to Asia/Seoul"
    
    # Test reverse mapping
    seoul = timezones.get("Asia/Seoul", {})
    win_names = seoul.get("win_names", [])
    assert "Korea Standard Time" in win_names, "Asia/Seoul should have Korea Standard Time in win_names"


# =============================================================================
# RULES TESTS
# =============================================================================

def test_json_rules_exist():
    """Test that DST rules are present"""
    data = load_json_data()
    rules = data["rules"]
    
    assert len(rules) >= 10, f"Too few rule sets: {len(rules)}"


def test_json_rules_structure():
    """Test that rule objects have correct structure"""
    data = load_json_data()
    rules = data["rules"]
    
    # Test known rule set
    assert "US" in rules, "Missing US rule set"
    us_rules = rules["US"]
    assert len(us_rules) > 0, "US rules should not be empty"
    
    # Test rule structure
    rule = us_rules[0]
    required_fields = ["from", "to", "type", "in", "on", "at", "save", "letter"]
    for field in required_fields:
        assert field in rule, f"Missing field '{field}' in rule"


# =============================================================================
# SQLITE TESTS
# =============================================================================

def test_sqlite_tables_exist():
    """Test that all required SQLite tables exist"""
    conn = get_sqlite_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]
    
    required_tables = ["zones", "transitions", "rules", "windows_mapping"]
    for table in required_tables:
        assert table in tables, f"Missing SQLite table: {table}"
    
    conn.close()


def test_sqlite_record_counts():
    """Test that SQLite tables have reasonable record counts"""
    conn = get_sqlite_connection()
    cur = conn.cursor()
    
    # Get record counts
    table_counts = {}
    for table in ["zones", "transitions", "rules", "windows_mapping"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        table_counts[table] = cur.fetchone()[0]
    
    # Sanity checks
    assert table_counts["zones"] >= 400, f"Zone count low: {table_counts['zones']}"
    assert table_counts["transitions"] >= table_counts["zones"], f"Transition count low: {table_counts['transitions']}"
    assert table_counts["rules"] >= 50, f"Rule count low: {table_counts['rules']}"
    assert table_counts["windows_mapping"] >= 50, f"Windows mapping count low: {table_counts['windows_mapping']}"
    
    conn.close()


def test_sqlite_sample_data():
    """Test that SQLite contains expected sample data"""
    conn = get_sqlite_connection()
    cur = conn.cursor()
    
    # Test sample zones
    cur.execute("""
        SELECT name, country_code 
        FROM zones 
        WHERE name IN ('America/New_York', 'Europe/London', 'Asia/Tokyo')
    """)
    sample_zones = cur.fetchall()
    assert len(sample_zones) >= 3, "Missing sample zones in SQLite"
    
    # Test transitions for known zone
    cur.execute("""
        SELECT COUNT(*) FROM transitions 
        WHERE zone_name = 'America/New_York'
    """)
    ny_transitions = cur.fetchone()[0]
    assert ny_transitions > 0, "No transitions for America/New_York in SQLite"
    
    # Test Windows mapping
    cur.execute("""
        SELECT COUNT(*) FROM windows_mapping 
        WHERE windows_name = 'Korea Standard Time'
    """)
    korea_mappings = cur.fetchone()[0]
    assert korea_mappings > 0, "No Korea Standard Time mappings in SQLite"
    
    conn.close()


def test_sqlite_data_consistency():
    """Test that SQLite data is internally consistent"""
    conn = get_sqlite_connection()
    cur = conn.cursor()
    
    # Test that all transitions reference valid zones
    cur.execute("""
        SELECT COUNT(*) FROM transitions t
        LEFT JOIN zones z ON t.zone_name = z.name
        WHERE z.name IS NULL
    """)
    orphan_transitions = cur.fetchone()[0]
    assert orphan_transitions == 0, f"Found {orphan_transitions} transitions with invalid zone references"
    
    # Windows mappings may legitimately reference zones not in the main zone list
    # (deprecated zones, aliases, etc. from Microsoft's comprehensive mapping)
    # This is normal and expected - we just check it's not excessive
    cur.execute("""
        SELECT COUNT(*) FROM windows_mapping w
        LEFT JOIN zones z ON w.iana_name = z.name
        WHERE z.name IS NULL
    """)
    orphan_count = cur.fetchone()[0]
    
    # Get total mappings for context
    cur.execute("SELECT COUNT(*) FROM windows_mapping")
    total_mappings = cur.fetchone()[0]
    
    orphan_percentage = (orphan_count / total_mappings) * 100 if total_mappings > 0 else 0
    
    # Allow up to 30% of mappings to reference zones not in main list (this is normal)
    assert orphan_percentage <= 30, f"Too many Windows mappings reference non-existent zones: {orphan_count}/{total_mappings} ({orphan_percentage:.1f}%). This suggests a data processing issue."
    
    # If there are some orphans, that's expected (show info but don't fail)
    if orphan_count > 0:
        print(f"\n📋 Info: {orphan_count}/{total_mappings} ({orphan_percentage:.1f}%) Windows mappings reference zones not in main zone list.")
        print("   This is normal - Microsoft's mapping includes deprecated/alias zones.")
    
    conn.close()


# =============================================================================
# DATA CONSISTENCY TESTS (JSON vs SQLite)
# =============================================================================

def test_json_sqlite_zone_count_consistency():
    """Test that JSON and SQLite have same number of zones"""
    data = load_json_data()
    conn = get_sqlite_connection()
    
    json_zone_count = len(data["timezones"])
    
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM zones")
    sqlite_zone_count = cur.fetchone()[0]
    
    assert json_zone_count == sqlite_zone_count, f"Zone count mismatch: JSON={json_zone_count}, SQLite={sqlite_zone_count}"
    
    conn.close()


def test_json_sqlite_windows_mapping_consistency():
    """Test that JSON and SQLite have consistent Windows mappings"""
    data = load_json_data()
    conn = get_sqlite_connection()
    
    json_mapping_count = sum(len(zones) for zones in data["windows_mapping"].values())
    
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM windows_mapping")
    sqlite_mapping_count = cur.fetchone()[0]
    
    assert json_mapping_count == sqlite_mapping_count, f"Windows mapping count mismatch: JSON={json_mapping_count}, SQLite={sqlite_mapping_count}"
    
    conn.close()


# =============================================================================
# SCRIPT ENTRY POINT - Manual test runner
# =============================================================================

def run_all_tests():
    """Run all tests manually and report results"""
    test_functions = [
        test_output_files_exist,
        test_file_sizes_reasonable,
        test_json_top_level_structure,
        test_json_timezone_counts,
        test_json_expected_zones_exist,
        test_json_timezone_structure,
        test_json_transition_structure,
        test_json_windows_mappings_exist,
        test_json_windows_mapping_bidirectional,
        test_json_rules_exist,
        test_json_rules_structure,
        test_sqlite_tables_exist,
        test_sqlite_record_counts,
        test_sqlite_sample_data,
        test_sqlite_data_consistency,
        test_json_sqlite_zone_count_consistency,
        test_json_sqlite_windows_mapping_consistency,
    ]
    
    passed = 0
    failed = 0
    
    print("🚀 Running tzbundler test suite...")
    print("=" * 60)
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print(f"💥 {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)