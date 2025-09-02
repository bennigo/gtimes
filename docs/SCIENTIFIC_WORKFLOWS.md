# Scientific Workflow Examples

This document provides real-world examples of using gtimes for GPS/GNSS data processing workflows at Veðurstofan Íslands and similar scientific applications.

## Daily GPS Processing Pipeline

### Workflow Overview
This example demonstrates the daily processing of GPS data from multiple Icelandic stations, converting raw observations through time format conversions commonly used in geodetic analysis.

```python
import datetime
import numpy as np
from gtimes.gpstime import gpsFromUTC, UTCFromGps
from gtimes.timefunc import dTimetoYearf, TimefromYearf, datepathlist

def daily_gps_processing_pipeline(processing_date, stations):
    """Complete daily GPS processing workflow."""
    
    # 1. Generate RINEX filenames for all stations
    rinex_files = {}
    for station in stations:
        files = datepathlist(
            stringformat=f"{station}%j0.%yO",
            lfrequency="1D",
            starttime=processing_date,
            periods=1
        )
        rinex_files[station] = files[0]
    
    # 2. Convert processing date to various time formats
    gps_week, sow, gps_day, sod = gpsFromUTC(*processing_date.timetuple()[:6])
    fractional_year = dTimetoYearf(processing_date)
    
    # 3. Generate processing epochs (every 30 seconds)
    processing_epochs = []
    current_time = processing_date
    for i in range(2880):  # 24 hours * 60 min * 2 (30-sec epochs)
        processing_epochs.append(current_time)
        current_time += datetime.timedelta(seconds=30)
    
    # 4. Convert all epochs to fractional years (GAMIT format)
    epoch_yearfs = [dTimetoYearf(epoch) for epoch in processing_epochs]
    
    results = {
        'processing_date': processing_date,
        'gps_week': gps_week,
        'sow': sow,
        'fractional_year': fractional_year,
        'rinex_files': rinex_files,
        'processing_epochs': len(processing_epochs),
        'yearf_span': (min(epoch_yearfs), max(epoch_yearfs))
    }
    
    return results

# Example usage
if __name__ == "__main__":
    stations = ['REYK', 'HOFN', 'AKUR', 'VMEY']
    processing_date = datetime.datetime(2020, 6, 15, 0, 0, 0)
    
    results = daily_gps_processing_pipeline(processing_date, stations)
    
    print(f"Processing Date: {results['processing_date']}")
    print(f"GPS Week/SOW: {results['gps_week']}/{results['sow']}")
    print(f"Fractional Year: {results['fractional_year']:.6f}")
    print(f"RINEX Files: {results['rinex_files']}")
```

## GAMIT Time Series Analysis

### Multi-Year Position Time Series
This example shows how to process multi-year GPS position time series data using fractional year representations.

