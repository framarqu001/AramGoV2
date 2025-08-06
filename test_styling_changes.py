#!/usr/bin/python3 -s
"""
Test script to validate the match card styling changes
"""
import os
import sys
import re

def test_css_changes():
    """Test that the CSS file contains the required changes"""
    css_file_path = '/workspace/match_history/static/match_history/css/details.css'
    
    print("Testing CSS changes...")
    
    with open(css_file_path, 'r') as f:
        css_content = f.read()
    
    # Test 1: Check match card height update
    if 'height: 120px' in css_content:
        print("✓ Match card height updated to 120px")
    else:
        print("✗ Match card height not updated")
        return False
    
    # Test 2: Check for expanded state
    if '.match-card.expanded' in css_content:
        print("✓ Expanded match card state added")
    else:
        print("✗ Expanded match card state missing")
        return False
    
    # Test 3: Check grid layout update
    if 'grid-template-columns: .6fr 1fr 1fr 1.2fr' in css_content:
        print("✓ Grid layout updated for expanded information")
    else:
        print("✗ Grid layout not updated")
        return False
    
    # Test 4: Check for rank indicator styles
    rank_classes = ['.rank-indicator', '.rank-indicator.gold', '.rank-indicator.silver', 
                   '.rank-indicator.diamond', '.rank-indicator.master']
    for rank_class in rank_classes:
        if rank_class in css_content:
            print(f"✓ {rank_class} style found")
        else:
            print(f"✗ {rank_class} style missing")
            return False
    
    # Test 5: Check for level indicator styles
    if '.level-indicator' in css_content:
        print("✓ Level indicator styles added")
    else:
        print("✗ Level indicator styles missing")
        return False
    
    # Test 6: Check for participant stats styles
    participant_classes = ['.participant-stats', '.participant-kda', '.participant-cs',
                          '.participant-expanded-info', '.participant-main-info']
    for participant_class in participant_classes:
        if participant_class in css_content:
            print(f"✓ {participant_class} style found")
        else:
            print(f"✗ {participant_class} style missing")
            return False
    
    # Test 7: Check for responsive breakpoints
    breakpoints = ['@media (max-width: 1200px)', '@media (max-width: 992px)', 
                  '@media (max-width: 768px)', '@media (max-width: 480px)']
    for breakpoint in breakpoints:
        if breakpoint in css_content:
            print(f"✓ {breakpoint} responsive breakpoint found")
        else:
            print(f"✗ {breakpoint} responsive breakpoint missing")
            return False
    
    # Test 8: Check for hover states
    if ':hover' in css_content and 'participant-expanded-info' in css_content:
        print("✓ Hover states for expanded information found")
    else:
        print("✗ Hover states for expanded information missing")
        return False
    
    # Test 9: Check color scheme consistency
    color_vars = ['var(--blue-color)', 'var(--red-color)', 'var(--secondary-color)', 'var(--yellow-color)']
    for color_var in color_vars:
        if color_var in css_content:
            print(f"✓ {color_var} used in new styles")
        else:
            print(f"✗ {color_var} not used in new styles")
            return False
    
    return True

def test_template_changes():
    """Test that the template contains the required changes"""
    template_file_path = '/workspace/match_history/templates/match_history/match_list.html'
    
    print("\nTesting template changes...")
    
    with open(template_file_path, 'r') as f:
        template_content = f.read()
    
    # Test 1: Check for new HTML structure
    required_elements = ['participant-main-info', 'participant-expanded-info', 
                        'participant-stats', 'level-indicator', 'rank-indicator',
                        'participant-kda', 'participant-cs']
    
    for element in required_elements:
        if element in template_content:
            print(f"✓ {element} found in template")
        else:
            print(f"✗ {element} missing from template")
            return False
    
    # Test 2: Check for summoner level conditional display
    if 'participant.summoner.summoner_level' in template_content:
        print("✓ Summoner level conditional display found")
    else:
        print("✗ Summoner level conditional display missing")
        return False
    
    # Test 3: Check for participant stats display
    if 'participant.kills' in template_content and 'participant.deaths' in template_content:
        print("✓ Participant KDA display found")
    else:
        print("✗ Participant KDA display missing")
        return False
    
    # Test 4: Check for CS display
    if 'participant.creep_score' in template_content:
        print("✓ Participant CS display found")
    else:
        print("✗ Participant CS display missing")
        return False
    
    return True

def test_file_integrity():
    """Test that files are properly formatted and don't have syntax errors"""
    print("\nTesting file integrity...")
    
    # Test CSS file
    css_file_path = '/workspace/match_history/static/match_history/css/details.css'
    try:
        with open(css_file_path, 'r') as f:
            css_content = f.read()
        
        # Basic CSS syntax check - count braces
        open_braces = css_content.count('{')
        close_braces = css_content.count('}')
        
        if open_braces == close_braces:
            print("✓ CSS file has balanced braces")
        else:
            print(f"✗ CSS file has unbalanced braces: {open_braces} open, {close_braces} close")
            return False
            
    except Exception as e:
        print(f"✗ Error reading CSS file: {e}")
        return False
    
    # Test template file
    template_file_path = '/workspace/match_history/templates/match_history/match_list.html'
    try:
        with open(template_file_path, 'r') as f:
            template_content = f.read()
        
        # Basic template syntax check - count Django template tags
        if_tags = template_content.count('{% if')
        endif_tags = template_content.count('{% endif %}')
        
        if if_tags == endif_tags:
            print("✓ Template file has balanced if/endif tags")
        else:
            print(f"✗ Template file has unbalanced if/endif tags: {if_tags} if, {endif_tags} endif")
            return False
            
    except Exception as e:
        print(f"✗ Error reading template file: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=== Match Card Styling Changes Validation ===\n")
    
    all_tests_passed = True
    
    # Run CSS tests
    if not test_css_changes():
        all_tests_passed = False
    
    # Run template tests
    if not test_template_changes():
        all_tests_passed = False
    
    # Run file integrity tests
    if not test_file_integrity():
        all_tests_passed = False
    
    print("\n=== Test Results ===")
    if all_tests_passed:
        print("✓ All tests passed! The styling changes have been successfully implemented.")
        return 0
    else:
        print("✗ Some tests failed. Please review the changes.")
        return 1

if __name__ == '__main__':
    sys.exit(main())