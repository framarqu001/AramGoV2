#!/usr/bin/env python3
"""
Simple validation script for expanded match card functionality
"""
import os
import re

def test_css_structure():
    """Test that CSS file has required classes and structure"""
    css_path = 'match_history/static/match_history/css/details.css'
    
    if not os.path.exists(css_path):
        print("❌ CSS file not found")
        return False
    
    with open(css_path, 'r') as f:
        css_content = f.read()
    
    required_classes = [
        '.match-card.expanded',
        '.match-expanded-content',
        '.expanded-stats-grid',
        '.detailed-stats-section',
        '.team-comparison',
        '.player-row',
        '.stat-row'
    ]
    
    missing_classes = []
    for css_class in required_classes:
        if css_class not in css_content:
            missing_classes.append(css_class)
    
    if missing_classes:
        print(f"❌ Missing CSS classes: {missing_classes}")
        return False
    
    # Check for responsive breakpoints
    breakpoints = ['@media (max-width: 1024px)', '@media (max-width: 768px)', '@media (max-width: 480px)']
    missing_breakpoints = []
    for breakpoint in breakpoints:
        if breakpoint not in css_content:
            missing_breakpoints.append(breakpoint)
    
    if missing_breakpoints:
        print(f"❌ Missing responsive breakpoints: {missing_breakpoints}")
        return False
    
    # Check for animations
    animations = ['@keyframes fadeIn', '@keyframes spin']
    missing_animations = []
    for animation in animations:
        if animation not in css_content:
            missing_animations.append(animation)
    
    if missing_animations:
        print(f"❌ Missing animations: {missing_animations}")
        return False
    
    print("✅ CSS structure validation passed")
    return True

def test_template_structure():
    """Test that template has required structure"""
    template_path = 'match_history/templates/match_history/match_list.html'
    
    if not os.path.exists(template_path):
        print("❌ Template file not found")
        return False
    
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    required_elements = [
        'match-expanded-content',
        'expanded-stats-grid',
        'detailed-stats-section',
        'team-comparison',
        'onclick="toggleMatchExpansion(this)"'
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in template_content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ Missing template elements: {missing_elements}")
        return False
    
    print("✅ Template structure validation passed")
    return True

def test_javascript_functions():
    """Test that JavaScript functions are defined"""
    js_template_path = 'match_history/templates/match_history/details.html'
    
    if not os.path.exists(js_template_path):
        print("❌ JavaScript template file not found")
        return False
    
    with open(js_template_path, 'r') as f:
        js_content = f.read()
    
    required_functions = [
        'function toggleMatchExpansion',
        'function closeOtherExpandedCards',
        'function initializeLazyLoading'
    ]
    
    missing_functions = []
    for function in required_functions:
        if function not in js_content:
            missing_functions.append(function)
    
    if missing_functions:
        print(f"❌ Missing JavaScript functions: {missing_functions}")
        return False
    
    print("✅ JavaScript functions validation passed")
    return True

def test_accessibility_features():
    """Test that accessibility features are implemented"""
    css_path = 'match_history/static/match_history/css/details.css'
    js_path = 'match_history/templates/match_history/details.html'
    
    # Check CSS focus states
    with open(css_path, 'r') as f:
        css_content = f.read()
    
    focus_states = ['.match-btn:focus', '.player-name:focus']
    missing_focus = []
    for focus_state in focus_states:
        if focus_state not in css_content:
            missing_focus.append(focus_state)
    
    if missing_focus:
        print(f"❌ Missing CSS focus states: {missing_focus}")
        return False
    
    # Check JavaScript keyboard support
    with open(js_path, 'r') as f:
        js_content = f.read()
    
    keyboard_features = ['keydown', "e.key === 'Enter'", "e.key === ' '"]
    missing_keyboard = []
    for feature in keyboard_features:
        if feature not in js_content:
            missing_keyboard.append(feature)
    
    if missing_keyboard:
        print(f"❌ Missing keyboard support: {missing_keyboard}")
        return False
    
    print("✅ Accessibility features validation passed")
    return True

def test_performance_optimizations():
    """Test that performance optimizations are in place"""
    css_path = 'match_history/static/match_history/css/details.css'
    
    with open(css_path, 'r') as f:
        css_content = f.read()
    
    # Check for will-change property
    if 'will-change: transform' not in css_content:
        print("❌ Missing performance optimization: will-change property")
        return False
    
    # Check for contain property
    if 'contain: layout style paint' not in css_content:
        print("❌ Missing performance optimization: contain property")
        return False
    
    print("✅ Performance optimizations validation passed")
    return True

def main():
    """Run all validation tests"""
    print("🧪 Running expanded match card validation tests...\n")
    
    tests = [
        test_css_structure,
        test_template_structure,
        test_javascript_functions,
        test_accessibility_features,
        test_performance_optimizations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All validation tests passed! Expanded match card functionality is ready.")
        return True
    else:
        print("❌ Some validation tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    main()