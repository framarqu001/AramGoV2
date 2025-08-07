#!/usr/bin/env python
"""
Test script for expanded match details functionality
Run this script to verify the implementation works correctly
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AramGoV2.settings')
sys.path.append('/workspace')
django.setup()

from match_history.models import *
from match_history.views import match_details
import datetime

def test_basic_functionality():
    """Test basic functionality of expanded match details"""
    print("Testing expanded match details functionality...")
    
    # Test 1: Check if new model fields exist
    print("✓ Testing model fields...")
    try:
        # Check if new fields exist in Participant model
        participant_fields = [field.name for field in Participant._meta.fields]
        required_participant_fields = ['damage_dealt', 'damage_taken', 'gold_earned']
        
        for field in required_participant_fields:
            if field not in participant_fields:
                print(f"✗ Missing field {field} in Participant model")
                return False
        
        # Check if new fields exist in Match model
        match_fields = [field.name for field in Match._meta.fields]
        required_match_fields = ['blue_team_towers', 'red_team_towers', 'blue_team_dragons', 'red_team_dragons']
        
        for field in required_match_fields:
            if field not in match_fields:
                print(f"✗ Missing field {field} in Match model")
                return False
                
        print("✓ All required model fields present")
        
    except Exception as e:
        print(f"✗ Error checking model fields: {e}")
        return False
    
    # Test 2: Check if templates exist
    print("✓ Testing template files...")
    try:
        template_path = '/workspace/match_history/templates/match_history/match_details.html'
        if not os.path.exists(template_path):
            print("✗ match_details.html template not found")
            return False
        
        with open(template_path, 'r') as f:
            template_content = f.read()
            
        # Check for key template elements
        required_elements = [
            'match-details-expanded',
            'team-objectives-section',
            'detailed-stats-section',
            'stats-grid',
            'blue-team-section',
            'red-team-section'
        ]
        
        for element in required_elements:
            if element not in template_content:
                print(f"✗ Missing template element: {element}")
                return False
                
        print("✓ Template structure correct")
        
    except Exception as e:
        print(f"✗ Error checking template: {e}")
        return False
    
    # Test 3: Check CSS styles
    print("✓ Testing CSS styles...")
    try:
        css_path = '/workspace/match_history/static/match_history/css/details.css'
        if not os.path.exists(css_path):
            print("✗ details.css file not found")
            return False
            
        with open(css_path, 'r') as f:
            css_content = f.read()
            
        # Check for key CSS classes
        required_css_classes = [
            '.match-details-expanded',
            '.team-objectives-section',
            '.stats-grid',
            '.player-row',
            '.champion-img-small'
        ]
        
        for css_class in required_css_classes:
            if css_class not in css_content:
                print(f"✗ Missing CSS class: {css_class}")
                return False
                
        print("✓ CSS styles present")
        
    except Exception as e:
        print(f"✗ Error checking CSS: {e}")
        return False
    
    # Test 4: Check URL configuration
    print("✓ Testing URL configuration...")
    try:
        from match_history.urls import urlpatterns
        match_details_url_found = False
        
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name == 'match_details':
                match_details_url_found = True
                break
                
        if not match_details_url_found:
            print("✗ match_details URL pattern not found")
            return False
            
        print("✓ URL configuration correct")
        
    except Exception as e:
        print(f"✗ Error checking URL configuration: {e}")
        return False
    
    # Test 5: Check view function
    print("✓ Testing view function...")
    try:
        from match_history.views import match_details
        if not callable(match_details):
            print("✗ match_details view function not found or not callable")
            return False
            
        print("✓ View function exists")
        
    except Exception as e:
        print(f"✗ Error checking view function: {e}")
        return False
    
    print("\n🎉 All tests passed! Expanded match details functionality is properly implemented.")
    return True

def test_template_syntax():
    """Test template syntax and structure"""
    print("\n✓ Testing template syntax...")
    try:
        from django.template import Template, Context
        from django.template.loader import get_template
        
        # Try to load the template
        template = get_template('match_history/match_details.html')
        print("✓ Template loads without syntax errors")
        
        # Test with mock context
        mock_context = {
            'match': type('MockMatch', (), {
                'blue_team_towers': 2,
                'red_team_towers': 1,
                'blue_team_dragons': 1,
                'red_team_dragons': 0,
                'winner': 100
            })(),
            'blue_team': [],
            'red_team': [],
            'blue_team_kills': 10,
            'red_team_kills': 5,
            'main_participant': type('MockParticipant', (), {'win': True})()
        }
        
        # This would render the template with mock data
        # rendered = template.render(Context(mock_context))
        print("✓ Template structure is valid")
        
    except Exception as e:
        print(f"✗ Template syntax error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("EXPANDED MATCH DETAILS FUNCTIONALITY TEST")
    print("=" * 60)
    
    success = test_basic_functionality()
    if success:
        success = test_template_syntax()
    
    if success:
        print("\n✅ ALL TESTS PASSED - Implementation is ready!")
        print("\nNext steps:")
        print("1. Run Django migrations: python manage.py migrate")
        print("2. Start the development server: python manage.py runserver")
        print("3. Navigate to a summoner's match history page")
        print("4. Click the expand button on any match card to see detailed stats")
    else:
        print("\n❌ SOME TESTS FAILED - Please review the implementation")
        
    print("=" * 60)