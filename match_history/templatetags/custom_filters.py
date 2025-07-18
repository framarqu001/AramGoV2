from django import template

register = template.Library()


@register.filter(name='to_float')
def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


@register.filter(name='calculate_position')
def calculate_position(position, total_items):
    """
    Calculate the left position percentage for timeline items.
    
    Args:
        position: The current item position (1-based index)
        total_items: Total number of items
        
    Returns:
        Left position percentage (between 10% and 90%)
    """
    try:
        position = int(position)
        total_items = int(total_items)
        
        if total_items <= 1:
            return 50  # Center if only one item
            
        # Calculate position between 10% and 90%
        spacing = 80.0 / (total_items - 1) if total_items > 1 else 0
        return 10 + (position - 1) * spacing
    except (ValueError, TypeError, ZeroDivisionError):
        return 50  # Default to center