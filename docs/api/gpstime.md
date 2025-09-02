# GPS Time Conversions API

The `gtimes.gpstime` module provides the core functionality for converting between GPS time and UTC time systems, handling leap seconds, and working with various GPS time representations.

## Overview

GPS time is a continuous atomic time scale that began at 00:00:00 UTC on January 6, 1980 (the GPS epoch). Unlike UTC, GPS time does not include leap seconds, making it essential for precise timing applications in GNSS processing.

## Core Functions

::: gtimes.gpstime.gpsFromUTC
    options:
      show_source: true
      heading_level: 3

::: gtimes.gpstime.UTCFromGps
    options:
      show_source: true
      heading_level: 3

::: gtimes.gpstime.GpsSecondsFromPyUTC
    options:
      show_source: true  
      heading_level: 3

## Leap Second Management

::: gtimes.gpstime.getleapSecs
    options:
      show_source: true
      heading_level: 3

::: gtimes.gpstime.leapSecDict
    options:
      show_source: true
      heading_level: 3

## Utility Functions

::: gtimes.gpstime.ymdhmsFromPyUTC
    options:
      show_source: true
      heading_level: 3

## Constants

The module defines several important constants:

- `secsInWeek = 604800`: Number of seconds in a GPS week
- `secsInDay = 86400`: Number of seconds in a day  
- `gpsEpoch = (1980, 1, 6, 0, 0, 0)`: GPS epoch as a tuple
- `epochTuple`: GPS epoch formatted for time functions

## Usage Examples

### Basic GPS Time Conversion

```python
from gtimes.gpstime import gpsFromUTC, UTCFromGps

# Convert UTC to GPS time
gps_week, sow, gps_day, sod = gpsFromUTC(2024, 1, 15, 12, 30, 45.123)
print(f"GPS Week: {gps_week}")          # GPS Week: 2297
print(f"Seconds of Week: {sow}")        # Seconds of Week: 216645.123
print(f"GPS Day: {gps_day}")            # GPS Day: 1 (Monday)
print(f"Seconds of Day: {sod}")         # Seconds of Day: 45045.123

# Convert back to UTC
utc_datetime = UTCFromGps(gps_week, sow, dtimeObj=True)
print(f"UTC DateTime: {utc_datetime}")  # 2024-01-15 12:30:45.123000

utc_tuple = UTCFromGps(gps_week, sow, dtimeObj=False)
print(f"UTC Tuple: {utc_tuple}")        # (2024, 1, 15, 12, 30, 45.123)
```

### Working with Leap Seconds

```python
from gtimes.gpstime import getleapSecs, leapSecDict
import datetime

# Get leap seconds for a specific date
date = datetime.datetime(2024, 1, 15)
leap_secs_utc = getleapSecs(date, gpst=False)  # Total leap seconds since 1972
leap_secs_gps = getleapSecs(date, gpst=True)   # Leap seconds since GPS epoch

print(f"Leap seconds (UTC): {leap_secs_utc}")  # 37 (as of 2024)
print(f"Leap seconds (GPS): {leap_secs_gps}")  # 18 (37 - 19 from GPS epoch)

# Get the leap second dictionary
leap_dict = leapSecDict()
print(f"Latest leap second dates: {list(leap_dict.keys())[-3:]}")
```

### Handling Fractional Seconds

```python
from gtimes.gpstime import gpsFromUTC, UTCFromGps

# GPS time handles fractional seconds precisely
year, month, day = 2024, 7, 1
hour, minute, second = 14, 30, 45.123456

gps_week, sow, gps_day, sod = gpsFromUTC(year, month, day, hour, minute, second)

# Fractional seconds are preserved in SOW and SOD
print(f"SOW fractional part: {sow % 1}")  # 0.123456
print(f"SOD fractional part: {sod % 1}")  # 0.123456

# Round-trip conversion maintains precision
utc_result = UTCFromGps(gps_week, sow, dtimeObj=False)
print(f"Original seconds: {second}")
print(f"Round-trip seconds: {utc_result[5]}")
print(f"Precision error: {abs(utc_result[5] - second)} seconds")
```

### Manual Leap Second Specification

```python
from gtimes.gpstime import gpsFromUTC

# Manually specify leap seconds (useful for historical analysis)
gps_week, sow, _, _ = gpsFromUTC(2024, 1, 15, 12, 0, 0, leapSecs=18)

# Or let the system determine automatically (recommended)
gps_week_auto, sow_auto, _, _ = gpsFromUTC(2024, 1, 15, 12, 0, 0)

print(f"Manual leap seconds: Week {gps_week}, SOW {sow}")
print(f"Auto leap seconds: Week {gps_week_auto}, SOW {sow_auto}")
```

