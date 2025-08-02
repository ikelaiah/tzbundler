## Changelog

### 1.0.1 (2025-07-31)

- Refactored transition model: removed `from_utc`, now only `to_utc` (IANA UNTIL) is used for all transitions
- All parsing, output, and serialization logic updated for IANA compatibility
- Documentation overhaul: clarified transition semantics, updated all examples, and improved DST calculation guidance
- Added acknowledgements for [a-blekot](https://github.com/a-blekot) and the Python community
- Version bump to v1.0.1


### 1.0 (2025-07-27)

- First public release with version badge
- Adds official Windows timezone mapping (Unicode CLDR)
- Outputs both JSON and SQLite with normalized, cross-platform data
- Includes bidirectional IANA ↔ Windows mapping in both formats
- Robust error handling and clear documentation
