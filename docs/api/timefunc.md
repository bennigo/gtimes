# Time Utilities API

The `gtimes.timefunc` module provides essential time utility functions for GPS data processing, including fractional year conversions, date arithmetic, file path generation, and GPS-specific time formatting.

## Overview

This module contains utility functions commonly used in GPS processing workflows, particularly for:
- Converting between datetime objects and fractional years (GAMIT/GLOBK compatibility)
- Generating time-based file paths for GPS data organization
- Date arithmetic and time shifting operations
- GPS-specific time formatting and calculations

## Fractional Year Functions

Fractional years are commonly used in GAMIT/GLOBK processing and geodetic time series analysis.

::: gtimes.timefunc.TimefromYearf
    options:
      show_source: true
      heading_level: 3

::: gtimes.timefunc.dTimetoYearf
    options:
      show_source: true
      heading_level: 3

::: gtimes.timefunc.currYearfDate
    options:
      show_source: true
      heading_level: 3

## Date Arithmetic Functions

::: gtimes.timefunc.shifTime
    options:
      show_source: true
      heading_level: 3

::: gtimes.timefunc.currDatetime
    options:
      show_source: true
      heading_level: 3

::: gtimes.timefunc.currDate
    options:
      show_source: true
      heading_level: 3

## File Path Generation

::: gtimes.timefunc.datepathlist
    options:
      show_source: true
      heading_level: 3

## GPS Time Utilities

::: gtimes.timefunc.gpsWeekDay
    options:
      show_source: true
      heading_level: 3

::: gtimes.timefunc.gpsfDateTime
    options:
      show_source: true
      heading_level: 3

::: gtimes.timefunc.dateTuple
    options:
      show_source: true
      heading_level: 3

## Calendar Utilities

::: gtimes.timefunc.DaysinYear
    options:
      show_source: true
      heading_level: 3

::: gtimes.timefunc.shlyear
    options:
      show_source: true
      heading_level: 3

::: gtimes.timefunc.hourABC
    options:
      show_source: true
      heading_level: 3

::: gtimes.timefunc.round_to_hour
    options:
      show_source: true
      heading_level: 3

## Usage Examples

### Working with Fractional Years

Fractional years are essential for GAMIT time series analysis:

```python
from gtimes.timefunc import TimefromYearf, dTimetoYearf
import datetime

# Convert datetime to fractional year (for GAMIT)
dt = datetime.datetime(2024, 7, 1, 12, 0, 0)
yearf = dTimetoYearf(dt)
print(f"Fractional year: {yearf:.6f}")  # 2024.497260

# Convert fractional year back to datetime  
dt_back = TimefromYearf(yearf)
print(f"DateTime: {dt_back}")  # 2024-07-01 11:56:02.976000

# Format as string
date_str = TimefromYearf(yearf, String="%Y-%m-%d %H:%M:%S")
print(f"Formatted: {date_str}")  # 2024-07-01 11:56:02

# Round to nearest hour
dt_rounded = TimefromYearf(yearf, rhour=True)
print(f"Rounded: {dt_rounded}")  # 2024-07-01 12:00:00

# Get ordinal day representation
ordinal = TimefromYearf(yearf, String="ordinalf")
print(f"Ordinal: {ordinal}")  # Float representation
```

### Time Shifting and Arithmetic

```python
from gtimes.timefunc import shifTime, currDatetime, currDate
import datetime

# Parse time shift strings
shift = shifTime("d5:H12:M30:S45")
print(f"Shift: {shift}")  # {'days': 5, 'hours': 12, 'minutes': 30, 'seconds': 45}

# Apply shifts to datetime
base_dt = datetime.datetime(2024, 1, 15, 12, 0, 0)
shifted_dt = currDatetime(days="d7", refday=base_dt)
print(f"Shifted: {shifted_dt}")  # 2024-01-22 12:00:00

# Complex shifts
complex_shift = currDatetime(days="d-5:H3:M-30", refday=base_dt)
print(f"Complex shift: {complex_shift}")  # 2024-01-10 14:30:00

# Work with dates only
base_date = datetime.date(2024, 1, 15)
shifted_date = currDate(days=30, refday=base_date)
print(f"Date shifted: {shifted_date}")  # 2024-02-14

# Format shifted dates
date_str = currDate(days=7, refday=base_date, String="%Y%m%d")
print(f"Formatted: {date_str}")  # 20240122
```

