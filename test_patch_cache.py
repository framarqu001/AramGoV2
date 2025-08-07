#!/usr/bin/env python
"""
Simple test runner to verify our patch cache timeout changes work correctly.
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AramGoV2.settings')
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run only the patch cache tests
    failures = test_runner.run_tests(["match_history.tests.PatchVersionCacheTest"])
    
    if failures:
        sys.exit(1)
    else:
        print("All patch cache tests passed!")