### GPS Week Rollover Handling

GPS weeks are represented as full weeks since the GPS epoch, not modulo 1024. The library handles GPS week rollovers transparently:

```python
from gtimes.gpstime import gpsFromUTC

# Dates around GPS week rollovers
rollover_date_1 = gpsFromUTC(1999, 8, 22, 0, 0, 0)  # First rollover
rollover_date_2 = gpsFromUTC(2019, 4, 7, 0, 0, 0)   # Second rollover

print(f"First rollover: Week {rollover_date_1[0]}")   # Week 1024
print(f"Second rollover: Week {rollover_date_2[0]}")  # Week 2048
```

## Error Handling

The GPS time functions include comprehensive input validation:

```python
from gtimes.gpstime import gpsFromUTC, UTCFromGps
from gtimes.exceptions import GPSTimeError

try:
    # Invalid date components
    gpsFromUTC(1900, 1, 1, 12, 0, 0)  # Year before GPS epoch
except GPSTimeError as e:
    print(f"Date validation error: {e}")

try:
    # Invalid GPS time
    UTCFromGps(-1, 388800)  # Negative GPS week
except GPSTimeError as e:
    print(f"GPS time validation error: {e}")
```

## Performance Considerations

### Leap Second Caching

The `leapSecDict()` function uses LRU caching for optimal performance:

```python
from gtimes.gpstime import leapSecDict
import time

# First call loads and caches the dictionary
start = time.time()
leap_dict_1 = leapSecDict()
first_call_time = time.time() - start

# Subsequent calls use cached data
start = time.time()  
leap_dict_2 = leapSecDict()
cached_call_time = time.time() - start

print(f"First call: {first_call_time:.6f} seconds")
print(f"Cached call: {cached_call_time:.6f} seconds")
# Cached calls are typically 100-1000x faster
```

### Batch Processing

For processing large datasets, GPS time conversions are highly optimized:

```python
from gtimes.gpstime import gpsFromUTC
import time

# Example: Convert 1000 dates
dates = [(2024, 1, i%30+1, 12, i%60, i%60) for i in range(1000)]

start = time.time()
gps_times = [gpsFromUTC(*date) for date in dates]
processing_time = time.time() - start

print(f"Processed {len(dates)} conversions in {processing_time:.3f} seconds")
print(f"Rate: {len(dates)/processing_time:.0f} conversions/second")
```

## Scientific Applications

### RINEX File Processing

```python
from gtimes.gpstime import gpsFromUTC
import datetime

def rinex_observation_time(dt):
    """Convert datetime to RINEX observation time format."""
    gps_week, sow, gps_day, sod = gpsFromUTC(
        dt.year, dt.month, dt.day, 
        dt.hour, dt.minute, dt.second + dt.microsecond/1e6
    )
    return gps_week, sow

# Example usage
obs_time = datetime.datetime(2024, 1, 15, 12, 30, 45, 123456)
week, sow = rinex_observation_time(obs_time)
print(f"RINEX GPS time: Week {week}, SOW {sow:.6f}")
```

### GPS Network Synchronization

```python
from gtimes.gpstime import gpsFromUTC, UTCFromGps
import datetime

def synchronize_station_data(station_times):
    """Synchronize data from multiple GPS stations to common GPS time."""
    synchronized_data = []
    
    for station_id, utc_time in station_times.items():
        gps_week, sow, _, _ = gpsFromUTC(
            utc_time.year, utc_time.month, utc_time.day,
            utc_time.hour, utc_time.minute, 
            utc_time.second + utc_time.microsecond/1e6
        )
        synchronized_data.append({
            'station': station_id,
            'gps_week': gps_week,
            'sow': sow,
            'utc_time': utc_time
        })
    
    return synchronized_data

# Example usage
station_times = {
    'REYK': datetime.datetime(2024, 1, 15, 12, 30, 45, 123000),
    'HOFN': datetime.datetime(2024, 1, 15, 12, 30, 45, 127000),
    'AKUR': datetime.datetime(2024, 1, 15, 12, 30, 45, 125000)
}

synced_data = synchronize_station_data(station_times)
for data in synced_data:
    print(f"{data['station']}: Week {data['gps_week']}, SOW {data['sow']:.6f}")
```