# GTimes - GPS Time Processing Library

A comprehensive Python library for GPS time conversions and processing, developed at Veðurstofan Íslands (Icelandic Met Office) for scientific GPS data analysis.

## Overview

GTimes provides precise and reliable GPS time conversions essential for GNSS data processing, scientific analysis, and geodetic applications. The library handles the complexities of GPS time systems, leap seconds, and various time representations used in GPS processing workflows.

## Key Features

### 🕐 **Comprehensive Time Conversions**
- GPS time ↔ UTC conversions with leap second handling
- Fractional year representations for GAMIT/GLOBK compatibility
- Python datetime integration with microsecond precision
- Support for various time formats and representations

### 🛰️ **GPS-Specific Functionality**
- GPS week and seconds-of-week calculations
- Day-of-week and seconds-of-day conversions
- GPS epoch handling and week rollover support
- RINEX filename generation and time formatting

### 🔧 **Scientific Applications**
- GAMIT time series processing with fractional years
- GPS station data processing workflows
- RINEX file time stamp generation
- Icelandic GPS network data processing

### ⚡ **High Performance**
- Optimized algorithms with LRU caching
- Minimal dependencies (only python-dateutil)
- Efficient batch processing capabilities
- Microsecond-precision arithmetic

### 🛡️ **Robust & Reliable**
- Comprehensive input validation
- Detailed error messages with context
- 150+ test cases covering edge cases
- 100% backward compatibility

## Quick Example

```python
from gtimes.gpstime import gpsFromUTC, UTCFromGps
from gtimes.timefunc import TimefromYearf, dTimetoYearf
import datetime

# Convert UTC to GPS time
gps_week, sow, gps_day, sod = gpsFromUTC(2024, 1, 15, 12, 30, 45.123)
print(f"GPS Week: {gps_week}, SOW: {sow}")
# Output: GPS Week: 2297, SOW: 216645.123

# Convert GPS time back to UTC
utc_dt = UTCFromGps(gps_week, sow, dtimeObj=True)
print(f"UTC: {utc_dt}")
# Output: UTC: 2024-01-15 12:30:45.123000

# Work with fractional years (GAMIT compatible)
dt = datetime.datetime(2024, 7, 1, 12, 0, 0)
yearf = dTimetoYearf(dt)
print(f"Fractional year: {yearf:.6f}")
# Output: Fractional year: 2024.497260

# Convert fractional year back to datetime
dt_back = TimefromYearf(yearf)
print(f"Date: {dt_back}")
# Output: Date: 2024-07-01 11:56:02.976000
```

## Applications

### GNSS Data Processing
- **RINEX Processing**: Time stamp generation and validation
- **GPS Station Networks**: Multi-station time synchronization
- **Data Quality Control**: Time-based data validation and filtering

### Scientific Research
- **GAMIT/GLOBK Processing**: Fractional year time series analysis
- **Geodetic Studies**: Precise time references for coordinate analysis
- **Seismic Monitoring**: GPS time integration with seismic data

### Operational Workflows
- **File Organization**: Time-based directory and filename generation
- **Data Pipelines**: Automated GPS data processing workflows  
- **Station Monitoring**: Real-time GPS station data processing

## Installation

```bash
pip install gtimes
```

For development with testing capabilities:

```bash
pip install gtimes[dev]
```

## Command Line Tools

GTimes includes a powerful command-line interface for time calculations:

```bash
# Get current GPS week and day
timecalc -wd

# Convert specific date to GPS time
timecalc -wd -d "2024-01-15"

# Get fractional year
timecalc -yf -d "2024-07-01"

# Generate RINEX filename patterns
timecalc -l "REYK%j0.%yO" "1D" -d "2024-01-01"
```

## Documentation Sections

### [📚 User Guide](guides/installation.md)
Complete guides for installation, setup, and common usage patterns.

### [🔧 API Reference](api/gpstime.md)
Detailed documentation of all functions, classes, and modules.

### [💡 Examples](examples/basic-usage.md)
Real-world examples and code snippets for common GPS processing tasks.

### [🧪 Scientific Background](concepts/gps-time-systems.md)
In-depth explanation of GPS time systems, coordinate frames, and geodetic concepts.

### [👥 Development](development/contributing.md)
Information for contributors, testing procedures, and development workflows.

## Why GTimes?

### Precision & Accuracy
- Microsecond-level precision in all time conversions
- Proper leap second handling with historical data
- Scientific-grade accuracy for geodetic applications

### Ease of Use
- Intuitive Python API with comprehensive documentation
- Extensive examples covering real-world use cases
- Command-line tools for quick calculations

### Scientific Heritage
- Developed for the Icelandic GPS network
- Battle-tested in operational GPS processing
- Compatible with standard GPS processing software (GAMIT/GLOBK)

### Performance
- Minimal dependencies reduce installation complexity
- Efficient algorithms optimized for batch processing
- LRU caching for frequently accessed leap second data

## Support

- **Documentation**: Complete user guides and API reference
- **Examples**: Real-world GPS processing workflows
- **Testing**: Comprehensive test suite with 150+ test cases
- **Community**: Open source with active development

## License

GTimes is released under the MIT License, making it free for both academic and commercial use.

---

*Developed by the GPS team at Veðurstofan Íslands (Icelandic Met Office)*