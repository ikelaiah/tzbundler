# Usage Examples

## Python Example

```python
import json
import sqlite3
from datetime import datetime, date

# Load JSON data
with open('tzdata/combined.json', 'r') as f:
    tzdata = json.load(f)

# Example 1: Get all timezones for a country
def get_country_timezones(country_code):
    """Get all timezones for a country code (e.g., 'AU' for Australia)"""
    zones = []
    for name, zone in tzdata['timezones'].items():
        if zone['country_code'] == country_code:
            zones.append({
                'name': name,
                'comment': zone['comment'],
                'offset': zone['transitions'][-1]['offset'] if zone['transitions'] else 'Unknown'
            })
    return sorted(zones, key=lambda x: x['name'])

# Usage
au_zones = get_country_timezones('AU')
for zone in au_zones:
    print(f"{zone['name']:<25} {zone['offset']:<8} {zone['comment']}")

# Example 2: Find Windows timezone mapping
def find_windows_mapping(iana_name):
    """Find Windows timezone name for an IANA timezone"""
    zone = tzdata['timezones'].get(iana_name, {})
    return zone.get('win_names', [])

print(f"Sydney Windows name: {find_windows_mapping('Australia/Sydney')}")

# Example 3: Get current transition info
def get_current_transition(timezone_name):
    """Get the current active transition for a timezone"""
    zone = tzdata['timezones'].get(timezone_name)
    if not zone:
        return None
    
    current = zone['transitions'][-1]  # Last transition is current
    return {
        'offset': current['offset'],
        'abbreviation': current['abbr'],
        'rule_name': current['rule_name'],
        'has_dst': current['rule_name'] is not None and current['rule_name'] != '-'
    }

sydney_info = get_current_transition('Australia/Sydney')
print(f"Sydney: {sydney_info}")
```

## JavaScript Example

```javascript
// Load JSON data (Node.js)
const fs = require('fs');
const tzdata = JSON.parse(fs.readFileSync('tzdata/combined.json', 'utf8'));

// Example: Find all aliases for a timezone
function getTimezoneAliases(timezoneName) {
    const zone = tzdata.timezones[timezoneName];
    return zone ? zone.aliases : [];
}

console.log('Sydney aliases:', getTimezoneAliases('Australia/Sydney'));

// Example: Reverse Windows mapping lookup
function findIanaFromWindows(windowsName) {
    return tzdata.windows_mapping[windowsName] || [];
}

console.log('Korea Standard Time maps to:', 
    findIanaFromWindows('Korea Standard Time'));

// Example: Browser version (using fetch)
/*
async function loadTzData() {
    try {
        const response = await fetch('tzdata/combined.json');
        const tzdata = await response.json();
        
        // Use tzdata here
        console.log('Loaded', Object.keys(tzdata.timezones).length, 'timezones');
        return tzdata;
    } catch (error) {
        console.error('Failed to load timezone data:', error);
    }
}
*/
```

## SQL Examples (SQLite)

```sql
-- Find all zones in Australia
SELECT name, comment, latitude, longitude 
FROM zones 
WHERE country_code = 'AU'
ORDER BY name;

-- Count transitions by timezone
SELECT zone_name, COUNT(*) as transition_count
FROM transitions 
GROUP BY zone_name 
ORDER BY transition_count DESC 
LIMIT 10;

-- Find zones with Windows mappings
SELECT z.name, z.country_code, w.windows_name
FROM zones z
JOIN windows_mapping w ON z.name = w.iana_name
WHERE z.country_code = 'US'
ORDER BY z.name;

-- Get DST rules for a specific rule set
SELECT * FROM rules 
WHERE rule_name = 'AN' 
ORDER BY from_year, in_month;

-- Find zones that currently use DST
SELECT DISTINCT t.zone_name, z.country_code
FROM transitions t
JOIN zones z ON t.zone_name = z.name
WHERE t.rule_name IS NOT NULL 
  AND t.rule_name != '-'
  AND t.from_utc = ''  -- Current transition
ORDER BY z.country_code, t.zone_name;
```

## PHP Example

```php
<?php
// Load JSON data
$jsonContent = file_get_contents('tzdata/combined.json');
if ($jsonContent === false) {
    die("Error: Could not read tzdata/combined.json\n");
}

$tzdata = json_decode($jsonContent, true);
if ($tzdata === null) {
    die("Error: Could not parse JSON data\n");
}

// Example: Get timezone hierarchy
function getTimezonesByRegion($tzdata) {
    $regions = [];
    
    foreach ($tzdata['timezones'] as $name => $zone) {
        $parts = explode('/', $name);
        $region = $parts[0];
        
        if (!isset($regions[$region])) {
            $regions[$region] = [];
        }
        
        $regions[$region][] = [
            'name' => $name,
            'country' => $zone['country_code'],
            'comment' => $zone['comment']
        ];
    }
    
    return $regions;
}

// Example: Find zones with Windows mappings
function getZonesWithWindowsMapping($tzdata) {
    $result = [];
    
    foreach ($tzdata['timezones'] as $name => $zone) {
        if (!empty($zone['win_names'])) {
            $result[$name] = $zone['win_names'];
        }
    }
    
    return $result;
}

// Usage examples
$regions = getTimezonesByRegion($tzdata);
foreach ($regions as $region => $zones) {
    echo "Region: $region (" . count($zones) . " zones)\n";
}

echo "\nZones with Windows mappings:\n";
$windowsZones = getZonesWithWindowsMapping($tzdata);
foreach (array_slice($windowsZones, 0, 5, true) as $iana => $windows) {
    echo "$iana => " . implode(', ', $windows) . "\n";
}
?>
```

