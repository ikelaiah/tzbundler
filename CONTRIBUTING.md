# Contributing to tzbundler

Thank you for your interest in contributing to tzbundler! This document provides guidelines and information for contributors.

## 🎯 Project Goals

tzbundler aims to:
- Provide IANA tzdata in easily consumable formats (JSON/SQLite)
- Include Windows timezone mappings for cross-platform compatibility
- Keep DST logic in consumer applications (not pre-calculated)
- Support multiple programming languages through simple data formats

## 🚀 Quick Start

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/yourusername/tzbundler.git
   cd tzbundler
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Test the tool:**
   ```bash
   python make_tz_bundle.py
   python test_outputs.py
   ```

## 📝 Types of Contributions

### 🐛 Bug Reports
- Use GitHub Issues with the "bug" label
- Include your Python version and OS
- Provide minimal reproduction steps
- Include relevant error messages

### ✨ Feature Requests
- Use GitHub Issues with the "enhancement" label
- Explain the use case and expected behavior
- Consider backward compatibility

### 📚 Documentation
- Improve README clarity
- Add usage examples for different languages
- Fix typos or clarify confusing sections

### 🔧 Code Contributions
- Follow the existing code style
- Add comments for complex logic
- Include tests for new functionality

## 🧪 Testing Guidelines

### Before Submitting
Run these checks:

```bash
# Test the main functionality
python make_tz_bundle.py

# Verify outputs
python test_outputs.py

# Test error handling (optional)
python test_windowsZones.py
```

### Test Data Quality
Verify your changes don't break:
- JSON structure validity
- SQLite schema consistency
- Windows mapping completeness
- Version tracking accuracy

## 📋 Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Keep commits focused and atomic
   - Write clear commit messages
   - Follow the existing code style

3. **Test thoroughly:**
   - Run the full pipeline
   - Verify outputs are correct
   - Test edge cases if applicable

4. **Update documentation:**
   - Update README if adding features
   - Add examples if appropriate
   - Update changelog if significant

5. **Submit pull request:**
   - Use a clear, descriptive title
   - Explain what changes and why
   - Reference any related issues

## 🎨 Code Style Guidelines

### Python Style
- Follow PEP 8 broadly, but prioritize readability
- Use descriptive variable names
- Add docstrings for functions and classes
- Comment complex parsing logic

### Documentation Style
- Use clear, concise language
- Include practical examples
- Structure with headers and lists
- Test all code examples

## 🗂️ Project Structure

```
tzbundler/
├── make_tz_bundle.py      # Main entry point
├── get_latest_tz.py       # Download logic
├── test_outputs.py        # Verification script
├── test_windowsZones.py   # Debug utilities
├── requirements.txt       # Dependencies
├── README.md             # Main documentation
├── CHANGELOG.md          # Version history
├── LICENSE               # MIT license
├── .gitignore           # Git ignore rules
├── examples/            # Usage examples (add this!)
│   └── usage-examples.md
└── tzdata/              # Generated output
    ├── combined.json
    └── combined.sqlite
```

## 🔍 Common Issues

### Download Failures
- IANA website occasionally has temporary issues
- Network connectivity problems
- Firewall/proxy blocking requests

### Parsing Errors
- tzdata format changes (rare but possible)
- Unicode encoding issues
- XML structure changes in CLDR

### Windows Mapping Issues
- CLDR repository structure changes
- New timezone mappings in updates
- Regional vs. global mapping preferences

## 📚 Helpful Resources

- [IANA Time Zone Database](https://www.iana.org/time-zones)
- [tzdata Theory Documentation](https://data.iana.org/time-zones/theory.html)
- [Unicode CLDR WindowsZones](https://github.com/unicode-org/cldr/blob/main/common/supplemental/windowsZones.xml)
- [RFC 6557 - tzdata Format](https://tools.ietf.org/html/rfc6557)

## 🤝 Community Guidelines

- Be respectful and constructive
- Help others learn and contribute
- Focus on improving the project
- Assume good intentions

## 📧 Getting Help

- **GitHub Issues:** For bugs and feature requests
- **GitHub Discussions:** For questions and general discussion
- **Email:** Contact the maintainer for sensitive issues

## 🏷️ Versioning

tzbundler follows semantic versioning:
- **Major (X.0.0):** Breaking changes to output format
- **Minor (0.X.0):** New features, backward compatible
- **Patch (0.0.X):** Bug fixes and improvements

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to tzbundler! 🎉