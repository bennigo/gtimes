# Exception Handling API

The `gtimes.exceptions` module provides comprehensive error handling and input validation for GPS time processing operations.

## Exception Hierarchy

GTimes uses a structured exception hierarchy to provide specific error information:

```
GTimesError (base class)
├── GPSTimeError (GPS time conversion errors)  
│   └── LeapSecondError (leap second related errors)
├── FractionalYearError (fractional year conversion errors)
├── DateRangeError (date/time outside valid ranges)
├── FormatError (string formatting errors)
└── ValidationError (input validation errors)
```

## Core Exceptions

::: gtimes.exceptions.GTimesError
    options:
      show_source: true
      heading_level: 3

::: gtimes.exceptions.GPSTimeError
    options:
      show_source: true
      heading_level: 3

::: gtimes.exceptions.ValidationError
    options:
      show_source: true
      heading_level: 3

::: gtimes.exceptions.FractionalYearError
    options:
      show_source: true
      heading_level: 3

## Validation Functions

::: gtimes.exceptions.validate_gps_week
    options:
      show_source: true
      heading_level: 3

::: gtimes.exceptions.validate_seconds_of_week
    options:
      show_source: true
      heading_level: 3

::: gtimes.exceptions.validate_utc_components
    options:
      show_source: true
      heading_level: 3

::: gtimes.exceptions.validate_fractional_year
    options:
      show_source: true
      heading_level: 3

::: gtimes.exceptions.validate_leap_seconds
    options:
      show_source: true
      heading_level: 3

## Usage Examples

### Basic Error Handling

```python
from gtimes.gpstime import gpsFromUTC, UTCFromGps
from gtimes.exceptions import GPSTimeError, ValidationError

try:
    # Attempt GPS time conversion with invalid date
    result = gpsFromUTC(1900, 1, 1, 12, 0, 0)  # Before GPS epoch
except GPSTimeError as e:
    print(f"GPS conversion failed: {e}")
    # Output: GPS conversion failed: Invalid UTC components: Year must be between 1980 and 2100 (Context: year=1900, valid_range=1980-2100)

try:
    # Invalid GPS time
    result = UTCFromGps(-5, 388800)  # Negative GPS week
except GPSTimeError as e:
    print(f"UTC conversion failed: {e}")
    # Output: UTC conversion failed: Invalid GPS time: GPS week cannot be negative (Context: gps_week=-5)
```

### Detailed Error Context

All GTimes exceptions include detailed context information:

```python
from gtimes.exceptions import ValidationError, validate_gps_week

try:
    validate_gps_week(-10)
except ValidationError as e:
    print(f"Error message: {e.message}")
    print(f"Error context: {e.context}")
    print(f"Full error: {e}")

# Output:
# Error message: GPS week cannot be negative
# Error context: {'gps_week': -10}
# Full error: GPS week cannot be negative (Context: gps_week=-10)
```

### Input Validation

Use validation functions to check inputs before processing:

```python
from gtimes.exceptions import (
    validate_gps_week, validate_seconds_of_week,
    validate_utc_components, ValidationError
)

def safe_gps_conversion(year, month, day, hour, minute, second):
    """Safely convert UTC to GPS with validation."""
    try:
        # Validate UTC components
        validated_components = validate_utc_components(
            year, month, day, hour, minute, second
        )
        
        # If validation passes, perform conversion
        from gtimes.gpstime import gpsFromUTC
        return gpsFromUTC(*validated_components)
        
    except ValidationError as e:
        print(f"Validation failed: {e}")
        return None

# Test with various inputs
test_cases = [
    (2024, 1, 15, 12, 30, 45),     # Valid
    (1900, 1, 1, 12, 0, 0),        # Invalid year
    (2024, 13, 1, 12, 0, 0),       # Invalid month
    (2024, 1, 32, 12, 0, 0),       # Invalid day
]

for test_case in test_cases:
    result = safe_gps_conversion(*test_case)
    if result:
        print(f"{test_case} -> GPS Week {result[0]}, SOW {result[1]}")
```

### Fractional Year Validation

