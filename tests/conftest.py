"""Shared test configuration and fixtures for gtimes tests."""

import datetime
import pytest
import numpy as np


@pytest.fixture
def sample_datetime():
    """Provide a sample datetime for testing."""
    return datetime.datetime(2020, 6, 15, 14, 30, 45, 123456)


@pytest.fixture
def gps_epoch():
    """Provide the GPS epoch datetime."""
    return datetime.datetime(1980, 1, 6, 0, 0, 0)


@pytest.fixture
def known_gps_times():
    """Provide known GPS time conversions for testing."""
    return [
        {
            'datetime': datetime.datetime(1980, 1, 6, 0, 0, 0),
            'gps_week': 0,
            'sow': 0,
            'yearf': 1980.0136986301369,  # Approximate
        },
        {
            'datetime': datetime.datetime(2000, 1, 1, 12, 0, 0),
            'gps_week': 1043,
            'sow': 388800,  # 4 days * 24 hours * 3600 seconds + 12 hours * 3600
            'yearf': 2000.0,  # Approximate
        },
        {
            'datetime': datetime.datetime(2020, 1, 1, 0, 0, 0),
            'gps_week': 2086,
            'sow': 345600,  # 4 days * 24 hours * 3600 seconds
            'yearf': 2020.0,
        }
    ]


@pytest.fixture
def sample_yearf_array():
    """Provide a sample fractional year array for vectorization tests."""
    return np.array([2020.0, 2020.25, 2020.5, 2020.75, 2021.0])


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


# Configure pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual functions"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests with real GPS data scenarios"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer to run"
    )


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