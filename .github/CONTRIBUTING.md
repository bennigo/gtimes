# Contributing to GTimes

Thank you for your interest in contributing to GTimes! This document provides guidelines and information for contributors.

## 🚀 Quick Start for Contributors

```bash
# Fork the repository on GitHub
git clone https://github.com/your-username/gtimes.git
cd gtimes

# Set up development environment
pip install -e .[dev,test,docs,quality]

# Verify setup
pytest tests/ -v
ruff check src/ tests/
mypy src/gtimes/

# Make your changes, then test
pytest tests/ -v --cov=gtimes
```

## 📖 Full Contributing Guide

For comprehensive contributing instructions, please see our detailed [Contributing Guide](https://bgo-ehi.github.io/gtimes/development/contributing/).

The documentation includes:
- **Development Environment Setup**: Complete setup instructions
- **Code Standards**: Style guide and quality requirements  
- **Testing Guidelines**: How to write and run tests
- **Pull Request Process**: Step-by-step contribution workflow
- **Scientific Validation**: GPS time accuracy requirements

## 🎯 Ways to Contribute

### 1. Bug Reports
- Use our [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- Include GPS time context and scientific impact
- Provide minimal reproducible examples

### 2. Feature Requests  
- Use our [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- Describe GPS/GNSS use cases and scientific applications
- Consider performance and precision requirements

### 3. Code Contributions
- Follow our [pull request template](.github/PULL_REQUEST_TEMPLATE.md)
- Maintain microsecond precision for GPS time functions
- Include comprehensive tests and documentation

### 4. Documentation Improvements
- API documentation updates
- Tutorial and example enhancements
- Scientific background explanations

## 🔬 Scientific Standards

GTimes maintains strict scientific accuracy standards:

### GPS Time Requirements
- **Microsecond precision** for all GPS ↔ UTC conversions
- **Leap second compliance** with up-to-date IERS data
- **GPS epoch accuracy** (January 6, 1980 00:00:00 UTC)
- **Standards compliance** with GPS ICD, RINEX, and GAMIT specifications

### Validation Requirements
- All GPS time functions must pass scientific validation tests
- Round-trip conversions must be accurate within 1 microsecond
- Leap second transitions must be handled correctly
- Edge cases (GPS epoch, year boundaries) must be tested

## 🧪 Testing Standards

### Test Categories
- **Unit tests**: Individual function testing
- **Integration tests**: Cross-module workflows
- **Scientific validation**: GPS time accuracy verification
- **Performance tests**: Speed and memory benchmarking
- **Platform tests**: Cross-platform compatibility

### Test Requirements
- All new code must include comprehensive tests
- Test coverage should be ≥80% for new functionality
- Scientific accuracy tests for GPS time functions
- Performance benchmarks for computationally intensive functions

## 📋 Code Standards

### Python Style
- **PEP 8 compliance** with 88-character line length
- **Type annotations** required for all public functions
- **Google-style docstrings** for all public APIs
- **Ruff** for linting and formatting

### GPS-Specific Conventions
- Function names follow GPS community conventions (e.g., `gpsFromUTC`)
- GPS week/time-of-week variables clearly named
- Scientific precision maintained in all calculations
- Error messages include GPS time context

## 🏗️ Development Workflow

### 1. Setup Development Environment
```bash
git clone https://github.com/your-username/gtimes.git
cd gtimes
pip install -e .[dev,test,docs,quality]
```

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes and Test
```bash
# Run tests
pytest tests/ -v

# Check code quality  
ruff check src/ tests/
mypy src/gtimes/

# Run scientific validation
python tests/validate_leap_seconds.py
```

### 4. Submit Pull Request
- Use the [pull request template](.github/PULL_REQUEST_TEMPLATE.md)
- Include comprehensive description and test results
- Ensure all CI checks pass

## 🌍 GPS/GNSS Community Context

### Scientific Applications
GTimes supports various GPS/GNSS applications:
- **Geodesy**: Coordinate time series and plate motion analysis
- **Seismology**: GPS station monitoring and earthquake research
- **Meteorology**: GPS atmospheric and weather applications
- **Surveying**: High-precision positioning and mapping
- **Research**: RINEX processing and GAMIT/GLOBK workflows

### Standards Compliance
- **GPS Interface Control Document (ICD-GPS-200)**
- **RINEX format specifications (IGS/RTCM)**
- **International Terrestrial Reference Frame (ITRF)**
- **GAMIT/GLOBK processing requirements**

## 📞 Getting Help

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and community discussions
- **Email**: [bgo@vedur.is](mailto:bgo@vedur.is) for complex issues

### Resources
- **[Documentation](https://bgo-ehi.github.io/gtimes)**: Complete API reference and guides
- **[Contributing Guide](https://bgo-ehi.github.io/gtimes/development/contributing/)**: Detailed development instructions
- **[Examples](https://bgo-ehi.github.io/gtimes/examples/)**: Real-world usage patterns

## 👥 Community Guidelines

### Respectful Collaboration
- Be respectful and inclusive in all interactions
- Provide constructive feedback on code and ideas
- Help newcomers learn GPS time concepts and conventions
- Share knowledge about GPS/GNSS applications and standards

### Scientific Integrity
- Maintain accuracy in GPS time calculations and documentation
- Cite relevant GPS/GNSS standards and references
- Validate scientific claims with appropriate testing
- Consider real-world GPS processing requirements

## 🎖️ Recognition

Contributors are recognized in:
- **README.md**: Contributor list with GitHub profiles
- **CHANGELOG.md**: Release notes acknowledging contributions
- **Documentation**: Author attribution for significant contributions
- **Git history**: Permanent record of all contributions

## 📄 Legal

By contributing to GTimes, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

**Thank you for helping make GTimes better!** 🛰️

Your contributions help advance GPS time processing capabilities for the global scientific community.