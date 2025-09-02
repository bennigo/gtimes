#!/usr/bin/env python3
"""
Performance benchmarks for GTimes GPS time conversions.

This module provides comprehensive benchmarks for GPS time conversion
functions to track performance over time and detect regressions.
"""

import datetime
import random
import time
from typing import List, Tuple

import pytest

from gtimes.gpstime import gpsFromUTC, UTCFromGps, leapSecDict
from gtimes.timefunc import TimefromYearf, dTimetoYearf


class TestGPSConversionBenchmarks:
    """Benchmark suite for GPS time conversion functions."""
    
    @pytest.fixture(scope="class")
    def test_dates(self) -> List[Tuple[int, int, int, int, int, float]]:
        """Generate test dates for benchmarking."""
        dates = []
        base_date = datetime.datetime(2020, 1, 1)
        
        # Generate 1000 random dates over 5 years
        for _ in range(1000):
            random_days = random.randint(0, 365 * 5)
            random_hours = random.randint(0, 23)
            random_minutes = random.randint(0, 59)
            random_seconds = random.uniform(0, 59.999999)
            
            test_date = base_date + datetime.timedelta(
                days=random_days,
                hours=random_hours,
                minutes=random_minutes
            )
            
            dates.append((
                test_date.year,
                test_date.month,
                test_date.day,
                test_date.hour,
                test_date.minute,
                test_date.second + random_seconds
            ))
        
        return dates
    
    @pytest.fixture(scope="class")
    def gps_times(self, test_dates) -> List[Tuple[int, float]]:
        """Convert test dates to GPS times for reverse conversion benchmarks."""
        gps_times = []
        for date_tuple in test_dates[:100]:  # Smaller set for reverse conversion
            try:
                week, sow, _, _ = gpsFromUTC(*date_tuple)
                gps_times.append((week, sow))
            except:
                continue  # Skip invalid dates
        return gps_times
    
    @pytest.fixture(scope="class")
    def fractional_years(self) -> List[float]:
        """Generate fractional years for GAMIT benchmarks."""
        years = []
        for year in range(2020, 2025):
            for month in range(1, 13):
                yearf = year + (month - 1) / 12.0
                years.append(yearf)
        return years
    
    def test_benchmark_gps_from_utc_single(self, benchmark):
        """Benchmark single GPS time conversion."""
        test_date = (2024, 1, 15, 12, 30, 45.123456)
        
        result = benchmark(gpsFromUTC, *test_date)
        
        assert len(result) == 4
        assert isinstance(result[0], int)  # GPS week
        assert isinstance(result[1], float)  # SOW
    
    def test_benchmark_gps_from_utc_batch(self, benchmark, test_dates):
        """Benchmark batch GPS time conversions."""
        
        def batch_conversion(dates):
            results = []
            for date_tuple in dates:
                try:
                    result = gpsFromUTC(*date_tuple)
                    results.append(result)
                except:
                    continue  # Skip invalid dates
            return results
        
        results = benchmark(batch_conversion, test_dates)
        
        assert len(results) > 900  # Most should succeed
        assert all(len(result) == 4 for result in results)
    
    def test_benchmark_utc_from_gps_single(self, benchmark):
        """Benchmark single UTC conversion."""
        gps_week = 2297
        sow = 216645.123456
        
        result = benchmark(UTCFromGps, gps_week, sow, dtimeObj=True)
        
        assert isinstance(result, datetime.datetime)
    
    def test_benchmark_utc_from_gps_batch(self, benchmark, gps_times):
        """Benchmark batch UTC conversions."""
        
        def batch_conversion(gps_times_list):
            results = []
            for week, sow in gps_times_list:
                try:
                    result = UTCFromGps(week, sow, dtimeObj=True)
                    results.append(result)
                except:
                    continue
            return results
        
        results = benchmark(batch_conversion, gps_times)
        
        assert len(results) > 90  # Most should succeed
        assert all(isinstance(result, datetime.datetime) for result in results)
    
    def test_benchmark_round_trip_conversion(self, benchmark, test_dates):
        """Benchmark round-trip conversion accuracy."""
        
        def round_trip_conversion(dates):
            results = []
            for date_tuple in dates[:100]:  # Smaller set for round-trip
                try:
                    # UTC -> GPS
                    week, sow, _, _ = gpsFromUTC(*date_tuple)
                    
                    # GPS -> UTC
                    utc_back = UTCFromGps(week, sow, dtimeObj=True)
                    
                    # Calculate accuracy
                    original = datetime.datetime(*[
                        int(x) if i < 6 else x for i, x in enumerate(date_tuple)
                    ])
                    diff = abs((utc_back - original).total_seconds())
                    
                    results.append(diff)
                except:
                    continue
            return results
        
        differences = benchmark(round_trip_conversion, test_dates)
        
        assert len(differences) > 90
        assert max(differences) < 1e-3  # Within 1ms accuracy
        assert sum(differences) / len(differences) < 1e-6  # Average within 1μs
    
    def test_benchmark_leap_second_lookup(self, benchmark):
        """Benchmark leap second dictionary lookup."""
        
        def leap_second_lookup():
            leap_dict = leapSecDict()
            return len(leap_dict)
        
        result = benchmark(leap_second_lookup)
        
        assert result > 0
        assert isinstance(result, int)
    
    def test_benchmark_fractional_year_to_datetime(self, benchmark, fractional_years):
        """Benchmark fractional year to datetime conversion."""
        
        def batch_yearf_conversion(yearfs):
            results = []
            for yearf in yearfs:
                try:
                    dt = TimefromYearf(yearf)
                    results.append(dt)
                except:
                    continue
            return results
        
        results = benchmark(batch_yearf_conversion, fractional_years)
        
        assert len(results) > 50
        assert all(isinstance(result, datetime.datetime) for result in results)
    
    def test_benchmark_datetime_to_fractional_year(self, benchmark):
        """Benchmark datetime to fractional year conversion."""
        
        # Generate test datetimes
        test_datetimes = []
        for year in range(2020, 2025):
            for month in range(1, 13, 3):  # Every 3 months
                dt = datetime.datetime(year, month, 15, 12, 0, 0)
                test_datetimes.append(dt)
        
        def batch_dt_conversion(datetimes):
            results = []
            for dt in datetimes:
                try:
                    yearf = dTimetoYearf(dt)
                    results.append(yearf)
                except:
                    continue
            return results
        
        results = benchmark(batch_dt_conversion, test_datetimes)
        
        assert len(results) > 15
        assert all(isinstance(result, float) for result in results)
        assert all(2020 <= result < 2025 for result in results)
    
    def test_benchmark_mixed_operations(self, benchmark, test_dates):
        """Benchmark mixed GPS time operations."""
        
        def mixed_operations(dates):
            results = {
                'gps_conversions': 0,
                'utc_conversions': 0,
                'fractional_years': 0,
                'errors': 0
            }
            
            for i, date_tuple in enumerate(dates[:200]):  # Subset for mixed ops
                try:
                    # UTC -> GPS
                    week, sow, day, sod = gpsFromUTC(*date_tuple)
                    results['gps_conversions'] += 1
                    
                    # GPS -> UTC (every other)
                    if i % 2 == 0:
                        utc_back = UTCFromGps(week, sow, dtimeObj=True)
                        results['utc_conversions'] += 1
                    
                    # Fractional year (every third)
                    if i % 3 == 0:
                        dt = datetime.datetime(*[
                            int(x) if j < 6 else x for j, x in enumerate(date_tuple)
                        ])
                        yearf = dTimetoYearf(dt)
                        results['fractional_years'] += 1
                        
                except:
                    results['errors'] += 1
            
            return results
        
        results = benchmark(mixed_operations, test_dates)
        
        assert results['gps_conversions'] > 190
        assert results['utc_conversions'] > 90
        assert results['fractional_years'] > 60
        assert results['errors'] < 10
    
    def test_benchmark_memory_usage(self, benchmark, test_dates):
        """Benchmark memory efficiency of conversions."""
        import tracemalloc
        
        def memory_efficient_conversion(dates):
            tracemalloc.start()
            
            results = []
            for date_tuple in dates:
                try:
                    # Process without storing intermediate values
                    week, sow, _, _ = gpsFromUTC(*date_tuple)
                    results.append((week, sow))
                except:
                    continue
            
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            return len(results), current, peak
        
        count, current_mem, peak_mem = benchmark(memory_efficient_conversion, test_dates)
        
        assert count > 900
        # Memory usage should be reasonable (less than 10MB peak)
        assert peak_mem < 10 * 1024 * 1024