## Free Pascal Example

```pascal
program TZBundlerExample;

{$mode objfpc}{$H+}

uses
  SysUtils, Classes, fpjson, jsonparser;

var
  FileStream: TFileStream;
  JSONData: TJSONData;
  RootObj: TJSONObject;
  TimeZones: TJSONObject;
  Zone: TJSONObject;
  ZoneName: String;
  I: Integer;

begin
  FileStream := TFileStream.Create('tzdata/combined.json', fmOpenRead);
  try
    // Load JSON file
    JSONData := GetJSON(FileStream);
    try
      RootObj := JSONData as TJSONObject;
      TimeZones := RootObj.Objects['timezones'];
      
      WriteLn('Loading timezone data...');
      WriteLn('Found ', TimeZones.Count, ' timezones');
      WriteLn('');
      
      // Iterate through first 10 timezones as example
      for I := 0 to Min(9, TimeZones.Count - 1) do
      begin
        ZoneName := TimeZones.Names[I];
        Zone := TimeZones.Objects[ZoneName];
        
        WriteLn(Format('%-25s %s', [
          ZoneName, 
          Zone.Get('country_code', 'Unknown')
        ]));
      end;
      
      // Example: Find a specific timezone
      if TimeZones.IndexOfName('Australia/Sydney') >= 0 then
      begin
        Zone := TimeZones.Objects['Australia/Sydney'];
        WriteLn('');
        WriteLn('Australia/Sydney details:');
        WriteLn('  Country: ', Zone.Get('country_code', ''));
        WriteLn('  Comment: ', Zone.Get('comment', ''));
        WriteLn('  Coordinates: ', Zone.Get('coordinates', ''));
      end;
      
    finally
      JSONData.Free;
    end;
  finally
    FileStream.Free;
  end;
  
  WriteLn('');
  WriteLn('Press Enter to exit...');
  ReadLn;
end.
```

## Go Example

```go
package main

import (
    "encoding/json"
    "fmt"
    "log"
    "os"
)

type TZData struct {
    Timezones      map[string]Zone            `json:"timezones"`
    Rules          map[string][]Rule          `json:"rules"`
    WindowsMapping map[string][]string        `json:"windows_mapping"`
    Version        string                     `json:"_version"`
}

type Zone struct {
    CountryCode string       `json:"country_code"`
    Coordinates string       `json:"coordinates"`
    Comment     string       `json:"comment"`
    Transitions []Transition `json:"transitions"`
    Aliases     []string     `json:"aliases"`
    WinNames    []string     `json:"win_names"`
}

type Transition struct {
    FromUTC  string  `json:"from_utc"`
    ToUTC    *string `json:"to_utc"`
    Offset   string  `json:"offset"`
    Abbr     string  `json:"abbr"`
    RuleName *string `json:"rule_name"`
}

type Rule struct {
    From   string `json:"from"`
    To     string `json:"to"`
    Type   string `json:"type"`
    In     string `json:"in"`
    On     string `json:"on"`
    At     string `json:"at"`
    Save   string `json:"save"`
    Letter string `json:"letter"`
}

func main() {
    // Load JSON data
    data, err := os.ReadFile("tzdata/combined.json")
    if err != nil {
        log.Fatal("Error reading file:", err)
    }
    
    var tzdata TZData
    if err := json.Unmarshal(data, &tzdata); err != nil {
        log.Fatal("Error parsing JSON:", err)
    }
    
    // Example: Find zones by country
    fmt.Printf("Timezone data version: %s\n", tzdata.Version)
    fmt.Printf("Total timezones: %d\n\n", len(tzdata.Timezones))
    
    auZones := 0
    fmt.Println("Australian timezones:")
    for name, zone := range tzdata.Timezones {
        if zone.CountryCode == "AU" {
            auZones++
            fmt.Printf("  %-25s %s\n", name, zone.Comment)
        }
    }
    
    fmt.Printf("\nTotal Australian zones: %d\n", auZones)
    
    // Example: Check Windows mappings
    if zone, exists := tzdata.Timezones["Australia/Sydney"]; exists {
        fmt.Printf("\nAustralia/Sydney Windows names: %v\n", zone.WinNames)
    }
}
```
