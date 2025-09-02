"""Integration tests using real GPS data scenarios and workflows."""

import datetime
import numpy as np
import pytest

from gtimes.gpstime import UTCFromGps, gpsFromUTC, GpsSecondsFromPyUTC
from gtimes.timefunc import (
    dTimetoYearf, TimefromYearf, currDatetime, 
    datepathlist, convfromYearf
)


@pytest.mark.integration
class TestRealGNSSWorkflows:
    """Test workflows that match real GNSS processing scenarios."""

    def test_rinex_filename_generation(self):
        """Test RINEX filename generation workflow used in GPS processing."""
        # Test the workflow for generating RINEX filenames for a GPS station
        base_date = datetime.datetime(2015, 10, 1, 0, 0, 0)
        
        # Generate a series of daily RINEX filenames
        date_list = datepathlist(
            stringformat="VONC%j0.%yO",  # RINEX filename pattern
            lfrequency="1D",
            periods=7,
            epoch=base_date
        )
        
        assert len(date_list) == 7
        
        # Check first filename
        first_file = date_list[0]
        assert "VONC" in first_file
        assert "15O" in first_file  # Year 2015 -> 15
        
        # Check that all filenames are unique
        assert len(set(date_list)) == len(date_list)

    def test_gamit_time_series_processing(self):
        """Test time series processing workflow used in GAMIT processing."""
        # Create fractional year time series (typical GAMIT output format)
        start_year = 2020.0
        end_year = 2020.5
        num_points = 100
        
        yearf_series = np.linspace(start_year, end_year, num_points)
        
        # Convert to datetime objects (typical preprocessing step)
        datetime_series = convfromYearf(yearf_series)
        
        assert len(datetime_series) == num_points
        assert all(isinstance(dt, datetime.datetime) for dt in datetime_series)
        
        # Check time progression
        for i in range(1, len(datetime_series)):
            assert datetime_series[i] > datetime_series[i-1]
        
        # Convert back to verify roundtrip
        yearf_recovered = np.array([dTimetoYearf(dt) for dt in datetime_series])
        
        # Should be very close (within numerical precision)
        np.testing.assert_allclose(yearf_series, yearf_recovered, rtol=1e-10)

    def test_gps_station_monitoring_workflow(self):
        """Test workflow for GPS station data monitoring."""
        # Simulate processing GPS observations from multiple days
        observation_dates = [
            datetime.datetime(2020, 1, 1, 12, 0, 0),
            datetime.datetime(2020, 1, 2, 12, 0, 0),
            datetime.datetime(2020, 1, 3, 12, 0, 0),
        ]
        
        gps_data = []
        for obs_date in observation_dates:
            # Convert to GPS time (typical for GPS processing)
            gps_week, sow = gpsFromUTC(*obs_date.timetuple()[:6])
            
            # Convert to GPS seconds (another common format)
            gps_seconds = GpsSecondsFromPyUTC(obs_date.timestamp())
            
            gps_data.append({
                'datetime': obs_date,
                'gps_week': gps_week,
                'sow': sow,
                'gps_seconds': gps_seconds
            })
        
        # Verify all conversions are consistent
        for data in gps_data:
            # Convert GPS week/SOW back to datetime
            recovered_dt = UTCFromGps(data['gps_week'], data['sow'], dtimeObj=True)
            
            # Should match original datetime
            time_diff = abs((recovered_dt - data['datetime']).total_seconds())
            assert time_diff < 1e-6

    def test_leap_second_handling_real_dates(self):
        """Test leap second handling with real leap second dates."""
        # Test around real leap second events
        leap_second_dates = [
            datetime.datetime(1999, 1, 1, 0, 0, 0),   # Leap second Dec 31, 1998
            datetime.datetime(2006, 1, 1, 0, 0, 0),   # Leap second Dec 31, 2005
            datetime.datetime(2009, 1, 1, 0, 0, 0),   # Leap second Dec 31, 2008
            datetime.datetime(2012, 7, 1, 0, 0, 0),   # Leap second June 30, 2012
            datetime.datetime(2015, 7, 1, 0, 0, 0),   # Leap second June 30, 2015
            datetime.datetime(2017, 1, 1, 0, 0, 0),   # Leap second Dec 31, 2016
        ]
        
        for test_date in leap_second_dates:
            # Test GPS conversion around leap second dates
            gps_week, sow = gpsFromUTC(*test_date.timetuple()[:6])
            
            # Convert back
            recovered_dt = UTCFromGps(gps_week, sow, dtimeObj=True)
            
            # Should be very close despite leap second complexity
            time_diff = abs((recovered_dt - test_date).total_seconds())
            assert time_diff < 1.0  # Within 1 second tolerance


