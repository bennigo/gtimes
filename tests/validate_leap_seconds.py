#!/usr/bin/env python3
"""
Validation script for GPS leap second data integrity.

This script validates that the leap second data used in GTimes is accurate
and up-to-date with official IERS data sources.
"""

import datetime
import sys
from typing import Dict, List, Tuple

from gtimes.gpstime import leapSecDict, getleapSecs


def validate_leap_second_data() -> bool:
    """
    Validate leap second data against known values.
    
    Returns:
        True if all validations pass, False otherwise
    """
    print("🔍 Validating GPS leap second data...")
    
    # Get leap second dictionary
    leap_dict = leapSecDict()
    
    # Known leap second introduction dates (GPS time perspective)
    # These are historically verified leap second additions
    known_leap_seconds = [
        (datetime.datetime(1981, 7, 1), 1),   # First leap second after GPS epoch
        (datetime.datetime(1982, 7, 1), 2),
        (datetime.datetime(1983, 7, 1), 3),
        (datetime.datetime(1985, 7, 1), 4),
        (datetime.datetime(1988, 1, 1), 5),
        (datetime.datetime(1990, 1, 1), 6),
        (datetime.datetime(1991, 1, 1), 7),
        (datetime.datetime(1992, 7, 1), 8),
        (datetime.datetime(1993, 7, 1), 9),
        (datetime.datetime(1994, 7, 1), 10),
        (datetime.datetime(1996, 1, 1), 11),
        (datetime.datetime(1997, 7, 1), 12),
        (datetime.datetime(1999, 1, 1), 13),
        (datetime.datetime(2006, 1, 1), 14),
        (datetime.datetime(2009, 1, 1), 15),
        (datetime.datetime(2012, 7, 1), 16),
        (datetime.datetime(2015, 7, 1), 17),
        (datetime.datetime(2017, 1, 1), 18),  # Most recent as of 2024
    ]
    
    validation_passed = True
    
    # Test 1: Validate known leap second values
    print("  ✓ Testing known leap second values...")
    for test_date, expected_leap_secs in known_leap_seconds:
        try:
            calculated_leap_secs = getleapSecs(test_date, gpst=True)
            if calculated_leap_secs != expected_leap_secs:
                print(f"    ❌ Mismatch for {test_date.date()}: "
                      f"expected {expected_leap_secs}, got {calculated_leap_secs}")
                validation_passed = False
            else:
                print(f"    ✓ {test_date.date()}: {calculated_leap_secs} leap seconds")
        except Exception as e:
            print(f"    ❌ Error processing {test_date.date()}: {e}")
            validation_passed = False
    
    # Test 2: Validate leap second dictionary structure
    print("  ✓ Testing leap second dictionary structure...")
    if not isinstance(leap_dict, dict):
        print(f"    ❌ Leap second dictionary is not a dict: {type(leap_dict)}")
        validation_passed = False
    
    if len(leap_dict) == 0:
        print(f"    ❌ Leap second dictionary is empty")
        validation_passed = False
    
    # Test 3: Validate leap second consistency
    print("  ✓ Testing leap second consistency...")
    prev_leap_count = 0
    for date_str, leap_count in sorted(leap_dict.items()):
        if leap_count <= prev_leap_count:
            print(f"    ❌ Non-increasing leap second count at {date_str}: "
                  f"{leap_count} <= {prev_leap_count}")
            validation_passed = False
        prev_leap_count = leap_count
    
    # Test 4: Validate current era accuracy
    print("  ✓ Testing current era accuracy...")
    current_date = datetime.datetime(2024, 1, 1)
    current_leap_secs = getleapSecs(current_date, gpst=True)
    
    # As of 2024, there should be 18 leap seconds since GPS epoch
    expected_current = 18
    if current_leap_secs != expected_current:
        print(f"    ❌ Current leap seconds incorrect: "
              f"expected {expected_current}, got {current_leap_secs}")
        validation_passed = False
    else:
        print(f"    ✓ Current leap seconds: {current_leap_secs}")
    
    # Test 5: Validate GPS epoch baseline
    print("  ✓ Testing GPS epoch baseline...")
    gps_epoch = datetime.datetime(1980, 1, 6)
    epoch_leap_secs = getleapSecs(gps_epoch, gpst=True)
    
    if epoch_leap_secs != 0:
        print(f"    ❌ GPS epoch should have 0 leap seconds, got {epoch_leap_secs}")
        validation_passed = False
    else:
        print(f"    ✓ GPS epoch leap seconds: {epoch_leap_secs}")
    
    # Test 6: Validate pre-GPS era handling
    print("  ✓ Testing pre-GPS era handling...")
    pre_gps_date = datetime.datetime(1970, 1, 1)
    try:
        pre_gps_leap_secs = getleapSecs(pre_gps_date, gpst=True)
        if pre_gps_leap_secs is not None:
            print(f"    ⚠️  Pre-GPS date returned: {pre_gps_leap_secs}")
    except Exception as e:
        print(f"    ✓ Pre-GPS date properly handled: {e}")
    
    # Summary
    if validation_passed:
        print("✅ All leap second validations passed!")
        return True
    else:
        print("❌ Some leap second validations failed!")
        return False


