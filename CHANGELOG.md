# Changelog

All notable changes to the GTimes project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- `parse_rinex2_filename` now recognises `.YYd` Hatanaka-compressed observation
  files (e.g. `ELDC0150.26d`). Previously the regex only matched `[ongmlh]`, so
  Hatanaka filenames silently returned `None`.

## [0.5.0] - 2026-04-18

### Fixed
- `datepathlist()` now respects the `lfrequency` parameter. Previously it
  hardcoded a daily interval regardless of requested frequency, so hourly
  (e.g. `"1H"`, `"3H"`) GNSS receiver downloads fell back to daily intervals.
  Added private helper `_parse_frequency_to_timedelta()` supporting H/D/W/M/S
  units. Backward compatible: empty/None defaults to daily, 8H session logic
  unchanged.

### Added
- **Package-level RINEX API**: `rinex2_filename`, `rinex3_filename`,
  `rinex_filename`, `parse_rinex2_filename`, `parse_rinex3_filename`, and
  `convert_rinex_filename` are now importable directly from `gtimes`.
- **`rinex3_filename(uppercase=...)`** optional flag for uppercase station
  IDs (default lowercase per RINEX 3 standard).
- **Time-range helpers in `timefunc`** for domain-generic time-series
  iteration: `previous_complete_period`, `generate_time_range`,
  `generate_datetime_list`, `generate_period_ranges`. All accept frequency
  as timedelta or string; end-exclusive to avoid reading mid-write periods.
- **`parse_datetime_flexible()`** multi-format datetime parser (ISO 8601,
  caller-supplied formats, built-in fallbacks).
- **`timecalc` CLI flags**: `--rin2`, `--rin3`, `--rinex-convert`,
  `--rinex-parse` for RINEX filename generation, conversion, and parsing.

### Tests
- 40+ new tests covering hourly frequency handling, RINEX round-trip
  generation/parsing, time-range iteration, and flexible datetime parsing.

## [0.4.0] - 2024-12-02

### Added
- **Phase 3B: Professional Documentation** 🎉
  - Complete MkDocs documentation website with Material theme
  - Comprehensive API reference with auto-generated documentation
  - User guides for installation and quick start
  - Developer contribution guide with setup instructions
  - Real-world usage examples and tutorials
  - Responsive design with dark/light mode support
  
- **Phase 3C: CI/CD Pipeline Infrastructure** 🚀
  - Multi-platform automated testing (Linux, Windows, macOS)
  - Python 3.8-3.12 compatibility testing
  - Scientific validation of GPS time accuracy
  - Performance benchmarking with regression detection
  - Security vulnerability scanning
  - Automated documentation deployment to GitHub Pages
  - PyPI release automation with test validation
  - Quality gates with comprehensive code analysis
  
- **Phase 3D: Distribution & Packaging** 📦
  - Optimized PyPI package metadata and keywords
  - Professional README with badges and comprehensive examples
  - Enhanced project URLs and discovery metadata
  - Semantic versioning with automated changelog management

### Enhanced
- **GPS Time Conversion Functions**
  - Improved precision handling for microsecond accuracy
  - Enhanced leap second data validation
  - Better error handling and validation messages
  - Comprehensive type annotations

- **Command-Line Interface (`timecalc`)**
  - Enhanced help documentation
  - Improved error reporting
  - Better integration with shell scripting

- **Development Experience**
  - Complete test coverage with multiple test categories
  - Enhanced development dependencies and tooling
  - Automated quality checks and formatting
  - Comprehensive benchmarking suite

### Fixed
- GPS epoch handling edge cases
- Leap year calculation accuracy
- Time zone handling consistency  
- Documentation link validation
- Cross-platform compatibility issues

### Documentation
- Complete API reference with examples
- Installation guide with multiple methods
- Quick start tutorial with real-world scenarios
- Advanced usage patterns and best practices
- Developer contribution guidelines
- Scientific background and accuracy guarantees

