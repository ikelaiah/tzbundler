#!/usr/bin/env python3
"""
Debug script to diagnose Windows timezone mapping issues
"""

import pathlib
import xml.etree.ElementTree as ET

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
LOCAL_WIN_ZONES_FILE = str(PROJECT_ROOT / "tzdata_raw" / "windowsZones.xml")


# =============================================================================
# TEST FUNCTION - Ensuring the downloaded windowsZones.xml file is valid
# =============================================================================

def debug_windows_zones_xml(xml_path: pathlib.Path):
    """
    Debug the windowsZones.xml parsing to see what's going wrong.
    """
    print(f"🔍 Debugging windowsZones.xml at: {xml_path}")
    print(f"📁 File exists: {xml_path.exists()}")
    
    if not xml_path.exists():
        print("❌ File not found!")
        return
        
    print(f"📏 File size: {xml_path.stat().st_size} bytes")
    
    try:
        # Parse the XML
        tree = ET.parse(str(xml_path))
        root = tree.getroot()
        
        print(f"🏷️  Root tag: {root.tag}")
        print(f"🏷️  Root attributes: {root.attrib}")
        
        # Show the XML structure
        print("\n📋 XML Structure:")
        def print_structure(element, indent=0):
            spaces = "  " * indent
            print(f"{spaces}{element.tag} - attrs: {element.attrib}")
            for child in element[:3]:  # Only show first 3 children
                print_structure(child, indent + 1)
            if len(element) > 3:
                print(f"{spaces}  ... and {len(element) - 3} more children")
        
        print_structure(root)
        
        # Look for mapZone elements
        print(f"\n🗺️  Looking for mapZone elements...")
        all_mapzones = root.findall('.//mapZone')
        print(f"📊 Total mapZone elements found: {len(all_mapzones)}")
        
        if all_mapzones:
            print(f"\n📝 First few mapZone elements:")
            for i, mapZone in enumerate(all_mapzones[:5]):
                print(f"  {i+1}. Attributes: {mapZone.attrib}")
        
        # Look specifically for territory='001'
        global_mapzones = root.findall('.//mapZone[@territory="001"]')
        print(f"\n🌍 mapZone elements with territory='001': {len(global_mapzones)}")
        
        if global_mapzones:
            print(f"\n📝 Global mapZone elements:")
            for i, mapZone in enumerate(global_mapzones[:10]):
                other = mapZone.attrib.get('other', 'N/A')
                type_val = mapZone.attrib.get('type', 'N/A')
                print(f"  {i+1}. Windows: '{other}' -> IANA: '{type_val}'")
        else:
            # Maybe territory attribute has different format?
            print("\n🔍 Checking all territory values:")
            territories = set()
            for mapZone in all_mapzones[:20]:
                territory = mapZone.attrib.get('territory')
                if territory:
                    territories.add(territory)
            print(f"📊 Found territories: {sorted(territories)}")
            
            # Show some examples with different territories
            print(f"\n📝 Sample mapZone elements with various territories:")
            for i, mapZone in enumerate(all_mapzones[:10]):
                attrs = mapZone.attrib
                print(f"  {i+1}. {attrs}")
                
    except ET.ParseError as e:
        print(f"❌ XML Parse Error: {e}")
    except Exception as e:
        print(f"❌ General Error: {e}")


# =============================================================================
# TEST FUNCTION - Try a different parsing approach 
# =============================================================================

def test_manual_parsing(xml_path: pathlib.Path):
    """
    Try a different parsing approach to see if we can get the data.
    """
    print(f"\n🔬 Testing manual parsing approach...")
    
    if not xml_path.exists():
        return
        
    try:
        with open(xml_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Look for some expected patterns
        if 'Korea Standard Time' in content:
            print("✅ Found 'Korea Standard Time' in file")
        else:
            print("❌ 'Korea Standard Time' not found in file")
            
        if 'Asia/Seoul' in content:
            print("✅ Found 'Asia/Seoul' in file")  
        else:
            print("❌ 'Asia/Seoul' not found in file")
            
        # Count mapZone occurrences
        mapzone_count = content.count('<mapZone')
        print(f"📊 Found {mapzone_count} <mapZone elements in raw text")
        
        # Look for territory="001"
        territory_001_count = content.count('territory="001"')
        print(f"🌍 Found {territory_001_count} territory=\"001\" in raw text")
        
        # Show a sample of the file
        print(f"\n📄 First 1000 characters of file:")
        print("=" * 50)
        print(content[:1000])
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")

# =============================================================================
# SCRIPT ENTRY POINT - Allow running this file directly
# =============================================================================

if __name__ == "__main__":
    # Test the actual file location
    xml_path = pathlib.Path(LOCAL_WIN_ZONES_FILE)
    
    debug_windows_zones_xml(xml_path)
    test_manual_parsing(xml_path)
    print("\n🔚 Test complete.")