```python
import numpy as np
import matplotlib.pyplot as plt
from gtimes.timefunc import dTimetoYearf, convfromYearf, TimefromYearf

def process_gamit_time_series(start_year, end_year, station_code):
    """Process multi-year GAMIT time series data."""
    
    # 1. Generate synthetic time series (replace with real GAMIT output)
    num_points = int((end_year - start_year) * 365.25 / 7)  # Weekly epochs
    yearf_series = np.linspace(start_year, end_year, num_points)
    
    # Simulate position variations (in mm)
    # Real data would come from GAMIT .pos files
    north_mm = 10 * np.sin(2 * np.pi * (yearf_series - start_year)) + \
               2 * np.random.randn(num_points)
    east_mm = 5 * np.cos(2 * np.pi * (yearf_series - start_year)) + \
              2 * np.random.randn(num_points)
    up_mm = 15 * np.sin(4 * np.pi * (yearf_series - start_year)) + \
            5 * np.random.randn(num_points)
    
    # 2. Convert fractional years to datetime objects for plotting
    datetime_series = convfromYearf(yearf_series)
    
    # 3. Analysis: detect seasonal signals
    annual_cycle_north = np.mean([north_mm[i] for i, yf in enumerate(yearf_series) 
                                  if (yf % 1) < 0.1])  # Winter signal
    annual_cycle_summer = np.mean([north_mm[i] for i, yf in enumerate(yearf_series) 
                                   if 0.4 < (yf % 1) < 0.6])  # Summer signal
    
    seasonal_amplitude = annual_cycle_summer - annual_cycle_north
    
    results = {
        'station': station_code,
        'time_span': f"{start_year}-{end_year}",
        'epochs': len(yearf_series),
        'datetime_series': datetime_series,
        'yearf_series': yearf_series,
        'positions': {
            'north_mm': north_mm,
            'east_mm': east_mm, 
            'up_mm': up_mm
        },
        'seasonal_amplitude_mm': seasonal_amplitude,
        'rms_north': np.std(north_mm),
        'rms_east': np.std(east_mm),
        'rms_up': np.std(up_mm)
    }
    
    return results

# Example usage with plotting
results = process_gamit_time_series(2018, 2023, 'REYK')

# Plot time series
fig, axes = plt.subplots(3, 1, figsize=(12, 8))
components = ['north_mm', 'east_mm', 'up_mm']
labels = ['North (mm)', 'East (mm)', 'Up (mm)']

for i, (comp, label) in enumerate(zip(components, labels)):
    axes[i].plot(results['datetime_series'], results['positions'][comp], 'b-', alpha=0.7)
    axes[i].set_ylabel(label)
    axes[i].grid(True, alpha=0.3)

axes[0].set_title(f"GPS Time Series - Station {results['station']}")
axes[2].set_xlabel('Date')
plt.tight_layout()
plt.show()

print(f"Station: {results['station']}")
print(f"Time span: {results['time_span']}")  
print(f"Seasonal amplitude: {results['seasonal_amplitude_mm']:.2f} mm")
print(f"RMS scatter: N={results['rms_north']:.2f}, E={results['rms_east']:.2f}, U={results['rms_up']:.2f} mm")
```

## Real-Time GPS Monitoring

### Station Health Monitoring
This example shows real-time GPS station monitoring with time format conversions.

```python
import datetime
from gtimes.gpstime import gpsFromUTC, getleapSecs
from gtimes.timefunc import currDatetime

class GPSStationMonitor:
    """Real-time GPS station monitoring system."""
    
    def __init__(self, station_codes):
        self.stations = station_codes
        self.monitoring_start = datetime.datetime.utcnow()
        
    def check_station_status(self, station_code):
        """Check current status of a GPS station."""
        current_time = datetime.datetime.utcnow()
        
        # Convert to GPS time for processing
        gps_week, sow, gps_day, sod = gpsFromUTC(*current_time.timetuple()[:6])
        leap_secs = getleapSecs(current_time)
        
        # Simulate data availability check (replace with real data query)
        data_delay_minutes = np.random.randint(0, 30)  # 0-30 min delay
        data_available = data_delay_minutes < 15  # Good if < 15 min delay
        
        # Calculate observation epochs expected (30-second intervals)
        elapsed_minutes = (current_time - current_time.replace(hour=0, minute=0, second=0)).seconds // 60
        expected_epochs = elapsed_minutes * 2  # 2 per minute (30-sec intervals)
        actual_epochs = expected_epochs - (data_delay_minutes * 2)
        
        status = {
            'station': station_code,
            'timestamp_utc': current_time,
            'gps_week': gps_week,
            'sow': sow,
            'leap_seconds': leap_secs,
            'data_available': data_available,
            'data_delay_minutes': data_delay_minutes,
            'expected_epochs': expected_epochs,
            'actual_epochs': max(0, actual_epochs),
            'data_completeness': max(0, actual_epochs) / expected_epochs if expected_epochs > 0 else 0
        }
        
        return status
    
    def generate_daily_report(self):
        """Generate daily monitoring report."""
        report_time = datetime.datetime.utcnow()
        
        print(f"GPS Station Daily Report - {report_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print("=" * 60)
        
        for station in self.stations:
            status = self.check_station_status(station)
            
            print(f"Station: {station}")
            print(f"  GPS Week/SOW: {status['gps_week']}/{status['sow']:.0f}")
            print(f"  Data Status: {'✓ GOOD' if status['data_available'] else '✗ DELAYED'}")
            print(f"  Data Delay: {status['data_delay_minutes']} minutes")
            print(f"  Completeness: {status['data_completeness']:.1%}")
            print()

# Example usage
if __name__ == "__main__":
    stations = ['REYK', 'HOFN', 'AKUR', 'VMEY']
    monitor = GPSStationMonitor(stations)
    monitor.generate_daily_report()
```

