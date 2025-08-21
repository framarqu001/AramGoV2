#!/usr/bin/env python
"""
Simple test script to verify the expandable match cards functionality
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/workspace')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AramGoV2.settings')
django.setup()

from django.template import Context, Template
from django.template.loader import get_template
from match_history.models import *
from django.utils import timezone

def test_template_syntax():
    """Test that the match_list.html template has valid syntax"""
    try:
        template = get_template('match_history/match_list.html')
        print("✓ Template syntax is valid")
        return True
    except Exception as e:
        print(f"✗ Template syntax error: {e}")
        return False

def test_expandable_functionality():
    """Test the expandable match card functionality"""
    print("\n=== Testing Expandable Match Cards ===")
    
    # Test template syntax
    if not test_template_syntax():
        return False
    
    # Test that essential CSS classes are defined
    css_file_path = '/workspace/match_history/static/match_history/css/details.css'
    try:
        with open(css_file_path, 'r') as f:
            css_content = f.read()
            
        required_classes = [
            '.match-details-expanded',
            '.chevron-icon',
            '.participant-detailed',
            '.match-metadata',
            '.team-victory',
            '.team-defeat'
        ]
        
        missing_classes = []
        for css_class in required_classes:
            if css_class not in css_content:
                missing_classes.append(css_class)
        
        if missing_classes:
            print(f"✗ Missing CSS classes: {missing_classes}")
            return False
        else:
            print("✓ All required CSS classes are present")
            
    except Exception as e:
        print(f"✗ Error reading CSS file: {e}")
        return False
    
    # Test JavaScript function presence
    details_template_path = '/workspace/match_history/templates/match_history/details.html'
    try:
        with open(details_template_path, 'r') as f:
            template_content = f.read()
            
        if 'toggleMatchDetails' in template_content:
            print("✓ JavaScript function toggleMatchDetails is present")
        else:
            print("✗ JavaScript function toggleMatchDetails is missing")
            return False
            
    except Exception as e:
        print(f"✗ Error reading details template: {e}")
        return False
    
    print("✓ All expandable match card functionality tests passed!")
    return True

def test_model_methods():
    """Test that model methods work correctly"""
    print("\n=== Testing Model Methods ===")
    
    try:
        # Test Match model methods
        from datetime import datetime
        
        # Create a test match (this won't be saved to DB)
        test_match = Match(
            match_id='test_001',
            game_start=timezone.now(),
            game_duration=1800,  # 30 minutes
            game_mode='ARAM',
            game_version='14.17.1',
            winner=100
        )
        
        # Test get_patch method
        patch = test_match.get_patch()
        expected_patch = '14.17'
        if patch == expected_patch:
            print(f"✓ get_patch() returns correct value: {patch}")
        else:
            print(f"✗ get_patch() returned {patch}, expected {expected_patch}")
            return False
        
        # Test get_duration method
        duration = test_match.get_duration()
        expected_duration = '30:0'
        if duration == expected_duration:
            print(f"✓ get_duration() returns correct value: {duration}")
        else:
            print(f"✗ get_duration() returned {duration}, expected {expected_duration}")
            return False
            
        print("✓ All model method tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error testing model methods: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting expandable match cards functionality tests...\n")
    
    success = True
    
    # Test expandable functionality
    if not test_expandable_functionality():
        success = False
    
    # Test model methods
    if not test_model_methods():
        success = False
    
    print(f"\n{'='*50}")
    if success:
        print("🎉 ALL TESTS PASSED! Expandable match cards are ready to use.")
    else:
        print("❌ SOME TESTS FAILED. Please check the implementation.")
    print(f"{'='*50}")
    
    return success

if __name__ == '__main__':
    main()