from django import template

register = template.Library()


@register.filter(name='to_float')
def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


@register.filter(name='get_item')
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    return dictionary.get(key)
