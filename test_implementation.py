#!/usr/bin/env python
"""
Simple test script to verify the expandable match card implementation
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, '/workspace')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AramGoV2.settings')
django.setup()

from django.template import Template, Context
from django.test import TestCase

def test_template_structure():
    """Test that the template structure includes all required elements"""
    
    # Read the actual match_list.html template
    with open('/workspace/match_history/templates/match_history/match_list.html', 'r') as f:
        template_content = f.read()
    
    # Check for required structural elements
    required_elements = [
        'match-card-content',
        'expandable-content',
        'detailed-participants',
        'team-blue-header',
        'team-red-header',
        'detailed-participant-entry',
        'participant-kda',
        'participant-cs',
        'champ-icon-medium',
        'tiny-img'
    ]
    
    print("Testing template structure...")
    for element in required_elements:
        if element in template_content:
            print(f"✓ Found {element}")
        else:
            print(f"✗ Missing {element}")
    
    return all(element in template_content for element in required_elements)

def test_css_classes():
    """Test that the CSS file includes all required classes"""
    
    # Read the details.css file
    with open('/workspace/match_history/static/match_history/css/details.css', 'r') as f:
        css_content = f.read()
    
    # Check for required CSS classes
    required_classes = [
        '.match-card-expanded',
        '.content-expanded',
        '.expandable-content',
        '.detailed-participants',
        '.champ-icon-medium',
        '.tiny-img',
        '.participant-kda',
        '.participant-cs'
    ]
    
    print("\nTesting CSS classes...")
    for css_class in required_classes:
        if css_class in css_content:
            print(f"✓ Found {css_class}")
        else:
            print(f"✗ Missing {css_class}")
    
    return all(css_class in css_content for css_class in required_classes)

def test_javascript_functionality():
    """Test that the JavaScript functionality is present"""
    
    # Read the details.html file
    with open('/workspace/match_history/templates/match_history/details.html', 'r') as f:
        html_content = f.read()
    
    # Check for required JavaScript elements
    required_js_elements = [
        '.match-btn',
        'toggleClass',
        'match-card-expanded',
        'content-expanded',
        'closest',
        'find'
    ]
    
    print("\nTesting JavaScript functionality...")
    for js_element in required_js_elements:
        if js_element in html_content:
            print(f"✓ Found {js_element}")
        else:
            print(f"✗ Missing {js_element}")
    
    return all(js_element in html_content for js_element in required_js_elements)

def main():
    """Run all tests"""
    print("Running expandable match card implementation tests...\n")
    
    template_ok = test_template_structure()
    css_ok = test_css_classes()
    js_ok = test_javascript_functionality()
    
    print(f"\n{'='*50}")
    print("SUMMARY:")
    print(f"Template structure: {'PASS' if template_ok else 'FAIL'}")
    print(f"CSS classes: {'PASS' if css_ok else 'FAIL'}")
    print(f"JavaScript functionality: {'PASS' if js_ok else 'FAIL'}")
    
    if template_ok and css_ok and js_ok:
        print("\n🎉 All tests PASSED! Implementation is complete.")
        return True
    else:
        print("\n❌ Some tests FAILED. Please review the implementation.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)