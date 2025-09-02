# Basic Usage Examples

This page provides practical examples of the most common GTimes operations for GPS time processing.

## Time Conversion Examples

### Basic UTC ↔ GPS Conversions

```python
from gtimes.gpstime import gpsFromUTC, UTCFromGps
import datetime

# Example 1: Convert current time to GPS
now = datetime.datetime.utcnow()
gps_week, sow, gps_day, sod = gpsFromUTC(
    now.year, now.month, now.day,
    now.hour, now.minute, now.second + now.microsecond/1e6
)

print(f"Current UTC: {now}")
print(f"GPS Week: {gps_week}")
print(f"Seconds of Week: {sow:.6f}")
print(f"GPS Day: {gps_day} (0=Sunday)")

# Example 2: Convert GPS time back to UTC
utc_dt = UTCFromGps(gps_week, sow, dtimeObj=True)
print(f"Converted back: {utc_dt}")

# Example 3: High precision conversion
precise_time = datetime.datetime(2024, 6, 15, 14, 30, 45, 123456)
gps_result = gpsFromUTC(
    precise_time.year, precise_time.month, precise_time.day,
    precise_time.hour, precise_time.minute,
    precise_time.second + precise_time.microsecond/1e6
)
print(f"Microsecond precision: SOW = {gps_result[1]:.6f}")
```

### Working with Leap Seconds

```python
from gtimes.gpstime import getleapSecs, leapSecDict
import datetime

# Get leap seconds for different dates
dates = [
    datetime.datetime(1980, 1, 6),   # GPS epoch
    datetime.datetime(2000, 1, 1),   # Y2K
    datetime.datetime(2017, 1, 1),   # Recent leap second
    datetime.datetime(2024, 1, 1)    # Current era
]

print("Leap second history:")
for date in dates:
    utc_leap = getleapSecs(date, gpst=False)  # Total since 1972
    gps_leap = getleapSecs(date, gpst=True)   # Since GPS epoch
    print(f"{date.date()}: UTC={utc_leap}, GPS={gps_leap}")

# Show leap second dictionary
leap_dict = leapSecDict()
recent_leaps = list(leap_dict.items())[-5:]
print(f"\nRecent leap seconds: {recent_leaps}")
```

## Fractional Year Processing

### GAMIT Time Series Workflow

```python
from gtimes.timefunc import TimefromYearf, dTimetoYearf
import datetime

# Simulate GAMIT fractional year output
gamit_epochs = [
    2024.0000,    # Jan 1
    2024.0833,    # ~Feb 1  
    2024.1667,    # ~Mar 1
    2024.2500,    # ~Apr 1
    2024.3333,    # ~May 1
]

print("GAMIT Time Series Processing:")
print("Epoch (fractional)  ->  Date")
print("-" * 40)

processed_dates = []
for yearf in gamit_epochs:
    # Convert to datetime
    dt = TimefromYearf(yearf)
    processed_dates.append(dt)
    
    # Format for display
    date_str = TimefromYearf(yearf, String="%Y-%m-%d")
    print(f"{yearf:14.4f}  ->  {date_str}")

# Verify round-trip accuracy
print("\nRound-trip accuracy check:")
for i, dt in enumerate(processed_dates):
    original_yearf = gamit_epochs[i]
    computed_yearf = dTimetoYearf(dt)
    error = abs(computed_yearf - original_yearf)
    print(f"Original: {original_yearf:.6f}, Computed: {computed_yearf:.6f}, Error: {error:.8f}")
```

### Time Series Analysis

```python
from gtimes.timefunc import dTimetoYearf, TimefromYearf
import datetime
import math

def generate_time_series(start_year, duration_years, frequency_per_year=12):
    """Generate a time series with specified frequency."""
    time_points = []
    fractional_years = []
    
    for i in range(int(duration_years * frequency_per_year)):
        yearf = start_year + (i / frequency_per_year)
        dt = TimefromYearf(yearf)
        
        time_points.append(dt)
        fractional_years.append(yearf)
    
    return time_points, fractional_years

# Generate monthly time series for 2 years
dates, yearfs = generate_time_series(2023.0, 2.0, 12)

print(f"Generated {len(dates)} time points:")
print("Date                Fractional Year")
print("-" * 40)
for i in range(0, len(dates), 3):  # Show every 3rd point
    print(f"{dates[i].strftime('%Y-%m-%d %H:%M:%S')}  {yearfs[i]:12.6f}")

# Calculate statistics
yearf_span = yearfs[-1] - yearfs[0]
date_span = (dates[-1] - dates[0]).days
print(f"\nTime series span: {yearf_span:.4f} years ({date_span} days)")
```

## File Organization and RINEX Processing

### Daily RINEX File Generation

