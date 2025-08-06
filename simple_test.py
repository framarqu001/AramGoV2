#!/usr/bin/env python3
"""
Simple test to verify the expandable match card functionality
"""

def test_html_structure():
    """Test that the HTML template has the correct structure"""
    print("Testing HTML structure...")
    
    # Read the match_list.html file
    with open('/workspace/match_history/templates/match_history/match_list.html', 'r') as f:
        content = f.read()
    
    # Check for data-expanded attribute
    assert 'data-expanded="false"' in content, "data-expanded attribute not found"
    print("✓ data-expanded attribute found")
    
    # Check for match-card class
    assert 'class="match-card' in content, "match-card class not found"
    print("✓ match-card class found")
    
    # Check for match-btn class
    assert 'class="match-btn' in content, "match-btn class not found"
    print("✓ match-btn class found")
    
    # Check for chevron SVG with drop class
    assert 'class = "drop"' in content, "chevron drop class not found"
    print("✓ chevron drop class found")

def test_css_structure():
    """Test that the CSS has the correct classes and transitions"""
    print("\nTesting CSS structure...")
    
    # Read the details.css file
    with open('/workspace/match_history/static/match_history/css/details.css', 'r') as f:
        content = f.read()
    
    # Check for match-card-expanded class
    assert '.match-card-expanded' in content, "match-card-expanded class not found"
    print("✓ match-card-expanded class found")
    
    # Check for transition on match-card
    assert 'transition: height 0.3s ease' in content, "height transition not found"
    print("✓ height transition found")
    
    # Check for chevron rotation class
    assert '.drop.rotated' in content, "chevron rotation class not found"
    print("✓ chevron rotation class found")
    
    # Check for transform rotate
    assert 'transform: rotate(180deg)' in content, "chevron rotation transform not found"
    print("✓ chevron rotation transform found")
    
    # Check for chevron transition
    assert 'transition: transform 0.3s ease' in content, "chevron transition not found"
    print("✓ chevron transition found")

def test_javascript_structure():
    """Test that the JavaScript has the correct event handlers"""
    print("\nTesting JavaScript structure...")
    
    # Read the details.html file
    with open('/workspace/match_history/templates/match_history/details.html', 'r') as f:
        content = f.read()
    
    # Check for match-btn click handler
    assert "$(document).on('click', '.match-btn'" in content, "match-btn click handler not found"
    print("✓ match-btn click handler found")
    
    # Check for data-expanded toggle logic
    assert "matchCard.attr('data-expanded'" in content, "data-expanded toggle logic not found"
    print("✓ data-expanded toggle logic found")
    
    # Check for match-card-expanded class toggle
    assert "addClass('match-card-expanded')" in content, "addClass match-card-expanded not found"
    assert "removeClass('match-card-expanded')" in content, "removeClass match-card-expanded not found"
    print("✓ match-card-expanded class toggle found")
    
    # Check for chevron rotation toggle
    assert "addClass('rotated')" in content, "addClass rotated not found"
    assert "removeClass('rotated')" in content, "removeClass rotated not found"
    print("✓ chevron rotation toggle found")

def main():
    """Main test function"""
    print("=== Testing Expandable Match Card Functionality ===\n")
    
    try:
        test_html_structure()
        test_css_structure()
        test_javascript_structure()
        
        print("\n=== Test Summary ===")
        print("✓ HTML structure tests passed")
        print("✓ CSS structure tests passed")
        print("✓ JavaScript structure tests passed")
        print("\n🎉 All tests passed! Expandable functionality is ready.")
            
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)