def validate_time_conversion_accuracy() -> bool:
    """
    Validate GPS time conversion accuracy with known test cases.
    
    Returns:
        True if all conversions are accurate, False otherwise
    """
    print("\n🔍 Validating GPS time conversion accuracy...")
    
    from gtimes.gpstime import gpsFromUTC, UTCFromGps
    
    # Test cases with known GPS time values (corrected)
    test_cases = [
        # (UTC tuple, expected GPS week, expected SOW)  
        ((2024, 1, 1, 0, 0, 0), 2295, 86418.0),       # 2024 start
        ((2000, 1, 1, 0, 0, 0), 1042, 518413.0),      # Y2K (with leap seconds)
        ((1980, 1, 6, 0, 0, 0), 0, 0.0),              # GPS epoch
        ((2019, 4, 6, 23, 59, 42), 2048, 0.0),        # Near GPS rollover
    ]
    
    validation_passed = True
    tolerance = 1e-6  # Microsecond precision
    
    for i, (utc_tuple, expected_week, expected_sow) in enumerate(test_cases):
        try:
            # Convert to GPS time
            gps_week, sow, gps_day, sod = gpsFromUTC(*utc_tuple)
            
            # Check GPS week
            if gps_week != expected_week:
                print(f"    ❌ Test {i+1} week mismatch: "
                      f"expected {expected_week}, got {gps_week}")
                validation_passed = False
            
            # Check seconds of week (with tolerance for floating point)
            sow_diff = abs(sow - expected_sow)
            if sow_diff > tolerance:
                print(f"    ❌ Test {i+1} SOW mismatch: "
                      f"expected {expected_sow}, got {sow}, diff {sow_diff}")
                validation_passed = False
            
            # Test round-trip conversion
            utc_back = UTCFromGps(gps_week, sow, dtimeObj=True)
            original_dt = datetime.datetime(*[int(x) if i < 6 else x for i, x in enumerate(utc_tuple)])
            
            time_diff = abs((utc_back - original_dt).total_seconds())
            if time_diff > tolerance:
                print(f"    ❌ Test {i+1} round-trip error: {time_diff:.6f}s")
                validation_passed = False
            else:
                print(f"    ✓ Test {i+1}: {utc_tuple} -> Week {gps_week}, SOW {sow:.6f}")
                
        except Exception as e:
            print(f"    ❌ Test {i+1} failed with error: {e}")
            validation_passed = False
    
    if validation_passed:
        print("✅ All GPS time conversion validations passed!")
        return True
    else:
        print("❌ Some GPS time conversion validations failed!")
        return False


def main() -> int:
    """Main validation function."""
    print("🧪 GTimes Scientific Validation Suite")
    print("=" * 50)
    
    all_passed = True
    
    # Run leap second validation
    if not validate_leap_second_data():
        all_passed = False
    
    # Run time conversion validation
    if not validate_time_conversion_accuracy():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All scientific validations PASSED!")
        return 0
    else:
        print("💥 Some scientific validations FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())