## RINEX File Management

### Automated RINEX Processing
This example demonstrates automated RINEX file generation and management.

```python
import os
import datetime
from gtimes.timefunc import datepathlist, currDatetime

class RINEXManager:
    """Automated RINEX file management system."""
    
    def __init__(self, base_path, stations):
        self.base_path = base_path
        self.stations = stations
        
    def generate_file_paths(self, start_date, days, file_type='O'):
        """Generate RINEX file paths for processing."""
        
        file_paths = {}
        
        for station in self.stations:
            # Generate daily file sequence
            files = datepathlist(
                stringformat=f"{self.base_path}/%Y/%j/{station}/%{station}%j0.%y{file_type}",
                lfrequency="1D",
                starttime=start_date,
                periods=days
            )
            file_paths[station] = files
            
        return file_paths
    
    def generate_hourly_files(self, processing_date, station):
        """Generate hourly RINEX files for high-rate processing."""
        
        hourly_files = datepathlist(
            stringformat=f"{station}%j%H.%yO",
            lfrequency="1H", 
            starttime=processing_date,
            periods=24  # 24 hours
        )
        
        return hourly_files
    
    def archive_old_files(self, cutoff_date):
        """Archive files older than cutoff date."""
        
        # Generate archive paths
        archive_paths = {}
        current_date = cutoff_date
        
        # Go back 30 days for archiving
        for i in range(30):
            archive_date = current_date - datetime.timedelta(days=i)
            
            for station in self.stations:
                archive_files = datepathlist(
                    stringformat=f"archive/%Y/%j/{station}_%j_%y.tar.gz",
                    lfrequency="1D",
                    starttime=archive_date,
                    periods=1
                )
                
                if station not in archive_paths:
                    archive_paths[station] = []
                archive_paths[station].extend(archive_files)
        
        return archive_paths

# Example usage
if __name__ == "__main__":
    stations = ['REYK', 'HOFN', 'AKUR']
    rinex_manager = RINEXManager('/data/gps', stations)
    
    # Generate file paths for a week of processing
    start_date = datetime.datetime(2020, 6, 15)
    file_paths = rinex_manager.generate_file_paths(start_date, days=7)
    
    print("Generated RINEX file paths:")
    for station, files in file_paths.items():
        print(f"\\n{station}:")
        for file_path in files:
            print(f"  {file_path}")
    
    # Generate hourly files for high-rate processing
    hourly_files = rinex_manager.generate_hourly_files(start_date, 'REYK')
    print(f"\\nHourly files for REYK:")
    for file_path in hourly_files[:6]:  # Show first 6 hours
        print(f"  {file_path}")
```

## Leap Second Handling

### Critical Time Period Processing
This example shows how to handle leap second transitions in GPS processing.

