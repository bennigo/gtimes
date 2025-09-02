"""Custom exceptions for GPS time processing."""

from typing import Any, Optional


class GTimesError(Exception):
    """Base exception for all gtimes errors."""
    
    def __init__(self, message: str, context: Optional[dict] = None):
        self.message = message
        self.context = context or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} (Context: {context_str})"
        return self.message


class GPSTimeError(GTimesError):
    """Errors in GPS time conversion operations."""
    pass


class LeapSecondError(GPSTimeError):
    """Errors related to leap second handling."""
    pass


class FractionalYearError(GTimesError):
    """Errors in fractional year conversions."""
    pass


class DateRangeError(GTimesError):
    """Errors when date/time values are outside valid ranges."""
    pass


class FormatError(GTimesError):
    """Errors in string formatting operations."""
    pass


class ValidationError(GTimesError):
    """Input validation errors."""
    pass


def validate_gps_week(gps_week: int) -> int:
    """Validate GPS week number.
    
    Args:
        gps_week: GPS week number to validate
        
    Returns:
        int: Validated GPS week number
        
    Raises:
        ValidationError: If GPS week is invalid
    """
    if not isinstance(gps_week, int):
        raise ValidationError(
            "GPS week must be an integer",
            {"provided_type": type(gps_week).__name__, "value": gps_week}
        )
    
    if gps_week < 0:
        raise ValidationError(
            "GPS week cannot be negative",
            {"gps_week": gps_week}
        )
    
    # GPS week rollover occurs at 1024 weeks, but we support full range
    if gps_week > 9999:  # Reasonable upper bound
        raise ValidationError(
            "GPS week is unreasonably large",
            {"gps_week": gps_week, "max_supported": 9999}
        )
    
    return gps_week


def validate_seconds_of_week(sow: float) -> float:
    """Validate seconds of week value.
    
    Args:
        sow: Seconds of week to validate
        
    Returns:
        float: Validated seconds of week
        
    Raises:
        ValidationError: If SOW is invalid
    """
    if not isinstance(sow, (int, float)):
        raise ValidationError(
            "Seconds of week must be numeric",
            {"provided_type": type(sow).__name__, "value": sow}
        )
    
    if sow < 0:
        raise ValidationError(
            "Seconds of week cannot be negative",
            {"sow": sow}
        )
    
    # There are 604800 seconds in a week
    if sow >= 604800:
        raise ValidationError(
            "Seconds of week must be less than 604800",
            {"sow": sow, "max_sow": 604799.999}
        )
    
    return float(sow)


def validate_utc_components(year: int, month: int, day: int, 
                          hour: int, minute: int, second: float) -> tuple[int, int, int, int, int, float]:
    """Validate UTC date/time components.
    
    Args:
        year: Year (1980-2100)
        month: Month (1-12)
        day: Day (1-31)
        hour: Hour (0-23)
        minute: Minute (0-59)
        second: Second (0-59.999...)
        
    Returns:
        tuple: Validated (year, month, day, hour, minute, second)
        
    Raises:
        ValidationError: If any component is invalid
    """
    # Validate types
    if not isinstance(year, int):
        raise ValidationError("Year must be an integer", {"year": year})
    if not isinstance(month, int):
        raise ValidationError("Month must be an integer", {"month": month})
    if not isinstance(day, int):
        raise ValidationError("Day must be an integer", {"day": day})
    if not isinstance(hour, int):
        raise ValidationError("Hour must be an integer", {"hour": hour})
    if not isinstance(minute, int):
        raise ValidationError("Minute must be an integer", {"minute": minute})
    if not isinstance(second, (int, float)):
        raise ValidationError("Second must be numeric", {"second": second})
    
    # Validate ranges
    if not (1980 <= year <= 2100):
        raise ValidationError(
            "Year must be between 1980 and 2100",
            {"year": year, "valid_range": "1980-2100"}
        )
    
    if not (1 <= month <= 12):
        raise ValidationError(
            "Month must be between 1 and 12",
            {"month": month}
        )
    
    if not (1 <= day <= 31):
        raise ValidationError(
            "Day must be between 1 and 31",
            {"day": day}
        )
    
    if not (0 <= hour <= 23):
        raise ValidationError(
            "Hour must be between 0 and 23",
            {"hour": hour}
        )
    
    if not (0 <= minute <= 59):
        raise ValidationError(
            "Minute must be between 0 and 59",
            {"minute": minute}
        )
    
    if not (0 <= second < 60):
        raise ValidationError(
            "Second must be between 0 and 59.999...",
            {"second": second}
        )
    
    return year, month, day, hour, minute, float(second)


def validate_fractional_year(yearf: float) -> float:
    """Validate fractional year value.
    
    Args:
        yearf: Fractional year to validate
        
    Returns:
        float: Validated fractional year
        
    Raises:
        ValidationError: If fractional year is invalid
    """
    if not isinstance(yearf, (int, float)):
        raise ValidationError(
            "Fractional year must be numeric",
            {"provided_type": type(yearf).__name__, "value": yearf}
        )
    
    # Reasonable range for GPS applications
    if not (1980.0 <= yearf <= 2100.0):
        raise ValidationError(
            "Fractional year must be between 1980.0 and 2100.0",
            {"yearf": yearf, "valid_range": "1980.0-2100.0"}
        )
    
    return float(yearf)


def validate_leap_seconds(leap_secs: int) -> int:
    """Validate leap seconds count.
    
    Args:
        leap_secs: Number of leap seconds
        
    Returns:
        int: Validated leap seconds count
        
    Raises:
        ValidationError: If leap seconds count is invalid
    """
    if not isinstance(leap_secs, int):
        raise ValidationError(
            "Leap seconds must be an integer",
            {"provided_type": type(leap_secs).__name__, "value": leap_secs}
        )
    
    # Historical range: 0 (at GPS epoch) to ~25 (reasonable future bound)
    if not (0 <= leap_secs <= 25):
        raise ValidationError(
            "Leap seconds must be between 0 and 25",
            {"leap_secs": leap_secs, "valid_range": "0-25"}
        )
    
    return leap_secs