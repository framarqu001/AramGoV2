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
    """
    Get an item from a dictionary using the key.
    Usage: {{ dictionary|get_item:key }}
    """
    if not dictionary:
        return None
    try:
        return dictionary.get(key)
    except (KeyError, AttributeError):
        return None


@register.filter(name='divide')
def divide(value, arg):
    """
    Divide the value by the argument.
    Usage: {{ value|divide:arg }}
    """
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0
