"""Tests for flexible datetime parsing function."""

import pytest
import datetime
from gtimes.timefunc import parse_datetime_flexible


class TestParseDatetimeFlexible:
    """Test the parse_datetime_flexible function with various datetime formats."""
    
    def test_space_separated_formats(self):
        """Test space-separated datetime formats."""
        # Basic format
        result = parse_datetime_flexible('2023-08-25 14:30')
        expected = datetime.datetime(2023, 8, 25, 14, 30)
        assert result == expected
        
        # With seconds
        result = parse_datetime_flexible('2023-08-25 14:30:45')
        expected = datetime.datetime(2023, 8, 25, 14, 30, 45)
        assert result == expected
        
        # With microseconds
        result = parse_datetime_flexible('2023-08-25 14:30:45.123456')
        expected = datetime.datetime(2023, 8, 25, 14, 30, 45, 123456)
        assert result == expected
    
    def test_iso_t_separated_formats(self):
        """Test ISO T-separated datetime formats."""
        # Standard ISO format
        result = parse_datetime_flexible('2023-08-25T14:30:45')
        expected = datetime.datetime(2023, 8, 25, 14, 30, 45)
        assert result == expected
        
        # ISO without seconds
        result = parse_datetime_flexible('2023-08-25T14:30')
        expected = datetime.datetime(2023, 8, 25, 14, 30)
        assert result == expected
        
        # ISO with microseconds
        result = parse_datetime_flexible('2023-08-25T14:30:45.123456')
        expected = datetime.datetime(2023, 8, 25, 14, 30, 45, 123456)
        assert result == expected
    
    def test_z_suffix_handling(self):
        """Test handling of Z suffix (UTC indicator)."""
        result = parse_datetime_flexible('2023-08-25T14:30:45Z')
        expected = datetime.datetime(2023, 8, 25, 14, 30, 45)
        assert result == expected
        
        result = parse_datetime_flexible('2023-08-25T14:30Z')
        expected = datetime.datetime(2023, 8, 25, 14, 30)
        assert result == expected
    
    def test_milliseconds_handling(self):
        """Test handling of milliseconds (3-digit precision)."""
        result = parse_datetime_flexible('2023-08-25T14:30:45.123')
        expected = datetime.datetime(2023, 8, 25, 14, 30, 45, 123000)
        assert result == expected
        
        result = parse_datetime_flexible('2023-08-25T14:30:45.123Z')
        expected = datetime.datetime(2023, 8, 25, 14, 30, 45, 123000)
        assert result == expected
    
    def test_date_only_format(self):
        """Test date-only format."""
        result = parse_datetime_flexible('2023-08-25')
        expected = datetime.datetime(2023, 8, 25)
        assert result == expected
    
    def test_whitespace_handling(self):
        """Test that leading/trailing whitespace is handled."""
        result = parse_datetime_flexible('  2023-08-25T14:30:45  ')
        expected = datetime.datetime(2023, 8, 25, 14, 30, 45)
        assert result == expected
    
    def test_truncation_handling(self):
        """Test handling of strings that need truncation (e.g., nanoseconds)."""
        # Nanosecond precision should be truncated to microseconds
        result = parse_datetime_flexible('2023-08-25T14:30:45.123456789')
        expected = datetime.datetime(2023, 8, 25, 14, 30, 45, 123456)
        assert result == expected
    
    def test_tostools_specific_formats(self):
        """Test formats specifically encountered in tostools."""
        # Original TOS API format
        result = parse_datetime_flexible('2023-08-25 14:30')
        expected = datetime.datetime(2023, 8, 25, 14, 30)
        assert result == expected
        
        # New ISO format from TOS API
        result = parse_datetime_flexible('2023-08-25T14:30:00')
        expected = datetime.datetime(2023, 8, 25, 14, 30, 0)
        assert result == expected
    
    def test_error_cases(self):
        """Test error handling for invalid inputs."""
        with pytest.raises(ValueError, match="Expected string"):
            parse_datetime_flexible(None)
            
        with pytest.raises(ValueError, match="Expected string"):
            parse_datetime_flexible(123)
            
        with pytest.raises(ValueError, match="Unable to parse datetime string"):
            parse_datetime_flexible('invalid-date-format')
            
        with pytest.raises(ValueError, match="Unable to parse datetime string"):
            parse_datetime_flexible('2023-13-45 25:70:80')  # Invalid values
            
        with pytest.raises(ValueError, match="Unable to parse datetime string"):
            parse_datetime_flexible('')  # Empty string
    
    def test_type_validation(self):
        """Test that only strings are accepted."""
        with pytest.raises(ValueError):
            parse_datetime_flexible(datetime.datetime.now())
            
        with pytest.raises(ValueError):
            parse_datetime_flexible(123456)
            
        with pytest.raises(ValueError):
            parse_datetime_flexible(['2023-08-25'])
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Leap year
        result = parse_datetime_flexible('2024-02-29T12:00:00')
        expected = datetime.datetime(2024, 2, 29, 12, 0, 0)
        assert result == expected
        
        # Year boundaries
        result = parse_datetime_flexible('1999-12-31T23:59:59')
        expected = datetime.datetime(1999, 12, 31, 23, 59, 59)
        assert result == expected
        
        result = parse_datetime_flexible('2000-01-01T00:00:00')
        expected = datetime.datetime(2000, 1, 1, 0, 0, 0)
        assert result == expected