```python
from gtimes.timefunc import datepathlist
import datetime

def generate_station_files(station_code, start_date, num_days):
    """Generate RINEX filenames for a GPS station."""
    end_date = start_date + datetime.timedelta(days=num_days)
    
    # Generate different file types
    files = {
        'obs': datepathlist(f"{station_code}%j0.%yO", "1D", start_date, end_date),
        'nav': datepathlist(f"{station_code}%j0.%yN", "1D", start_date, end_date),
        'met': datepathlist(f"{station_code}%j0.%yM", "1D", start_date, end_date),
    }
    
    return files

# Example: Generate files for Icelandic stations
stations = ['REYK', 'HOFN', 'AKUR', 'VMEY']
start = datetime.datetime(2024, 1, 15, 0, 0, 0)

print("RINEX files for Icelandic GPS network:")
print("=" * 50)

for station in stations:
    files = generate_station_files(station, start, 5)
    
    print(f"\n{station} Station:")
    print("  Observation files:")
    for obs_file in files['obs']:
        print(f"    {obs_file}")
    
    print("  Navigation files:")
    for nav_file in files['nav'][:2]:  # Show first 2
        print(f"    {nav_file}")
```

### Processing Directory Structure

```python
from gtimes.timefunc import datepathlist, gpsWeekDay
import datetime

def create_processing_structure(base_path, start_date, num_weeks=4):
    """Create GPS processing directory structure."""
    end_date = start_date + datetime.timedelta(weeks=num_weeks)
    
    # Weekly processing directories
    weekly_dirs = datepathlist(f"{base_path}/%Y/week_%U/", "7D", start_date, end_date)
    
    # Daily subdirectories
    daily_dirs = datepathlist(f"{base_path}/%Y/%j/daily/", "1D", start_date, end_date)
    
    # GPS week-based organization
    gps_week_dirs = datepathlist(f"{base_path}/gps/week_#gpsw/", "7D", start_date, end_date)
    
    return {
        'weekly': weekly_dirs,
        'daily': daily_dirs[:7],  # First week only
        'gps_weekly': gps_week_dirs
    }

# Create processing structure
start = datetime.datetime(2024, 1, 15, 0, 0, 0)
structure = create_processing_structure("/gps_proc", start, 2)

print("GPS Processing Directory Structure:")
print("=" * 45)

print("\nWeekly directories:")
for dir_path in structure['weekly']:
    print(f"  {dir_path}")

print("\nDaily directories (first week):")
for dir_path in structure['daily']:
    print(f"  {dir_path}")
    
print("\nGPS week directories:")
for dir_path in structure['gps_weekly']:
    print(f"  {dir_path}")
```

## Command Line Integration

### Automating with Shell Scripts

Example shell script using timecalc:

```bash
#!/bin/bash
# gps_daily_processing.sh

STATION="REYK"
DATE="2024-01-15"

# Get GPS week and day for this date
GPS_INFO=$(timecalc -wd -d "$DATE")
GPS_WEEK=$(echo $GPS_INFO | cut -d' ' -f1)
GPS_DAY=$(echo $GPS_INFO | cut -d' ' -f2)

echo "Processing $STATION for $DATE"
echo "GPS Week: $GPS_WEEK, GPS Day: $GPS_DAY"

# Generate RINEX filename
RINEX_FILE=$(timecalc -l "${STATION}%j0.%yO" "0D" -d "$DATE" | head -1)
echo "RINEX file: $RINEX_FILE"

# Get fractional year for GAMIT
YEARF=$(timecalc -yf -d "$DATE")
echo "Fractional year: $YEARF"

# Create processing directory
PROC_DIR="/gps_proc/$(date -d "$DATE" +%Y/%j)"
echo "Processing directory: $PROC_DIR"
```

### Python wrapper for command line

```python
import subprocess
import datetime

def timecalc_wrapper(args):
    """Wrapper for timecalc command line tool."""
    cmd = ['timecalc'] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"timecalc failed: {result.stderr}")
    
    return result.stdout.strip()

# Example usage
date_str = "2024-01-15"

# Get GPS week and day
gps_wd = timecalc_wrapper(['-wd', '-d', date_str])
print(f"GPS Week/Day: {gps_wd}")

# Get fractional year
yearf = timecalc_wrapper(['-yf', '-d', date_str])
print(f"Fractional year: {yearf}")

# Get day of year
doy = timecalc_wrapper(['-j', '-d', date_str])
print(f"Day of year: {doy}")

# Generate file list
file_list = timecalc_wrapper(['-l', 'REYK%j0.%yO', '3D', '-d', date_str])
files = file_list.split('\n')
print(f"Generated {len(files)} files:")
for f in files:
    print(f"  {f}")
```

## Data Validation and Quality Control

### Time Stamp Validation