class TestPerformanceRegression:
    """Test for performance regressions."""
    
    def test_performance_baseline(self, benchmark):
        """Establish performance baseline for monitoring."""
        
        def baseline_operations():
            # Standard test case
            results = []
            
            # 100 GPS conversions
            base_date = datetime.datetime(2024, 1, 1)
            for i in range(100):
                test_date = base_date + datetime.timedelta(days=i)
                week, sow, _, _ = gpsFromUTC(
                    test_date.year, test_date.month, test_date.day,
                    12, 30, 45.123
                )
                results.append((week, sow))
            
            return len(results)
        
        count = benchmark(baseline_operations)
        assert count == 100
    
    @pytest.mark.slow
    def test_large_dataset_performance(self, benchmark):
        """Test performance with large datasets."""
        
        def large_dataset_processing():
            # Generate 10,000 dates
            results = []
            base_date = datetime.datetime(2020, 1, 1)
            
            for i in range(10000):
                days_offset = i % (365 * 5)  # 5 years
                hours = i % 24
                minutes = i % 60
                seconds = (i % 60) + (i % 1000) / 1000.0
                
                test_date = base_date + datetime.timedelta(days=days_offset)
                
                try:
                    week, sow, _, _ = gpsFromUTC(
                        test_date.year, test_date.month, test_date.day,
                        hours, minutes, seconds
                    )
                    results.append((week, sow))
                except:
                    continue
            
            return len(results)
        
        count = benchmark(large_dataset_processing)
        assert count > 9900  # Most should succeed


if __name__ == "__main__":
    # Run benchmarks standalone
    import subprocess
    import sys
    
    print("🏃 Running GTimes performance benchmarks...")
    
    # Run with pytest-benchmark
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__,
        "--benchmark-only",
        "--benchmark-sort=mean",
        "--benchmark-json=benchmark-results.json",
        "-v"
    ])
    
    sys.exit(result.returncode)