### GPS Data File Organization

Generate file paths for GPS data processing workflows:

```python
from gtimes.timefunc import datepathlist
import datetime

start = datetime.datetime(2024, 1, 15, 0, 0, 0)
end = datetime.datetime(2024, 1, 18, 0, 0, 0)

# Generate daily RINEX observation files
rinex_obs = datepathlist("REYK%j0.%yO", "1D", start, end)
print("RINEX Observation files:")
for filename in rinex_obs:
    print(f"  {filename}")
# Output:
#   REYK0150.24O
#   REYK0160.24O  
#   REYK0170.24O

# Generate monthly directories with GPS week numbers
monthly_dirs = datepathlist("/gps_data/%Y/%m/week_#gpsw/", "1D", start, end)
print("Monthly directories:")
for path in monthly_dirs[:3]:  # Show first 3
    print(f"  {path}")
# Output:
#   /gps_data/2024/01/week_2297/
#   /gps_data/2024/01/week_2297/
#   /gps_data/2024/01/week_2297/

# Generate RINEX filenames with session identifiers
rinex_sessions = datepathlist("HOFN#Rin2O.Z", "1D", start, end)
print("RINEX with sessions:")
for filename in rinex_sessions:
    print(f"  {filename}")
# Output:
#   HOFN0150.24O.Z
#   HOFN0160.24O.Z
#   HOFN0170.24O.Z
```

### GPS Week and Day Calculations

```python
from gtimes.timefunc import gpsWeekDay, gpsfDateTime, dateTuple
import datetime

# Calculate GPS week and day
dt = datetime.datetime(2024, 1, 15, 14, 30, 45)
gps_week, gps_day = gpsWeekDay(dt)
print(f"GPS Week: {gps_week}, GPS Day: {gps_day}")  # GPS Week: 2297, GPS Day: 1

# Get full GPS time breakdown
gps_week, sow, dow, sod = gpsfDateTime(dt)
print(f"Week: {gps_week}")        # Week: 2297
print(f"SOW: {sow}")              # SOW: 138645.0  
print(f"DOW: {dow}")              # DOW: 1 (Monday)
print(f"SOD: {sod}")              # SOD: 52245.0

# Generate comprehensive date tuple
date_info = dateTuple(dt)
print(f"Date tuple: {date_info}")
# (year, month, day, doy, yearf, gps_week, dow, hour, minute, formatted_string)
```

### Calendar Utilities

```python
from gtimes.timefunc import DaysinYear, shlyear, hourABC

# Days in year (handles leap years)
print(f"Days in 2024: {DaysinYear(2024)}")  # 366 (leap year)
print(f"Days in 2023: {DaysinYear(2023)}")  # 365

# Year format conversion
print(f"Short year: {shlyear(2024, change=True)}")  # 24
print(f"Long year: {shlyear(24, change=True)}")     # 2024

# Hour to alphabetic conversion (RINEX naming)
print(f"Hour 0: {hourABC(0)}")   # 'a'
print(f"Hour 1: {hourABC(1)}")   # 'b'
print(f"Hour 23: {hourABC(23)}") # 'x'
```

### RINEX File Processing Workflow

Complete example of generating RINEX filenames for a GPS station:

```python
from gtimes.timefunc import datepathlist, gpsWeekDay
import datetime

def generate_rinex_files(station, start_date, days=7):
    """Generate RINEX filenames for a station over multiple days."""
    end_date = start_date + datetime.timedelta(days=days)
    
    # Daily observation files
    obs_files = datepathlist(f"{station}%j0.%yO", "1D", start_date, end_date)
    
    # Daily navigation files
    nav_files = datepathlist(f"{station}%j0.%yN", "1D", start_date, end_date)
    
    # Hourly observation files (example for first day)
    hourly_files = datepathlist(f"{station}%j%H.%yO", "1H", 
                               start_date, 
                               start_date + datetime.timedelta(days=1))
    
    return {
        'daily_obs': obs_files,
        'daily_nav': nav_files, 
        'hourly_obs': hourly_files[:24]  # First 24 hours
    }

# Generate files for REYK station
start = datetime.datetime(2024, 1, 15, 0, 0, 0)
files = generate_rinex_files("REYK", start, days=3)

print("Daily observation files:")
for f in files['daily_obs']:
    print(f"  {f}")

print("\nDaily navigation files:")
for f in files['daily_nav']:
    print(f"  {f}")

print(f"\nHourly files for first day ({len(files['hourly_obs'])} files):")
for f in files['hourly_obs'][:6]:  # Show first 6 hours
    print(f"  {f}")
```

