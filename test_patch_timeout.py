#!/usr/bin/env python3
"""
Simple test script to verify the patch timeout calculation is correct.
"""

def test_timeout_calculation():
    """Test that 3 weeks equals 1814400 seconds"""
    weeks = 3
    days_per_week = 7
    hours_per_day = 24
    minutes_per_hour = 60
    seconds_per_minute = 60
    
    total_days = weeks * days_per_week
    total_seconds = total_days * hours_per_day * minutes_per_hour * seconds_per_minute
    
    expected_timeout = 1814400
    
    print(f"Calculation verification:")
    print(f"3 weeks = {weeks} weeks")
    print(f"3 weeks = {total_days} days")
    print(f"3 weeks = {total_seconds} seconds")
    print(f"Expected timeout: {expected_timeout}")
    print(f"Calculation matches: {total_seconds == expected_timeout}")
    
    assert total_seconds == expected_timeout, f"Expected {expected_timeout}, got {total_seconds}"
    print("✅ Timeout calculation is correct!")

if __name__ == "__main__":
    test_timeout_calculation()