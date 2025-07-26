"""
Quick verification script to check if tzkit output looks correct.
Run this after running make_tz_bundle.py to validate the results.
"""

import json
import sqlite3
import os
from pathlib import Path

def verify_tzkit_output():
    """Verify that tzkit generated reasonable output files."""
    
    print("🔍 Verifying tzkit output...")
    print("=" * 50)
    
    # Check if output files exist
    json_file = Path("tzdata/combined.json")
    sqlite_file = Path("tzdata/combined.sqlite")
    
    if not json_file.exists():
        print("❌ combined.json not found!")
        return False
        
    if not sqlite_file.exists():
        print("❌ combined.sqlite not found!")
        return False
    
    print("✅ Both output files exist")
    
    # Verify JSON structure
    print("\n📄 Checking JSON file...")
    try:
        with open(json_file) as f:
            data = json.load(f)
        
        # Check version
        version = data.get("_version", "unknown")
        print(f"   Version: {version}")
        
        # Remove version key to count actual zones
        zones = {k: v for k, v in data.items() if k != "_version"}
        print(f"   Zones: {len(zones)}")
        
        # Check some well-known zones
        expected_zones = [
            "America/New_York",
            "Europe/London", 
            "Asia/Tokyo",
            "Australia/Sydney",
            "America/Los_Angeles"
        ]
        
        missing_zones = []
        for zone in expected_zones:
            if zone not in zones:
                missing_zones.append(zone)
            else:
                zone_data = zones[zone]
                rules_count = len(zone_data.get("rules", []))
                country = zone_data.get("country_code", "?")
                print(f"   ✓ {zone}: {country}, {rules_count} transitions")
        
        if missing_zones:
            print(f"   ⚠️  Missing expected zones: {missing_zones}")
        else:
            print("   ✅ All major zones found")
            
    except Exception as e:
        print(f"   ❌ Error reading JSON: {e}")
        return False
    
    # Verify SQLite structure
    print("\n🗄️  Checking SQLite file...")
    try:
        conn = sqlite3.connect(sqlite_file)
        cur = conn.cursor()
        
        # Check tables exist
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
        
        if "zones" not in tables or "transitions" not in tables:
            print(f"   ❌ Missing tables. Found: {tables}")
            return False
        
        # Count records
        cur.execute("SELECT COUNT(*) FROM zones")
        zone_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM transitions") 
        transition_count = cur.fetchone()[0]
        
        print(f"   Zones table: {zone_count} records")
        print(f"   Transitions table: {transition_count} records")
        
        # Check a few sample zones
        cur.execute("""
            SELECT name, country_code, latitude, longitude 
            FROM zones 
            WHERE name IN ('America/New_York', 'Europe/London', 'Asia/Tokyo')
            ORDER BY name
        """)
        
        sample_zones = cur.fetchall()
        for name, country, lat, lon in sample_zones:
            print(f"   ✓ {name}: {country} at {lat},{lon}")
        
        # Check transitions for one zone
        cur.execute("""
            SELECT COUNT(*), MIN(from_utc), MAX(from_utc)
            FROM transitions 
            WHERE zone_name = 'America/New_York'
        """)
        
        count, min_date, max_date = cur.fetchone()
        print(f"   America/New_York transitions: {count} (from {min_date} to {max_date})")
        
        conn.close()
        print("   ✅ SQLite structure looks good")
        
    except Exception as e:
        print(f"   ❌ Error reading SQLite: {e}")
        return False
    
    # File size checks
    print("\n📊 File sizes:")
    json_size = json_file.stat().st_size
    sqlite_size = sqlite_file.stat().st_size
    
    print(f"   JSON: {json_size:,} bytes ({json_size//1024}KB)")
    print(f"   SQLite: {sqlite_size:,} bytes ({sqlite_size//1024}KB)")
    
    # Reasonable size checks
    if json_size < 100_000:  # Less than 100KB seems too small
        print("   ⚠️  JSON file seems unusually small")
    elif json_size > 10_000_000:  # More than 10MB seems too big
        print("   ⚠️  JSON file seems unusually large")
    else:
        print("   ✅ File sizes look reasonable")
    
    print("\n" + "=" * 50)
    print("✅ Verification complete - output looks good!")
    print("\n💡 To explore your data:")
    print("   - Open combined.json in a text editor")
    print("   - Use SQLite browser to explore the database")
    print("   - Try the sample queries below")
    
    return True

def sample_queries():
    """Show some sample SQL queries to explore the data."""
    
    print("\n🔍 Sample SQL queries to explore your data:")
    print("-" * 45)
    
    queries = [
        ("All zones in Japan", 
         "SELECT * \n "
         "    FROM zones WHERE country_code = 'JP'"),
        ("Zones with most transitions", 
         "SELECT zone_name, COUNT(*) as transitions \n "
         "    FROM transitions GROUP BY zone_name ORDER BY transitions DESC LIMIT 10"),
        ("Recent transitions", 
         "SELECT zone_name, from_utc, offset, abbr \n "
         "    FROM transitions WHERE from_utc LIKE '202%' ORDER BY from_utc DESC LIMIT 10"),
        ("Countries by zone count", 
         "SELECT country_code, COUNT(*) as zone_count \n "
         "    FROM zones WHERE country_code != '' GROUP BY country_code ORDER BY zone_count DESC LIMIT 10"),
    ]
    
    for description, query in queries:
        print(f"\n{description}:")
        print(f"   {query}")

if __name__ == "__main__":
    success = verify_tzkit_output()
    if success:
        sample_queries()
    else:
        print("\n❌ Verification failed - check your tzkit output")