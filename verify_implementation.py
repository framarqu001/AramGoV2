#!/usr/bin/env python
"""
Simple verification script to test the add_numbers function
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, '/workspace')

# Import the function
try:
    from AramGoV2.util.math_utils import add_numbers
    print("✓ Successfully imported add_numbers function")
except ImportError as e:
    print(f"✗ Failed to import add_numbers: {e}")
    sys.exit(1)

# Test basic functionality
test_cases = [
    (2, 3, 5),
    (2.5, 3.7, 6.2),
    (-1, 5, 4),
    (0, 0, 0),
    (1000000, 2000000, 3000000),
    (-10, -5, -15)
]

print("\nTesting basic functionality:")
all_passed = True

for a, b, expected in test_cases:
    try:
        result = add_numbers(a, b)
        if abs(result - expected) < 0.0001:  # Handle floating point precision
            print(f"✓ add_numbers({a}, {b}) = {result} (expected {expected})")
        else:
            print(f"✗ add_numbers({a}, {b}) = {result} (expected {expected})")
            all_passed = False
    except Exception as e:
        print(f"✗ add_numbers({a}, {b}) raised exception: {e}")
        all_passed = False

# Test error handling
print("\nTesting error handling:")
error_test_cases = [
    ("2", 3),
    (2, "3"),
    (None, 3),
    ([1, 2], 3),
    ({"a": 1}, 3)
]

for a, b in error_test_cases:
    try:
        result = add_numbers(a, b)
        print(f"✗ add_numbers({a}, {b}) should have raised TypeError but returned {result}")
        all_passed = False
    except TypeError:
        print(f"✓ add_numbers({a}, {b}) correctly raised TypeError")
    except Exception as e:
        print(f"✗ add_numbers({a}, {b}) raised unexpected exception: {e}")
        all_passed = False

if all_passed:
    print("\n🎉 All tests passed! The implementation is working correctly.")
else:
    print("\n❌ Some tests failed. Please check the implementation.")
    sys.exit(1)