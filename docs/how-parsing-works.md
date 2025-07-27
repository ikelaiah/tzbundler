# ❓ How Parsing Works

## Zone Block Example (from tzdata source)

```text
Zone    Asia/Baku    3:19:24 -    LMT    1924 May 2
                     3:00    -    %z     1957 Mar  
                     4:00    RussiaAsia %z 1991 Mar 31 2:00s
                     3:00    RussiaAsia %z 1992 Sep lastSun 2:00s
                     4:00    -    %z     1996
                     4:00    EUAsia %z  1997
                     4:00    Azer   %z
```

### 1. Zone Block Structure

- The first line starts with `Zone` and the zone name (`Asia/Baku`).
- The following indented lines (no `Zone` keyword) are *continuations*—each describes a new period (transition) in the zone's history.

### 2. Parsing Steps

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

### 3. Output Structure (JSON)

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

### 4. Notes

- The `abbr` field is `"LMT"` or `"%z"` (which means the abbreviation is determined by rules).
- The `rule_name` field (e.g., `"RussiaAsia"`, `"EUAsia"`, `"Azer"`) is used to look up DST rules.
- The `from_utc` field is the UNTIL value (when this transition ends).
- Metadata (`country_code`, `latitude`, etc.) is added later from `zone1970.tab`.
- Windows timezone names are added from the Unicode CLDR mappings.
- **DST calculations are left to consumers** using the rules data.

### 5. Summary

Each line in the zone block becomes a `Transition` in the `Zone.transitions` list. The zone itself is created once, and metadata is attached later. DST status must be calculated by consumers using the provided rules.