@pytest.mark.integration
class TestDataProcessingPipelines:
    """Test complete data processing pipelines."""

    def test_daily_processing_pipeline(self):
        """Test a typical daily GPS data processing pipeline."""
        # Simulate processing a week of GPS data
        start_date = datetime.datetime(2020, 6, 15, 0, 0, 0)
        
        # Generate processing epochs (every 30 seconds for 1 day)
        epochs = []
        current_time = start_date
        for _ in range(24 * 60 * 2):  # 24 hours * 60 minutes * 2 (30-sec intervals)
            epochs.append(current_time)
            current_time += datetime.timedelta(seconds=30)
        
        # Convert all to fractional years (GAMIT format)
        yearf_data = np.array([dTimetoYearf(epoch) for epoch in epochs])
        
        # Verify data consistency
        assert len(yearf_data) == len(epochs)
        assert np.all(np.diff(yearf_data) > 0)  # Monotonically increasing
        
        # Verify time span is approximately 1 day
        time_span = yearf_data[-1] - yearf_data[0]
        expected_span = 1.0 / 365.25  # Approximately 1 day in years
        assert abs(time_span - expected_span) < 0.001

    def test_multi_station_processing(self):
        """Test processing data from multiple GPS stations."""
        stations = ['REYK', 'HOFN', 'AKUR', 'VMEY']  # Icelandic GPS stations
        base_date = datetime.datetime(2020, 1, 1, 12, 0, 0)
        
        station_data = {}
        for station in stations:
            # Generate RINEX filenames for each station
            filenames = datepathlist(
                stringformat=f"{station}%j0.%yD",
                lfrequency="1D",
                periods=30,  # One month
                epoch=base_date
            )
            
            # Generate corresponding GPS weeks
            gps_weeks = []
            current_date = base_date
            for _ in range(30):
                gps_week, _ = gpsFromUTC(*current_date.timetuple()[:6])
                gps_weeks.append(gps_week)
                current_date += datetime.timedelta(days=1)
            
            station_data[station] = {
                'filenames': filenames,
                'gps_weeks': gps_weeks
            }
        
        # Verify all stations have consistent data
        for station, data in station_data.items():
            assert len(data['filenames']) == 30
            assert len(data['gps_weeks']) == 30
            assert station in data['filenames'][0]
            
        # Verify GPS weeks are the same across all stations for same dates
        first_station_weeks = station_data[stations[0]]['gps_weeks']
        for station in stations[1:]:
            station_weeks = station_data[station]['gps_weeks']
            assert station_weeks == first_station_weeks

    def test_time_series_interpolation_workflow(self):
        """Test time series interpolation workflow common in GPS analysis."""
        # Create irregular time series (typical of real GPS data)
        base_time = datetime.datetime(2020, 1, 1, 0, 0, 0)
        irregular_times = []
        
        # Add some gaps and irregular spacing
        current_time = base_time
        for i in range(100):
            irregular_times.append(current_time)
            
            # Irregular intervals: sometimes 1 hour, sometimes 2-3 hours
            if i % 7 == 0:  # Introduce gaps
                current_time += datetime.timedelta(hours=6)
            elif i % 3 == 0:
                current_time += datetime.timedelta(hours=2)
            else:
                current_time += datetime.timedelta(hours=1)
        
        # Convert to fractional years
        yearf_irregular = np.array([dTimetoYearf(dt) for dt in irregular_times])
        
        # Create regular time grid for interpolation
        start_yearf = yearf_irregular[0]
        end_yearf = yearf_irregular[-1]
        regular_yearf = np.linspace(start_yearf, end_yearf, 200)
        
        # Convert back to datetime for validation
        regular_times = convfromYearf(regular_yearf)
        
        # Verify regular grid properties
        assert len(regular_times) == 200
        assert all(isinstance(dt, datetime.datetime) for dt in regular_times)
        
        # Check that regular grid spans the same time period
        time_span_original = irregular_times[-1] - irregular_times[0]
        time_span_regular = regular_times[-1] - regular_times[0]
        
        # Should be very close
        time_diff = abs((time_span_regular - time_span_original).total_seconds())
        assert time_diff < 3600  # Within 1 hour