```python
import datetime
from gtimes.gpstime import gpsFromUTC, UTCFromGps, getleapSecs

def process_leap_second_transition(leap_second_date):
    """Process data around leap second transitions."""
    
    # Define time window around leap second (±1 hour)
    before_leap = leap_second_date - datetime.timedelta(hours=1)
    after_leap = leap_second_date + datetime.timedelta(hours=1)
    
    # Generate test epochs every minute
    test_epochs = []
    current_time = before_leap
    while current_time <= after_leap:
        test_epochs.append(current_time)
        current_time += datetime.timedelta(minutes=1)
    
    results = []
    
    for epoch in test_epochs:
        # Get leap second count for this epoch
        leap_secs = getleapSecs(epoch)
        
        # Convert to GPS time and back
        gps_week, sow, _, _ = gpsFromUTC(*epoch.timetuple()[:6])
        utc_recovered = UTCFromGps(gps_week, sow, dtimeObj=True)
        
        # Calculate time difference
        time_diff = abs((utc_recovered - epoch).total_seconds())
        
        results.append({
            'utc_epoch': epoch,
            'leap_seconds': leap_secs,
            'gps_week': gps_week,
            'sow': sow,
            'time_diff_sec': time_diff,
            'conversion_ok': time_diff < 1e-6
        })
    
    return results

# Example for 2017 leap second
leap_date = datetime.datetime(2017, 1, 1, 0, 0, 0)
results = process_leap_second_transition(leap_date)

print(f"Leap Second Transition Analysis - {leap_date}")
print("=" * 50)

for i, result in enumerate(results[::10]):  # Show every 10th result
    status = "✓" if result['conversion_ok'] else "✗"
    print(f"{result['utc_epoch']} | Leap: {result['leap_seconds']} | "
          f"Diff: {result['time_diff_sec']:.2e}s {status}")
```

## Performance Benchmarking

### Large Dataset Processing
This example benchmarks gtimes performance with large datasets.

```python
import time
import numpy as np
from gtimes.timefunc import dTimetoYearf, convfromYearf, TimefromYearf

def benchmark_time_conversions(num_points=10000):
    """Benchmark time conversion performance."""
    
    print(f"Benchmarking gtimes with {num_points} data points...")
    
    # Generate test dataset
    start_year = 2020.0
    end_year = 2023.0
    yearf_data = np.linspace(start_year, end_year, num_points)
    
    # Benchmark 1: Fractional year to datetime conversion
    start_time = time.time()
    datetime_results = convfromYearf(yearf_data)
    yearf_to_dt_time = time.time() - start_time
    
    # Benchmark 2: Datetime to fractional year conversion  
    start_time = time.time()
    yearf_recovered = np.array([dTimetoYearf(dt) for dt in datetime_results])
    dt_to_yearf_time = time.time() - start_time
    
    # Benchmark 3: Roundtrip accuracy
    max_error = np.max(np.abs(yearf_data - yearf_recovered))
    mean_error = np.mean(np.abs(yearf_data - yearf_recovered))
    
    results = {
        'num_points': num_points,
        'yearf_to_dt_sec': yearf_to_dt_time,
        'dt_to_yearf_sec': dt_to_yearf_time,
        'total_time_sec': yearf_to_dt_time + dt_to_yearf_time,
        'points_per_sec': num_points / (yearf_to_dt_time + dt_to_yearf_time),
        'max_error': max_error,
        'mean_error': mean_error,
        'accuracy_ok': max_error < 1e-10
    }
    
    return results

# Run benchmarks
for size in [1000, 10000, 100000]:
    results = benchmark_time_conversions(size)
    
    print(f"\\nDataset size: {results['num_points']:,} points")
    print(f"Total time: {results['total_time_sec']:.3f} seconds")
    print(f"Throughput: {results['points_per_sec']:.0f} points/second")
    print(f"Max error: {results['max_error']:.2e}")
    print(f"Accuracy: {'✓ PASS' if results['accuracy_ok'] else '✗ FAIL'}")
```

These examples demonstrate real-world usage patterns of the gtimes library in scientific GPS/GNSS processing workflows. They can be adapted for specific applications at Veðurstofan Íslands and similar institutions.