### Technical Infrastructure
- GitHub Actions CI/CD with 8 specialized workflows
- Automated testing across 15 environment combinations
- Performance monitoring with benchmark tracking
- Security scanning with vulnerability reporting
- Documentation deployment with link validation
- Release automation with PyPI publishing

## [0.3.3] - Previous Version

### Added
- Basic GPS time conversion functionality
- GAMIT fractional year support
- Command-line interface (timecalc)
- RINEX file processing utilities

### Features
- GPS ↔ UTC time conversions
- Leap second handling
- Time string formatting
- Date arithmetic operations
- File path generation for GPS workflows

## Migration Guide

### From 0.3.x to 0.4.0

The GTimes 0.4.0 release is **fully backward compatible** with 0.3.x versions. All existing APIs continue to work without changes.

#### New Features Available
- Enhanced documentation and examples
- Improved error handling and validation
- Better type annotations for IDE support
- Additional development and testing tools

#### Installation Updates
```bash
# Standard installation (unchanged)
pip install gtimes

# New optional dependencies available
pip install gtimes[dev]      # Development tools
pip install gtimes[test]     # Testing framework
pip install gtimes[docs]     # Documentation building
pip install gtimes[quality]  # Quality assurance tools
pip install gtimes[all]      # All optional dependencies
```

#### Enhanced Development Workflow
```bash
# New development setup
git clone https://github.com/bennigo/gtimes.git
cd gtimes
pip install -e .[dev,test,docs]

# Run comprehensive tests
pytest tests/ -v

# Run quality checks
ruff check src/ tests/
mypy src/gtimes/

# Build documentation
mkdocs serve
```

No code changes required for existing users.

## Development Milestones

### Phase 1: Core Implementation ✅
- GPS time conversion algorithms
- Leap second data management  
- Basic command-line interface
- RINEX and GAMIT integration

### Phase 2: Testing & Validation ✅
- Comprehensive test suite
- Scientific accuracy validation
- Performance optimization
- Cross-platform compatibility

### Phase 3A: Testing Infrastructure ✅
- Enhanced test framework
- Automated testing setup
- Quality assurance tools
- Development environment

### Phase 3B: Professional Documentation ✅
- Complete API documentation
- User guides and tutorials
- Professional website design
- Examples and best practices

### Phase 3C: CI/CD Pipeline ✅
- Automated testing workflows
- Quality gates and validation
- Performance monitoring
- Release automation

### Phase 3D: Distribution & Packaging ✅
- PyPI optimization
- Package metadata enhancement
- Professional presentation
- Community readiness

## Contributors

### Core Team
- **Benedikt Gunnar Ófeigsson** - Project Lead & Core Developer
- **Maria Fernanda Gonzalez** - Developer & Tester

### Institutional Support
- **Veðurstofan Íslands** (Icelandic Met Office) - Primary development and testing
- **GPS Research Community** - Requirements and validation

### Acknowledgments
- IGS Community for GPS time standards
- GAMIT/GLOBK team for fractional year specifications
- Scientific Python community for the excellent ecosystem
- All users who provided feedback and bug reports

## Version History Summary

| Version | Release Date | Major Changes |
|---------|-------------|---------------|
| 0.4.0   | 2024-12-02  | Professional documentation, CI/CD, distribution |
| 0.3.3   | Previous    | Core GPS time functionality |
| 0.3.x   | Historical  | Initial implementations |

## Planned Features

### Future Enhancements
- Additional coordinate system support
- Enhanced RINEX 3.x compatibility  
- Real-time leap second updates
- GPS constellation expansions (Galileo, GLONASS, BeiDou)
- Advanced time series analysis tools

### Community Requests
- Web API interface
- Additional output formats
- Enhanced plotting capabilities
- Database integration tools

---

For detailed technical changes, see the [GitHub releases](https://github.com/bennigo/gtimes/releases) and [commit history](https://github.com/bennigo/gtimes/commits).

**Questions?** Open an [issue](https://github.com/bennigo/gtimes/issues) or start a [discussion](https://github.com/bennigo/gtimes/discussions).