@pytest.mark.integration
@pytest.mark.slow
class TestLongRunningProcesses:
    """Test long-running processes typical of GPS analysis."""

    def test_annual_processing(self):
        """Test processing a full year of GPS data."""
        # Generate daily epochs for a full year
        start_date = datetime.datetime(2020, 1, 1, 12, 0, 0)
        
        daily_epochs = []
        current_date = start_date
        while current_date.year == 2020:
            daily_epochs.append(current_date)
            current_date += datetime.timedelta(days=1)
        
        # Convert to fractional years
        yearf_annual = np.array([dTimetoYearf(epoch) for epoch in daily_epochs])
        
        # Verify properties
        assert len(yearf_annual) == 366  # 2020 is a leap year
        assert yearf_annual[0] >= 2020.0
        assert yearf_annual[-1] < 2021.0
        
        # Verify monotonic increase
        assert np.all(np.diff(yearf_annual) > 0)
        
        # Check that we span most of the year
        year_span = yearf_annual[-1] - yearf_annual[0]
        assert year_span > 0.99  # Should be very close to 1 full year

    def test_multi_year_time_series(self):
        """Test multi-year time series processing."""
        # Generate monthly epochs for 5 years
        start_date = datetime.datetime(2018, 1, 1, 12, 0, 0)
        
        monthly_epochs = []
        current_date = start_date
        for year in range(2018, 2023):
            for month in range(1, 13):
                epoch_date = datetime.datetime(year, month, 15, 12, 0, 0)  # Mid-month
                monthly_epochs.append(epoch_date)
        
        # Convert to fractional years
        yearf_series = np.array([dTimetoYearf(epoch) for epoch in monthly_epochs])
        
        # Verify time series properties
        assert len(yearf_series) == 5 * 12  # 5 years * 12 months
        assert yearf_series[0] >= 2018.0
        assert yearf_series[-1] < 2023.0
        
        # Check approximate 5-year span
        time_span = yearf_series[-1] - yearf_series[0]
        assert 4.8 < time_span < 5.2  # Should be close to 5 years


@pytest.mark.integration 
class TestEdgeCases:
    """Test edge cases and boundary conditions in real scenarios."""

    def test_year_boundary_processing(self):
        """Test processing across year boundaries."""
        # Test around New Year's Eve/Day transition
        test_times = [
            datetime.datetime(2019, 12, 31, 23, 59, 59),
            datetime.datetime(2020, 1, 1, 0, 0, 0),
            datetime.datetime(2020, 1, 1, 0, 0, 1),
        ]
        
        for test_time in test_times:
            # Convert to GPS time and back
            gps_week, sow = gpsFromUTC(*test_time.timetuple()[:6])
            recovered_dt = UTCFromGps(gps_week, sow, dtimeObj=True)
            
            # Should be very close
            time_diff = abs((recovered_dt - test_time).total_seconds())
            assert time_diff < 1e-6
            
            # Also test fractional year conversion
            yearf = dTimetoYearf(test_time)
            recovered_from_yearf = TimefromYearf(yearf)
            
            # Should be very close
            time_diff_yearf = abs((recovered_from_yearf - test_time).total_seconds())
            assert time_diff_yearf < 1.0

    def test_leap_year_boundary(self):
        """Test leap year boundary conditions."""
        # Test February 29th in leap years
        leap_year_dates = [
            datetime.datetime(2000, 2, 29, 12, 0, 0),
            datetime.datetime(2004, 2, 29, 12, 0, 0),
            datetime.datetime(2020, 2, 29, 12, 0, 0),
        ]
        
        for leap_date in leap_year_dates:
            # Should handle leap day correctly
            yearf = dTimetoYearf(leap_date)
            
            # Should be in appropriate position in the year
            # Feb 29 should be around day 60/366 ≈ 0.164 through the year
            year_fraction = yearf - int(yearf)
            assert 0.1 < year_fraction < 0.2
            
            # Round trip conversion
            recovered = TimefromYearf(yearf)
            assert recovered.year == leap_date.year
            assert recovered.month == leap_date.month
            assert recovered.day == leap_date.day

    def test_extreme_precision_requirements(self):
        """Test high-precision time handling for precise GPS applications."""
        # Test microsecond precision
        precise_time = datetime.datetime(2020, 6, 15, 12, 30, 45, 123456)
        
        # Convert to fractional year
        yearf = dTimetoYearf(precise_time)
        
        # Convert back (without rounding)
        recovered = TimefromYearf(yearf)
        
        # Should preserve precision to at least second level
        time_diff = abs((recovered - precise_time).total_seconds())
        assert time_diff < 1.0  # Within 1 second for fractional year conversion
        
        # GPS time conversion should be more precise
        gps_week, sow = gpsFromUTC(*precise_time.timetuple()[:6])
        gps_recovered = UTCFromGps(gps_week, sow, dtimeObj=True)
        
        gps_time_diff = abs((gps_recovered - precise_time).total_seconds())
        assert gps_time_diff < 1e-6  # Microsecond precision