# tests/test_parser.py
"""
Unit tests for the parsing logic in tzbundler
"""

import json
import tempfile
import pathlib
import pytest
import sys
import os


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


# =============================================================================
# TEST FUNCTIONS - Parsing tests
# =============================================================================
def test_json_structure():
    """Test that the JSON output has the correct structure"""
    json_file = pathlib.Path(OUTPUT_JSON_FILE)

    if not json_file.exists():
        pytest.skip("No combined.json found - run make_tz_bundle.py first")
    
    with open(json_file) as f:
        data = json.load(f)
    
    # Test top-level structure
    assert "timezones" in data, "Missing 'timezones' key"
    assert "rules" in data, "Missing 'rules' key"  
    assert "windows_mapping" in data, "Missing 'windows_mapping' key"
    assert "_version" in data, "Missing '_version' key"
    
    # Test timezone structure
    timezones = data["timezones"]
    assert len(timezones) > 300, f"Too few timezones: {len(timezones)}"
    
    # Test a known timezone
    assert "Australia/Sydney" in timezones, "Missing Australia/Sydney"
    sydney = timezones["Australia/Sydney"]
    
    required_fields = ["country_code", "coordinates", "comment", "transitions", "aliases", "win_names"]
    for field in required_fields:
        assert field in sydney, f"Missing field '{field}' in Australia/Sydney"
    
    # Test transition structure
    assert len(sydney["transitions"]) > 0, "Australia/Sydney has no transitions"
    transition = sydney["transitions"][0]
    
    required_transition_fields = ["from_utc", "to_utc", "offset", "abbr", "rule_name"]
    for field in required_transition_fields:
        assert field in transition, f"Missing field '{field}' in transition"


# =============================================================================
# TEST FUNCTION - Windows timezone mappings
# =============================================================================
def test_windows_mappings():
    """Test that Windows timezone mappings are present and valid"""
    json_file = pathlib.Path(OUTPUT_JSON_FILE)

    if not json_file.exists():
        pytest.skip("No combined.json found - run make_tz_bundle.py first")
    
    with open(json_file) as f:
        data = json.load(f)
    
    windows_mapping = data["windows_mapping"]
    
    # Should have some mappings
    assert len(windows_mapping) > 50, f"Too few Windows mappings: {len(windows_mapping)}"
    
    # Test specific known mappings
    assert "Korea Standard Time" in windows_mapping, "Missing Korea Standard Time"
    korea_zones = windows_mapping["Korea Standard Time"]
    assert "Asia/Seoul" in korea_zones, "Korea Standard Time should map to Asia/Seoul"
    
    # Test bidirectional consistency
    timezones = data["timezones"]
    seoul = timezones.get("Asia/Seoul", {})
    win_names = seoul.get("win_names", [])
    assert "Korea Standard Time" in win_names, "Asia/Seoul should have Korea Standard Time in win_names"

# =============================================================================
# TEST FUNCTION - DST rule structure    
# =============================================================================
def test_rule_structure():
    """Test that DST rules are properly structured"""
    json_file = pathlib.Path(OUTPUT_JSON_FILE)

    if not json_file.exists():
        pytest.skip("No combined.json found - run make_tz_bundle.py first")
    
    with open(json_file) as f:
        data = json.load(f)
    
    rules = data["rules"]
    
    # Should have some rules
    assert len(rules) > 10, f"Too few rule sets: {len(rules)}"
    
    # Test a known rule set (US rules should exist)
    assert "US" in rules, "Missing US rule set"
    us_rules = rules["US"]
    
    assert len(us_rules) > 0, "US rules should not be empty"
    
    # Test rule structure
    rule = us_rules[0]
    required_rule_fields = ["from", "to", "type", "in", "on", "at", "save", "letter"]
    for field in required_rule_fields:
        assert field in rule, f"Missing field '{field}' in rule"

# =============================================================================
# SCRIPT ENTRY POINT - Allow running this file directly
# =============================================================================

if __name__ == "__main__":
    # Run tests manually if pytest not available
    try:
        test_json_structure()
        print("✅ JSON structure test passed")
    except Exception as e:
        print(f"❌ JSON structure test failed: {e}")
    
    try:
        test_windows_mappings()
        print("✅ Windows mappings test passed")
    except Exception as e:
        print(f"❌ Windows mappings test failed: {e}")
    
    try:
        test_rule_structure()
        print("✅ Rule structure test passed")
    except Exception as e:
        print(f"❌ Rule structure test failed: {e}")