```python
from gtimes.timefunc import TimefromYearf
from gtimes.exceptions import FractionalYearError

def process_gamit_epochs(fractional_years):
    """Process GAMIT fractional year epochs with error handling."""
    processed = []
    errors = []
    
    for i, yearf in enumerate(fractional_years):
        try:
            dt = TimefromYearf(yearf)
            processed.append((yearf, dt))
        except FractionalYearError as e:
            errors.append((i, yearf, str(e)))
    
    return processed, errors

# Test with mixed valid/invalid fractional years
test_epochs = [2020.0, 2020.5, 1900.0, 2024.123, 2200.0, 2023.999]
processed, errors = process_gamit_epochs(test_epochs)

print(f"Processed {len(processed)} valid epochs:")
for yearf, dt in processed:
    print(f"  {yearf:.3f} -> {dt.strftime('%Y-%m-%d %H:%M:%S')}")

print(f"\nFound {len(errors)} invalid epochs:")
for idx, yearf, error in errors:
    print(f"  {idx}: {yearf} -> {error}")
```

### Custom Error Handling

Create custom error handling for specific workflows:

```python
from gtimes.exceptions import GPSTimeError, ValidationError
import datetime

class GPSProcessingError(Exception):
    """Custom exception for GPS processing workflows."""
    pass

def robust_gps_processing(station_data):
    """Process GPS station data with comprehensive error handling."""
    processed_data = []
    processing_errors = []
    
    for station_id, time_stamps in station_data.items():
        station_results = []
        
        for i, timestamp in enumerate(time_stamps):
            try:
                # Attempt GPS time conversion
                from gtimes.gpstime import gpsFromUTC
                
                if isinstance(timestamp, datetime.datetime):
                    result = gpsFromUTC(
                        timestamp.year, timestamp.month, timestamp.day,
                        timestamp.hour, timestamp.minute, 
                        timestamp.second + timestamp.microsecond/1e6
                    )
                    station_results.append({
                        'timestamp': timestamp,
                        'gps_week': result[0],
                        'sow': result[1],
                        'status': 'success'
                    })
                else:
                    raise GPSProcessingError(f"Invalid timestamp type: {type(timestamp)}")
                    
            except (GPSTimeError, ValidationError) as e:
                processing_errors.append({
                    'station': station_id,
                    'index': i,
                    'timestamp': timestamp,
                    'error': str(e),
                    'error_type': type(e).__name__
                })
                station_results.append({
                    'timestamp': timestamp,
                    'status': 'error',
                    'error': str(e)
                })
            except GPSProcessingError as e:
                processing_errors.append({
                    'station': station_id, 
                    'index': i,
                    'timestamp': timestamp,
                    'error': str(e),
                    'error_type': 'ProcessingError'
                })
        
        processed_data.append({
            'station': station_id,
            'results': station_results,
            'success_count': len([r for r in station_results if r['status'] == 'success']),
            'error_count': len([r for r in station_results if r['status'] == 'error'])
        })
    
    return processed_data, processing_errors

# Example usage
station_data = {
    'REYK': [
        datetime.datetime(2024, 1, 15, 12, 30, 45),
        datetime.datetime(1900, 1, 1, 12, 0, 0),    # Invalid date
        "2024-01-15",                                # Wrong type
        datetime.datetime(2024, 1, 16, 14, 15, 30),
    ],
    'HOFN': [
        datetime.datetime(2024, 1, 15, 10, 0, 0),
        datetime.datetime(2024, 1, 15, 11, 0, 0),
    ]
}

results, errors = robust_gps_processing(station_data)

print("Processing Summary:")
for station_result in results:
    station = station_result['station']
    success = station_result['success_count']
    error = station_result['error_count']
    print(f"  {station}: {success} success, {error} errors")

print(f"\nDetailed Errors ({len(errors)} total):")
for error in errors:
    print(f"  {error['station']} #{error['index']}: {error['error_type']} - {error['error']}")
```

### Validation Best Practices

