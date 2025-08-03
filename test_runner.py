#!/usr/bin/env python
"""
Simple test runner to verify the math_utils implementation
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AramGoV2.settings')
    django.setup()
    
    # Import and test the function directly
    from AramGoV2.util.math_utils import add_numbers
    
    print("Testing add_numbers function directly:")
    print(f"add_numbers(2, 3) = {add_numbers(2, 3)}")
    print(f"add_numbers(2.5, 3.7) = {add_numbers(2.5, 3.7)}")
    print(f"add_numbers(-1, 5) = {add_numbers(-1, 5)}")
    
    # Test error handling
    try:
        add_numbers("2", 3)
        print("ERROR: Should have raised TypeError")
    except TypeError as e:
        print(f"Correctly raised TypeError: {e}")
    
    print("\nDirect testing completed successfully!")
    
    # Now run the Django tests
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["AramGoV2.tests.MathUtilsTest"])
    
    if failures:
        print(f"\n{failures} test(s) failed!")
        sys.exit(1)
    else:
        print("\nAll tests passed!")