# Quick Start Guide

Get up and running with GTimes in minutes. This guide covers the most common GPS time processing tasks.

## Installation

```bash
pip install gtimes
```

For development with testing capabilities:
```bash  
pip install gtimes[dev]
```

## Basic GPS Time Conversions

### UTC to GPS Time

```python
from gtimes.gpstime import gpsFromUTC

# Convert UTC to GPS time
year, month, day = 2024, 1, 15
hour, minute, second = 12, 30, 45.123

gps_week, sow, gps_day, sod = gpsFromUTC(year, month, day, hour, minute, second)

print(f"GPS Week: {gps_week}")          # GPS Week: 2297
print(f"Seconds of Week: {sow}")        # Seconds of Week: 216645.123
print(f"GPS Day: {gps_day}")            # GPS Day: 1 (Monday) 
print(f"Seconds of Day: {sod}")         # Seconds of Day: 45045.123
```

### GPS Time to UTC

```python
from gtimes.gpstime import UTCFromGps

# Convert GPS time back to UTC
gps_week, sow = 2297, 216645.123

# Get datetime object
utc_datetime = UTCFromGps(gps_week, sow, dtimeObj=True)
print(f"UTC DateTime: {utc_datetime}")  # 2024-01-15 12:30:45.123000

# Get tuple format
utc_tuple = UTCFromGps(gps_week, sow, dtimeObj=False)
print(f"UTC Tuple: {utc_tuple}")        # (2024, 1, 15, 12, 30, 45.123)
```

## Working with Fractional Years

Fractional years are commonly used in GAMIT/GLOBK processing for geodetic time series.

### DateTime to Fractional Year

```python
from gtimes.timefunc import dTimetoYearf
import datetime

# Convert datetime to fractional year
dt = datetime.datetime(2024, 7, 1, 12, 0, 0)  # Mid-year
yearf = dTimetoYearf(dt)
print(f"Fractional year: {yearf:.6f}")  # 2024.497260
```

### Fractional Year to DateTime

```python
from gtimes.timefunc import TimefromYearf

# Convert fractional year back to datetime
yearf = 2024.497260
dt = TimefromYearf(yearf)
print(f"DateTime: {dt}")  # 2024-07-01 11:56:02.976000

# Format as string
date_str = TimefromYearf(yearf, String="%Y-%m-%d %H:%M:%S")
print(f"Formatted: {date_str}")  # 2024-07-01 11:56:02

# Round to nearest hour
dt_rounded = TimefromYearf(yearf, rhour=True)
print(f"Rounded: {dt_rounded}")  # 2024-07-01 12:00:00
```

## Command Line Usage

GTimes includes a powerful command-line tool for quick time calculations:

```bash
# Get current GPS week and day
timecalc -wd
# Output: 2297 001

# Convert specific date to GPS time
timecalc -wd -d "2024-01-15"
# Output: 2297 001

# Get fractional year for a date  
timecalc -yf -d "2024-07-01"
# Output: 2024.497260

# Get day of year
timecalc -j -d "2024-01-15" 
# Output: 015

# Date arithmetic - add 30 days
timecalc -D 30 -d "2024-01-15"
# Output: Mon, 14. Feb 2024
```

### Generate File Lists

Generate RINEX filenames for processing:

```bash
# Generate daily RINEX files for a week
timecalc -l "REYK%j0.%yO" "1D" -d "2024-01-15"
# Output:
# REYK0150.24O
# REYK0160.24O
# REYK0170.24O
# ...
```

## RINEX File Processing

Common workflow for RINEX file processing:

```python
from gtimes.timefunc import datepathlist
import datetime

# Generate RINEX filenames for a GPS station
station = "REYK"
start_date = datetime.datetime(2024, 1, 15, 0, 0, 0)
end_date = datetime.datetime(2024, 1, 18, 0, 0, 0)

# Daily observation files
obs_files = datepathlist(f"{station}%j0.%yO", "1D", start_date, end_date)
print("RINEX Observation files:")
for filename in obs_files:
    print(f"  {filename}")

# Output:
#   REYK0150.24O
#   REYK0160.24O  
#   REYK0170.24O
```

### Advanced RINEX Processing

```python
from gtimes.gpstime import gpsFromUTC
from gtimes.timefunc import gpsWeekDay
import datetime

def process_rinex_observation(obs_datetime):
    """Process a RINEX observation time."""
    # Convert to GPS time
    gps_week, sow, gps_day, sod = gpsFromUTC(
        obs_datetime.year, obs_datetime.month, obs_datetime.day,
        obs_datetime.hour, obs_datetime.minute, 
        obs_datetime.second + obs_datetime.microsecond/1e6
    )
    
    return {
        'datetime': obs_datetime,
        'gps_week': gps_week,
        'seconds_of_week': sow,
        'gps_day': gps_day,
        'seconds_of_day': sod
    }

# Process observation
obs_time = datetime.datetime(2024, 1, 15, 12, 30, 45, 123456)
result = process_rinex_observation(obs_time)

print(f"Observation: {result['datetime']}")
print(f"GPS Week: {result['gps_week']}")
print(f"SOW: {result['seconds_of_week']:.6f}")
print(f"GPS Day: {result['gps_day']} (0=Sunday)")
print(f"SOD: {result['seconds_of_day']:.6f}")
```

## GPS Processing Pipeline Example

