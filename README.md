# GTimes - High-Precision GPS Time Processing Library

[![PyPI version](https://badge.fury.io/py/gtimes.svg)](https://badge.fury.io/py/gtimes)
[![Python versions](https://img.shields.io/pypi/pyversions/gtimes.svg)](https://pypi.org/project/gtimes/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD](https://github.com/bennigo/gtimes/actions/workflows/ci.yml/badge.svg)](https://github.com/bennigo/gtimes/actions/workflows/ci.yml)
[![Quality](https://github.com/bennigo/gtimes/actions/workflows/quality-checks.yml/badge.svg)](https://github.com/bennigo/gtimes/actions/workflows/quality-checks.yml)
[![codecov](https://codecov.io/gh/bennigo/gtimes/branch/main/graph/badge.svg)](https://codecov.io/gh/bennigo/gtimes)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://bennigo.github.io/gtimes)

**GTimes** is a high-precision GPS time conversion and processing library designed for GNSS applications, geodetic research, and scientific computing. It provides microsecond-accurate conversions between GPS time and UTC, handles leap seconds correctly, and offers comprehensive tools for time-related calculations in GPS data processing workflows.

## 🚀 Key Features

- **High-Precision GPS Time Conversions**: Microsecond-accurate GPS ↔ UTC conversions
- **Leap Second Management**: Automatic handling of leap seconds with up-to-date leap second data
- **RINEX Processing Support**: Time formatting and file organization for RINEX workflows
- **GAMIT/GLOBK Integration**: Fractional year conversions for GAMIT time series analysis
- **Command-Line Interface**: Powerful `timecalc` tool for shell scripting and automation
- **Scientific Validation**: Comprehensive testing against known GPS time standards
- **Cross-Platform**: Works on Linux, Windows, and macOS with Python 3.8+

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install gtimes
```

### Development Installation

```bash
git clone https://github.com/bennigo/gtimes.git
cd gtimes
pip install -e .[dev]
```

### With Documentation

```bash
pip install gtimes[docs]
mkdocs serve  # View documentation locally
```

## 🏃 Quick Start

### Basic GPS Time Conversions

```python
from gtimes.gpstime import gpsFromUTC, UTCFromGps
import datetime

# Convert current time to GPS
now = datetime.datetime.utcnow()
gps_week, sow, gps_day, sod = gpsFromUTC(
    now.year, now.month, now.day,
    now.hour, now.minute, now.second
)

print(f"Current GPS time: Week {gps_week}, SOW {sow:.3f}")

# Convert GPS time back to UTC
utc_datetime = UTCFromGps(gps_week, sow, dtimeObj=True)
print(f"Back to UTC: {utc_datetime}")
```

### GAMIT Fractional Year Processing

```python
from gtimes.timefunc import TimefromYearf, dTimetoYearf
import datetime

# Convert GAMIT fractional year to datetime
gamit_time = 2024.0411  # ~Feb 15, 2024
dt = TimefromYearf(gamit_time)
print(f"GAMIT {gamit_time:.4f} = {dt.strftime('%Y-%m-%d %H:%M:%S')}")

# Convert datetime to fractional year
date = datetime.datetime(2024, 6, 15, 12, 0, 0)
yearf = dTimetoYearf(date)
print(f"{date} = {yearf:.6f}")
```

### Command-Line Usage

```bash
# Get GPS week and day for today
timecalc -wd

# GPS time for specific date
timecalc -wd -d "2024-01-15"

# Generate RINEX filenames
timecalc -l "REYK%j0.%yO" "7D" -d "2024-01-15"

# Get fractional year for GAMIT
timecalc -yf -d "2024-06-15"
```

## 📊 Real-World Applications

### GPS Network Processing

```python
from gtimes.gpstime import gpsFromUTC
from gtimes.timefunc import datepathlist
import datetime

# Process GPS station data
stations = ['REYK', 'HOFN', 'AKUR', 'VMEY']
start_date = datetime.datetime(2024, 1, 15)

for station in stations:
    # Generate RINEX observation files
    obs_files = datepathlist(f"{station}%j0.%yO", "7D", start_date, 
                            start_date + datetime.timedelta(days=7))
    
    print(f"{station} files: {len(obs_files)} files")
    for obs_file in obs_files[:3]:  # Show first 3
        print(f"  {obs_file}")
```

### RINEX File Organization

```python
from gtimes.timefunc import datepathlist
import datetime

# Create processing directory structure
start = datetime.datetime(2024, 1, 1)
end = datetime.datetime(2024, 2, 1)

# Daily processing directories
daily_dirs = datepathlist("/gps_proc/%Y/%j/", "1D", start, end)
print("Daily processing directories:")
for directory in daily_dirs[:5]:
    print(f"  {directory}")

# Weekly GPS processing
weekly_dirs = datepathlist("/gps_proc/week_%U/", "7D", start, end)
print("Weekly processing directories:")
for directory in weekly_dirs:
    print(f"  {directory}")
```

## 🛠️ Advanced Usage

### High-Precision Time Series

```python
from gtimes.gpstime import gpsFromUTC, UTCFromGps
import datetime

# Process time series with microsecond precision
timestamps = [
    datetime.datetime(2024, 1, 15, 12, 30, 45, 123456),
    datetime.datetime(2024, 1, 15, 12, 30, 46, 234567),
    datetime.datetime(2024, 1, 15, 12, 30, 47, 345678),
]

gps_times = []
for ts in timestamps:
    # Convert with microsecond precision
    week, sow, day, sod = gpsFromUTC(
        ts.year, ts.month, ts.day, ts.hour, ts.minute,
        ts.second + ts.microsecond / 1e6
    )
    gps_times.append((week, sow))
    
    # Verify round-trip accuracy
    utc_back = UTCFromGps(week, sow, dtimeObj=True)
    diff = abs((utc_back - ts).total_seconds())
    print(f"GPS: Week {week}, SOW {sow:.6f}, Round-trip error: {diff:.6f}s")
```

### Leap Second Analysis

```python
from gtimes.gpstime import getleapSecs, leapSecDict
import datetime

# Analyze leap second history
leap_dict = leapSecDict()
print(f"Total leap seconds in database: {len(leap_dict)}")

# Check leap seconds for different epochs
important_dates = [
    ("GPS Epoch", datetime.datetime(1980, 1, 6)),
    ("Y2K", datetime.datetime(2000, 1, 1)),
    ("Recent", datetime.datetime(2024, 1, 1)),
]

for label, date in important_dates:
    gps_leap = getleapSecs(date, gpst=True)
    utc_leap = getleapSecs(date, gpst=False)
    print(f"{label}: GPS={gps_leap}, UTC={utc_leap} leap seconds")
```

## 🔧 Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/bennigo/gtimes.git
cd gtimes

# Install development dependencies
pip install -e .[dev,test,docs,quality]

# Run tests
pytest tests/ -v

# Run quality checks
ruff check src/ tests/
mypy src/gtimes/

# Build documentation
mkdocs build
mkdocs serve
```

### Running Benchmarks

```bash
# Performance benchmarks
pytest tests/benchmark/ --benchmark-only

# Scientific validation
python tests/validate_leap_seconds.py

# Documentation link checking
python tests/check_docs_links.py
```

## 📚 Documentation

- **[Full Documentation](https://bennigo.github.io/gtimes)**: Complete API reference and tutorials
- **[Installation Guide](https://bennigo.github.io/gtimes/guides/installation/)**: Detailed installation instructions
- **[Quick Start Tutorial](https://bennigo.github.io/gtimes/guides/quickstart/)**: Get started quickly
- **[API Reference](https://bennigo.github.io/gtimes/api/)**: Complete function documentation
- **[Examples](https://bennigo.github.io/gtimes/examples/)**: Real-world usage examples
- **[Contributing Guide](https://bennigo.github.io/gtimes/development/contributing/)**: How to contribute

## 🧪 Testing & Quality

GTimes maintains high standards for accuracy and reliability:

- **✅ Comprehensive Test Suite**: 200+ tests covering all functionality
- **✅ Scientific Validation**: GPS time accuracy verified against known standards
- **✅ Multi-Platform Testing**: Linux, Windows, macOS compatibility
- **✅ Performance Benchmarks**: >1000 GPS conversions/second
- **✅ Code Quality**: 90%+ test coverage, strict linting, type checking
- **✅ Documentation**: Complete API documentation with examples

### Accuracy Guarantees

- **Microsecond Precision**: GPS ↔ UTC conversions accurate to microseconds
- **Leap Second Handling**: Up-to-date leap second data (18 leap seconds as of 2024)
- **GPS Epoch Compliance**: Correct handling of GPS epoch (January 6, 1980)
- **Round-Trip Accuracy**: UTC → GPS → UTC conversions within 1μs

## 🌍 Applications

GTimes is used in various scientific and engineering applications:

- **GNSS Data Processing**: RINEX file processing and GPS network analysis
- **Geodetic Research**: Coordinate time series and plate motion studies  
- **Seismology**: GPS station monitoring and earthquake research
- **Meteorology**: GPS meteorology and atmospheric studies
- **Surveying**: High-precision positioning and coordinate systems
- **Satellite Navigation**: GPS receiver testing and algorithm development

## 🏢 Institutional Use

GTimes is developed and maintained by researchers at:

- **Veðurstofan Íslands** (Icelandic Met Office): Operational GPS network monitoring
- **GPS Research Community**: GAMIT/GLOBK processing workflows
- **Scientific Institutions**: Geodetic research and GNSS applications

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://bennigo.github.io/gtimes/development/contributing/) for details.

### Quick Contribution Steps

```bash
# Fork the repository on GitHub
git clone https://github.com/your-username/gtimes.git
cd gtimes

# Install development environment
pip install -e .[dev,test]

# Make changes and test
pytest tests/ -v
ruff check src/ tests/

# Submit pull request
```

## 📄 License

GTimes is released under the [MIT License](LICENSE). See LICENSE file for details.

## 🙏 Acknowledgments

- **IGS Community**: For GPS time standards and RINEX specifications
- **GAMIT/GLOBK Team**: For fractional year time representations
- **Scientific Python Community**: For the excellent ecosystem
- **Veðurstofan Íslands**: For supporting open-source GPS research tools

## 📞 Support & Contact

- **📖 Documentation**: [https://bennigo.github.io/gtimes](https://bennigo.github.io/gtimes)
- **🐛 Bug Reports**: [GitHub Issues](https://github.com/bennigo/gtimes/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/bennigo/gtimes/discussions)
- **📧 Email**: [bgo@vedur.is](mailto:bgo@vedur.is)

---

**GTimes** - Precision GPS time processing for scientific applications 🛰️⏰🔬
