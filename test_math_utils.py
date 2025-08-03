#!/usr/bin/env python3
"""
Simple test script to verify the add_numbers function works correctly.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, '/workspace')

# Import the function
from AramGoV2.util.math_utils import add_numbers

def test_add_numbers():
    """Test the add_numbers function with various inputs."""
    
    print("Testing add_numbers function...")
    
    # Test cases
    test_cases = [
        (2, 3, 5, "Adding positive integers"),
        (-2, -3, -5, "Adding negative integers"),
        (5, -3, 2, "Adding positive and negative"),
        (0, 5, 5, "Adding with zero"),
        (2.5, 3.7, 6.2, "Adding floats"),
        (2, 3.5, 5.5, "Adding int and float"),
        (1000000, 2000000, 3000000, "Adding large numbers"),
    ]
    
    passed = 0
    failed = 0
    
    for a, b, expected, description in test_cases:
        try:
            result = add_numbers(a, b)
            if abs(result - expected) < 0.0001:  # Handle floating point precision
                print(f"✓ {description}: {a} + {b} = {result}")
                passed += 1
            else:
                print(f"✗ {description}: Expected {expected}, got {result}")
                failed += 1
        except Exception as e:
            print(f"✗ {description}: Exception occurred - {e}")
            failed += 1
    
    # Test error cases
    error_cases = [
        ("2", 3, "String and int"),
        (2, "3", "Int and string"),
        (None, 3, "None and int"),
        ([1, 2], 3, "List and int"),
    ]
    
    print("\nTesting error cases...")
    for a, b, description in error_cases:
        try:
            result = add_numbers(a, b)
            print(f"✗ {description}: Should have raised TypeError, got {result}")
            failed += 1
        except TypeError:
            print(f"✓ {description}: Correctly raised TypeError")
            passed += 1
        except Exception as e:
            print(f"✗ {description}: Wrong exception type - {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    success = test_add_numbers()
    sys.exit(0 if success else 1)