"""Shared test configuration and fixtures for gtimes test suite.

This module provides pytest fixtures and configuration used across multiple test modules.
"""

import datetime
import pytest
import sys
from pathlib import Path

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_datetime():
    """Provide a sample datetime for testing."""
    return datetime.datetime(2020, 6, 15, 14, 30, 45, 123456)


@pytest.fixture
def gps_epoch():
    """Provide the GPS epoch datetime."""
    return datetime.datetime(1980, 1, 6, 0, 0, 0)


@pytest.fixture
def sample_utc_times():
    """Provide a variety of UTC times for testing."""
    return [
        # GPS Epoch
        (1980, 1, 6, 0, 0, 0.0),
        # Y2K
        (2000, 1, 1, 0, 0, 0.0),
        # Recent date with fractional seconds
        (2020, 6, 15, 14, 30, 45.123),
        # Leap year
        (2020, 2, 29, 12, 0, 0.0),
        # End of month
        (2022, 1, 31, 18, 45, 30.0),
        # Mid-range date
        (2010, 7, 15, 9, 30, 15.0),
    ]


@pytest.fixture
def known_gps_times():
    """Provide known GPS time conversions for testing."""
    return [
        {
            'datetime': datetime.datetime(1980, 1, 6, 0, 0, 0),
            'gps_week': 0,
            'sow': 0.0,
            'yearf': 1980.0136986301369,  # Approximate
        },
        {
            'datetime': datetime.datetime(2000, 1, 1, 12, 0, 0),
            'gps_week': 1042,
            'sow': 561613.0,  # Correct calculated SOW
            'yearf': 2000.0,  # Approximate
        },
        {
            'datetime': datetime.datetime(2020, 1, 1, 0, 0, 0),
            'gps_week': 2086,
            'sow': 259218.0,  # Correct calculated SOW
            'yearf': 2020.0,
        }
    ]


@pytest.fixture
def sample_fractional_years():
    """Provide fractional years for testing."""
    return [2020.0, 2020.25, 2020.5, 2020.75, 2021.0, 1980.0, 2023.99726]


@pytest.fixture
def leap_year_dates():
    """Provide dates from various leap years for testing."""
    return [
        datetime.datetime(2000, 2, 29, 12, 0, 0),  # Century leap year
        datetime.datetime(2004, 2, 29, 12, 0, 0),  # Regular leap year
        datetime.datetime(2020, 2, 29, 12, 0, 0),  # Recent leap year
    ]


@pytest.fixture
def non_leap_year_dates():
    """Provide dates from non-leap years for testing."""
    return [
        datetime.datetime(1900, 2, 28, 12, 0, 0),  # Century non-leap year
        datetime.datetime(2001, 2, 28, 12, 0, 0),  # Regular non-leap year
        datetime.datetime(2021, 2, 28, 12, 0, 0),  # Recent non-leap year
    ]


@pytest.fixture
def icelandic_station_codes():
    """Provide Icelandic GPS station codes for realistic testing."""
    return ['REYK', 'HOFN', 'AKUR', 'VMEY', 'HVER', 'OLKE', 'SKRO']


@pytest.fixture
def rinex_filename_patterns():
    """Provide RINEX filename patterns for testing."""
    return [
        "%s%j0.%yO",      # Standard daily RINEX observation
        "%s%j0.%yD",      # Standard daily RINEX navigation
        "%s%j%H.%yO",     # Hourly RINEX observation
        "%s%j0.%y_.Z",    # Compressed RINEX
    ]


@pytest.fixture
def invalid_gps_inputs():
    """Provide invalid GPS time inputs for validation testing."""
    return {
        'negative_week': (-1, 388800.0),
        'excessive_week': (99999, 388800.0),
        'negative_sow': (2086, -1.0),
        'excessive_sow': (2086, 604800.0),
        'float_week': (2086.5, 388800.0),
        'string_week': ('2086', 388800.0),
        'string_sow': (2086, '388800'),
    }


@pytest.fixture
def invalid_utc_inputs():
    """Provide invalid UTC inputs for validation testing."""
    return {
        'invalid_year': (1900, 1, 1, 12, 0, 0),
        'future_year': (2200, 1, 1, 12, 0, 0),
        'invalid_month': (2020, 13, 1, 12, 0, 0),
        'invalid_day': (2020, 1, 32, 12, 0, 0),
        'invalid_hour': (2020, 1, 1, 24, 0, 0),
        'invalid_minute': (2020, 1, 1, 12, 60, 0),
        'invalid_second': (2020, 1, 1, 12, 0, 60.0),
    }


# Configure pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests for individual functions")
    config.addinivalue_line("markers", "integration: Integration tests with multiple components")
    config.addinivalue_line("markers", "performance: Performance and benchmark tests")
    config.addinivalue_line("markers", "edge_cases: Edge cases and boundary condition tests")
    config.addinivalue_line("markers", "cli: Command-line interface tests")
    config.addinivalue_line("markers", "validation: Input validation and error handling tests")
    config.addinivalue_line("markers", "slow: Tests that take longer to run")


# Skip slow tests by default unless explicitly requested
def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle slow tests."""
    if not config.getoption("--runslow"):
        skip_slow = pytest.mark.skip(reason="need --runslow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


def pytest_addoption(parser):
    """Add command line options."""
    parser.addoption(
        "--runslow",
        action="store_true",
        default=False,
        help="run slow tests"
    )


# Precision tolerance for floating-point comparisons
GPS_TIME_TOLERANCE = 1e-6  # Microsecond precision
FRACTIONAL_YEAR_TOLERANCE = 1e-8  # High precision for fractional years