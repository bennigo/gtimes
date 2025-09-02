# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **gtimes** package - part of the gpslibrary_new collection. It provides GPS time conversions and temporal calculations for scientific applications at Veðurstofan Íslands (Icelandic Met Office). The package handles GPS-specific time formats, fractional year conversions, and string formatting for GNSS data processing workflows.

## Development Commands

### Installation and Setup
```bash
# Install in development mode
pip install -e .

# Install with UV (if uv.lock exists)
uv sync
```

### Command-Line Usage
```bash
# Time calculation examples
timecalc -wd                           # Get GPS week and day
timecalc -wd -d 2016-10-1             # GPS week/day for specific date
timecalc -D 10 -l "/%Y/#gpsw/#b/VONC#Rin2D.Z " 1D -d 2015-10-01   # Complex RINEX filename generation

# Get help
timecalc -h
```

### Testing
No formal test suite currently exists. Testing is done via the command-line interface and integration with parent library workflows.

## Architecture Overview

### Core Modules

#### `gpstime.py` 
- **Source**: LIGO Scientific Collaboration GPS time utilities (GNU LGPL)
- **Core Functions**:
  - `gpsFromUTC()` - Convert UTC to GPS week/seconds
  - `UTCFromGps()` - Convert GPS week/seconds to UTC  
  - `GpsSecondsFromPyUTC()` - Python UTC to GPS seconds
  - `getleapSecs()` - Automatic leap second handling
- **Key Constants**: GPS epoch (1980-01-06), leap second tables

#### `timefunc.py`
- **Purpose**: High-level time manipulation using gpstime and datetime
- **Core Functions**:
  - `dTimetoYearf()` - Convert datetime to fractional year
  - `TimefromYearf()` - Convert fractional year to datetime/formatted string
  - `currDatetime()` - Current date with offset handling
  - `gpsfDateTime()` - GPS-specific date formatting
  - `round_to_hour()` - Round datetime to nearest hour
- **String Formatting**: Custom format strings for RINEX filenames and scientific data

#### `timecalc.py`
- **Command-line interface** for time calculations
- **GPS-specific options**: Week/day output, RINEX filename generation
- **Date validation** and argument parsing

### Dependencies
- **Core**: `pandas>=2.0.3`, `python-dateutil>=2.9.0`
- **Standard**: `numpy`, `datetime`, `calendar`, `math`
- **Build**: `hatchling` backend

## Key Time Handling Concepts

### GPS Time System
- **GPS Epoch**: January 6, 1980, 00:00:00 UTC
- **GPS Week**: Integer weeks since GPS epoch
- **Seconds of Week (SOW)**: 0-604799 seconds within GPS week
- **Leap Seconds**: Automatically handled via internal tables

### Fractional Year Format
- Used extensively in GAMIT time series processing
- Format: `YYYY.FFFFFF` where decimal represents day of year + time
- Functions: `dTimetoYearf()`, `TimefromYearf()`, `convfromYearf()`

### String Formatting Patterns
Complex format strings support GPS-specific tokens:
- `#gpsw` - GPS week number
- `#Rin2D` - RINEX 2-character day of year
- `#b` - Short month name
- Standard strftime patterns supported

## Development Notes

### Code Conventions
- **Function naming**: Mixed camelCase and snake_case (legacy patterns)
- **Time handling**: Always use timezone-aware datetime objects when possible
- **GPS compliance**: Maintain compatibility with IGS and RINEX standards

### Recent Changes
- Added `round_to_hour()` function for temporal rounding
- Enhanced `TimefromYearf()` with optional hour rounding (`rhour` parameter)
- Import reorganization and code formatting improvements

### Integration Context
- **Parent library**: Part of 6-package gpslibrary_new collection
- **Used by**: `gps_plot` package (GitHub dependency)
- **Consumers**: RINEX processors, GAMIT workflows, GPS station monitoring

### Leap Second Management
- Automatic detection based on date ranges
- Internal leap second table maintained in `leapSecDict()`
- Default to current leap second count (18 as of 2019)

## File Structure

```
src/gtimes/
├── __init__.py          # Package initialization
├── gpstime.py           # Low-level GPS time conversions (LGPL)
├── timefunc.py          # High-level time manipulation functions
└── timecalc.py          # Command-line interface
```