```python
from gtimes.exceptions import ValidationError, GPSTimeError
from gtimes.gpstime import gpsFromUTC, UTCFromGps

def validate_before_processing(func):
    """Decorator to add validation to GPS processing functions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            # Convert validation errors to more specific GPS errors
            raise GPSTimeError(f"Input validation failed in {func.__name__}: {e}") from e
        except Exception as e:
            # Handle unexpected errors
            raise GPSTimeError(f"Unexpected error in {func.__name__}: {e}") from e
    return wrapper

@validate_before_processing
def batch_gps_conversion(utc_times):
    """Convert multiple UTC times to GPS with validation."""
    results = []
    for utc_time in utc_times:
        if isinstance(utc_time, tuple) and len(utc_time) == 6:
            result = gpsFromUTC(*utc_time)
            results.append(result)
        else:
            raise ValidationError(f"Invalid UTC time format: {utc_time}")
    return results

# Test batch conversion
test_times = [
    (2024, 1, 15, 12, 30, 45),
    (2024, 1, 16, 14, 0, 0),
    (1900, 1, 1, 12, 0, 0),    # This will cause validation error
]

try:
    results = batch_gps_conversion(test_times)
    print(f"Successfully converted {len(results)} timestamps")
except GPSTimeError as e:
    print(f"Batch conversion failed: {e}")
```

### Error Recovery Strategies

```python
from gtimes.exceptions import ValidationError, GPSTimeError, FractionalYearError
from gtimes.timefunc import TimefromYearf
import datetime

def resilient_time_conversion(inputs, fallback_strategy='skip'):
    """Convert times with error recovery strategies."""
    results = []
    errors = []
    
    for i, input_data in enumerate(inputs):
        try:
            if isinstance(input_data, float):
                # Fractional year conversion
                result = TimefromYearf(input_data)
                results.append(('fractional_year', input_data, result))
                
            elif isinstance(input_data, tuple) and len(input_data) == 6:
                # UTC tuple conversion
                from gtimes.gpstime import gpsFromUTC
                result = gpsFromUTC(*input_data)
                results.append(('utc_tuple', input_data, result))
                
            else:
                raise ValidationError(f"Unsupported input type: {type(input_data)}")
                
        except (ValidationError, GPSTimeError, FractionalYearError) as e:
            error_info = {
                'index': i,
                'input': input_data,
                'error': str(e),
                'error_type': type(e).__name__
            }
            errors.append(error_info)
            
            # Apply fallback strategy
            if fallback_strategy == 'skip':
                continue
            elif fallback_strategy == 'default_time':
                # Use current time as fallback
                fallback = datetime.datetime.utcnow()
                results.append(('fallback', input_data, fallback))
            elif fallback_strategy == 'raise':
                raise
    
    return results, errors

# Test with mixed input types
mixed_inputs = [
    2024.123,                           # Valid fractional year
    (2024, 1, 15, 12, 30, 45),         # Valid UTC tuple
    1900.0,                             # Invalid fractional year
    (1900, 1, 1, 12, 0, 0),            # Invalid UTC tuple
    "invalid",                          # Invalid type
    2020.5,                             # Valid fractional year
]

results, errors = resilient_time_conversion(mixed_inputs, 'skip')

print(f"Successfully processed {len(results)} inputs:")
for conversion_type, original, result in results:
    if conversion_type == 'fractional_year':
        print(f"  Fractional {original} -> {result.strftime('%Y-%m-%d')}")
    elif conversion_type == 'utc_tuple':
        print(f"  UTC {original} -> GPS Week {result[0]}, SOW {result[1]:.0f}")

print(f"\nEncountered {len(errors)} errors:")
for error in errors:
    print(f"  #{error['index']}: {error['error_type']} - {error['error']}")
```

## Error Message Customization

All GTimes exceptions support detailed context that can be customized:

```python
from gtimes.exceptions import GTimesError, ValidationError

# Create custom exception with context
custom_error = ValidationError(
    "Custom validation failed",
    context={
        'user_input': 'invalid_data',
        'expected_range': '1980-2100',
        'processing_stage': 'input_validation',
        'suggestions': ['Check input format', 'Verify date range']
    }
)

print(f"Error: {custom_error}")
print(f"Context: {custom_error.context}")
```

This comprehensive error handling system ensures robust GPS time processing with informative error messages and recovery strategies.