Complete example of a GPS processing workflow:

```python
from gtimes.gpstime import gpsFromUTC, UTCFromGps
from gtimes.timefunc import dTimetoYearf, TimefromYearf, datepathlist
import datetime

def gps_processing_pipeline(station_id, start_date, num_days=7):
    """Example GPS processing pipeline."""
    
    # 1. Generate processing period
    end_date = start_date + datetime.timedelta(days=num_days)
    print(f"Processing {station_id} from {start_date.date()} to {end_date.date()}")
    
    # 2. Convert to fractional years for GAMIT processing
    start_yearf = dTimetoYearf(start_date)
    end_yearf = dTimetoYearf(end_date)
    print(f"Fractional year range: {start_yearf:.6f} to {end_yearf:.6f}")
    
    # 3. Generate GPS time information
    gps_week, sow, gps_day, sod = gpsFromUTC(
        start_date.year, start_date.month, start_date.day,
        start_date.hour, start_date.minute, start_date.second
    )
    print(f"Processing starts at GPS Week {gps_week}, SOW {sow}")
    
    # 4. Generate required data files
    rinex_files = datepathlist(f"{station_id}%j0.%yO", "1D", start_date, end_date)
    nav_files = datepathlist(f"{station_id}%j0.%yN", "1D", start_date, end_date)
    
    # 5. Create processing directories
    proc_dirs = datepathlist(f"/gps_proc/%Y/%j/{station_id}/", "1D", start_date, end_date)
    
    return {
        'station': station_id,
        'start_yearf': start_yearf,
        'end_yearf': end_yearf,
        'gps_week': gps_week,
        'start_sow': sow,
        'rinex_files': rinex_files,
        'nav_files': nav_files,
        'proc_directories': proc_dirs
    }

# Run processing pipeline
start = datetime.datetime(2024, 1, 15, 0, 0, 0)
pipeline_result = gps_processing_pipeline("REYK", start, num_days=3)

print("\nGenerated files:")
print("RINEX observations:")
for f in pipeline_result['rinex_files']:
    print(f"  {f}")
    
print("Navigation files:")  
for f in pipeline_result['nav_files']:
    print(f"  {f}")
```

## Error Handling

GTimes provides comprehensive error handling with informative messages:

```python
from gtimes.gpstime import gpsFromUTC, UTCFromGps
from gtimes.exceptions import GPSTimeError, ValidationError

# Handle invalid dates
try:
    # Date before GPS epoch
    gpsFromUTC(1900, 1, 1, 12, 0, 0)
except GPSTimeError as e:
    print(f"GPS time error: {e}")

# Handle invalid GPS time
try:
    # Negative GPS week
    UTCFromGps(-1, 388800)
except GPSTimeError as e:
    print(f"Validation error: {e}")

# Handle invalid fractional years
from gtimes.timefunc import TimefromYearf
from gtimes.exceptions import FractionalYearError

try:
    # Year outside valid range
    TimefromYearf(1900.0)
except FractionalYearError as e:
    print(f"Fractional year error: {e}")
```

## Performance Tips

### Batch Processing

For processing many dates, GPS time conversions are highly optimized:

```python
from gtimes.gpstime import gpsFromUTC
import time

# Process large batch of dates
dates = [(2024, 1, i%28+1, 12, i%60, i%60) for i in range(1000)]

start_time = time.time()
gps_times = [gpsFromUTC(*date) for date in dates]
processing_time = time.time() - start_time

print(f"Processed {len(dates)} conversions in {processing_time:.3f} seconds")
print(f"Rate: {len(dates)/processing_time:.0f} conversions/second")
```

### Leap Second Caching

The leap second dictionary is cached for optimal performance:

```python
from gtimes.gpstime import leapSecDict

# First call loads and caches data
leap_dict = leapSecDict()
print(f"Loaded {len(leap_dict)} leap second entries")

# Subsequent calls use cached data (much faster)
leap_dict_cached = leapSecDict()
```

## Next Steps

- **[GPS Concepts Guide](gps-concepts.md)**: Learn about GPS time systems and coordinate frames
- **[Common Workflows](workflows.md)**: Real-world GPS processing examples  
- **[API Reference](../api/gpstime.md)**: Detailed function documentation
- **[Examples](../examples/basic-usage.md)**: More comprehensive code examples

## Common Use Cases

### Real-time GPS Processing
```python
from gtimes.timefunc import currYearfDate
import datetime

# Get current time in various formats
now = datetime.datetime.utcnow()
current_yearf = currYearfDate()
gps_week, sow, _, _ = gpsFromUTC(now.year, now.month, now.day, 
                                 now.hour, now.minute, now.second)

print(f"Current time: {now}")
print(f"Fractional year: {current_yearf:.6f}")  
print(f"GPS time: Week {gps_week}, SOW {sow:.0f}")
```

### Data Archive Organization
```python
from gtimes.timefunc import datepathlist
import datetime

# Organize data by GPS week
start = datetime.datetime(2024, 1, 1)
end = datetime.datetime(2024, 2, 1)

weekly_dirs = datepathlist("/archive/%Y/gps_week_#gpsw/", "7D", start, end)
print("Weekly archive directories:")
for dir_path in weekly_dirs:
    print(f"  {dir_path}")
```

This quick start guide covers the essential GPS time processing tasks. For more advanced usage and detailed examples, explore the other documentation sections.