### GAMIT Time Series Processing

Example workflow for processing GAMIT time series data:

```python
from gtimes.timefunc import TimefromYearf, dTimetoYearf, currYearfDate
import datetime

def process_gamit_timeseries(data_file, output_format="%Y-%m-%d"):
    """Process GAMIT fractional year time series."""
    # Example fractional years from GAMIT output
    fractional_years = [2024.0, 2024.0274, 2024.0548, 2024.0822, 2024.1096]
    
    processed_data = []
    for yearf in fractional_years:
        # Convert to datetime
        dt = TimefromYearf(yearf)
        
        # Format for output
        formatted_date = TimefromYearf(yearf, String=output_format)
        
        # Calculate GPS week for organization
        week, day = gpsWeekDay(dt)
        
        processed_data.append({
            'fractional_year': yearf,
            'datetime': dt,
            'formatted': formatted_date,
            'gps_week': week,
            'gps_day': day
        })
    
    return processed_data

# Process time series
results = process_gamit_timeseries("dummy_file")
print("GAMIT Time Series Processing:")
for result in results:
    print(f"  {result['fractional_year']:.4f} -> {result['formatted']} "
          f"(Week {result['gps_week']}, Day {result['gps_day']})")
```

### Real-time GPS Processing

Example of real-time GPS data organization:

```python
from gtimes.timefunc import currYearfDate, currDatetime, datepathlist
import datetime

def organize_realtime_data():
    """Organize real-time GPS data by time periods."""
    now = datetime.datetime.utcnow()
    
    # Current fractional year for GAMIT processing
    current_yearf = currYearfDate()
    
    # Generate processing directories for the current week
    week_start = now - datetime.timedelta(days=now.weekday())
    week_end = week_start + datetime.timedelta(days=7)
    
    # Daily processing directories
    daily_dirs = datepathlist(
        "/gps_proc/%Y/%j/daily/",
        "1D", 
        week_start, 
        week_end
    )
    
    # Hourly data directories for today
    today_start = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
    today_end = today_start + datetime.timedelta(days=1)
    
    hourly_dirs = datepathlist(
        "/gps_data/%Y/%m/%d/hour_%H/",
        "1H",
        today_start,
        today_end
    )
    
    return {
        'current_yearf': current_yearf,
        'daily_dirs': daily_dirs,
        'hourly_dirs': hourly_dirs[:6]  # First 6 hours
    }

# Example usage
data_org = organize_realtime_data()
print(f"Current fractional year: {data_org['current_yearf']:.6f}")
print(f"Daily processing directories: {len(data_org['daily_dirs'])}")
print(f"Hourly data directories: {len(data_org['hourly_dirs'])}")
```

## Performance Notes

### Efficient Date Range Processing

For large date ranges, use appropriate frequency strings to avoid excessive memory usage:

```python
import datetime
from gtimes.timefunc import datepathlist

# For large ranges, be mindful of frequency
start = datetime.datetime(2020, 1, 1)
end = datetime.datetime(2024, 1, 1)

# Daily over 4 years = ~1460 items (manageable)
daily_files = datepathlist("data_%Y%m%d.dat", "1D", start, end)
print(f"Daily files: {len(daily_files)} items")

# Hourly over 4 years = ~35,000 items (use with caution)
# hourly_files = datepathlist("data_%Y%m%d_%H.dat", "1H", start, end)
```

### Fractional Year Precision

Fractional year conversions maintain high precision for scientific applications:

```python
from gtimes.timefunc import TimefromYearf, dTimetoYearf
import datetime

# Test precision
original_dt = datetime.datetime(2024, 6, 15, 14, 30, 45, 123456)
yearf = dTimetoYearf(original_dt)
converted_dt = TimefromYearf(yearf)

time_diff = abs((converted_dt - original_dt).total_seconds())
print(f"Roundtrip precision error: {time_diff} seconds")
# Typically less than 1 second for fractional year conversions
```