```python
from gtimes.gpstime import gpsFromUTC, UTCFromGps
from gtimes.exceptions import GPSTimeError
import datetime

def validate_observation_times(time_stamps):
    """Validate GPS observation time stamps."""
    valid_times = []
    invalid_times = []
    
    for i, ts in enumerate(time_stamps):
        try:
            # Try to convert to GPS time
            gps_week, sow, gps_day, sod = gpsFromUTC(
                ts.year, ts.month, ts.day,
                ts.hour, ts.minute, ts.second + ts.microsecond/1e6
            )
            
            # Verify round-trip conversion
            utc_back = UTCFromGps(gps_week, sow, dtimeObj=True)
            time_diff = abs((utc_back - ts).total_seconds())
            
            if time_diff < 1e-3:  # Within 1 millisecond
                valid_times.append((i, ts, gps_week, sow))
            else:
                invalid_times.append((i, ts, f"Round-trip error: {time_diff:.6f}s"))
                
        except GPSTimeError as e:
            invalid_times.append((i, ts, str(e)))
    
    return valid_times, invalid_times

# Test with various time stamps
test_times = [
    datetime.datetime(2024, 1, 15, 12, 30, 45, 123456),  # Valid
    datetime.datetime(1970, 1, 1, 0, 0, 0),               # Before GPS epoch
    datetime.datetime(2024, 2, 29, 12, 0, 0),             # Valid leap day
    datetime.datetime(2023, 2, 29, 12, 0, 0),             # Invalid leap day
    datetime.datetime(2024, 6, 15, 23, 59, 59, 999999),   # Valid edge case
]

valid, invalid = validate_observation_times(test_times)

print(f"Validation Results:")
print(f"Valid times: {len(valid)}")
print(f"Invalid times: {len(invalid)}")

print(f"\nValid time stamps:")
for idx, ts, week, sow in valid:
    print(f"  {idx}: {ts} -> Week {week}, SOW {sow:.6f}")

print(f"\nInvalid time stamps:")
for idx, ts, error in invalid:
    print(f"  {idx}: {ts} -> {error}")
```

### GPS Week Rollover Detection

```python
from gtimes.gpstime import gpsFromUTC
import datetime

def detect_gps_week_boundaries(start_date, days=14):
    """Detect GPS week boundaries in a date range."""
    boundaries = []
    current_week = None
    
    for i in range(days):
        date = start_date + datetime.timedelta(days=i)
        gps_week, sow, gps_day, sod = gpsFromUTC(
            date.year, date.month, date.day, 0, 0, 0
        )
        
        if current_week is None:
            current_week = gps_week
        elif current_week != gps_week:
            boundaries.append({
                'date': date,
                'old_week': current_week,
                'new_week': gps_week,
                'sow': sow
            })
            current_week = gps_week
    
    return boundaries

# Detect boundaries around known rollover dates
test_dates = [
    datetime.datetime(2019, 4, 5),   # Around second GPS rollover
    datetime.datetime(2024, 1, 13),  # Recent week boundary
]

for start_date in test_dates:
    print(f"\nGPS Week boundaries near {start_date.date()}:")
    boundaries = detect_gps_week_boundaries(start_date, 10)
    
    for boundary in boundaries:
        print(f"  {boundary['date'].date()}: Week {boundary['old_week']} -> {boundary['new_week']}")
```

## Performance Optimization

### Batch Processing Example

```python
from gtimes.gpstime import gpsFromUTC, leapSecDict
import time
import datetime

def benchmark_conversions(num_conversions=1000):
    """Benchmark GPS time conversions."""
    
    # Pre-load leap second dictionary
    leap_dict = leapSecDict()
    
    # Generate test data
    base_date = datetime.datetime(2024, 1, 1)
    test_dates = []
    
    for i in range(num_conversions):
        test_date = base_date + datetime.timedelta(days=i % 365, 
                                                   hours=i % 24,
                                                   minutes=i % 60)
        test_dates.append((test_date.year, test_date.month, test_date.day,
                          test_date.hour, test_date.minute, test_date.second))
    
    # Benchmark conversions
    start_time = time.time()
    results = []
    
    for date_tuple in test_dates:
        result = gpsFromUTC(*date_tuple)
        results.append(result)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    return {
        'num_conversions': num_conversions,
        'total_time': processing_time,
        'rate': num_conversions / processing_time,
        'avg_time_per_conversion': processing_time / num_conversions * 1000  # ms
    }

# Run benchmark
results = benchmark_conversions(1000)

print("GPS Time Conversion Performance:")
print(f"Conversions: {results['num_conversions']:,}")
print(f"Total time: {results['total_time']:.3f} seconds")
print(f"Rate: {results['rate']:.0f} conversions/second")
print(f"Average time per conversion: {results['avg_time_per_conversion']:.3f} ms")
```

These examples demonstrate the most common GTimes usage patterns. For more advanced scenarios, see the [API reference documentation](../api/gpstime.md) and other example pages.