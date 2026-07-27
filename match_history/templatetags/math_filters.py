from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """Divides the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return value

@register.filter
def add(value, arg):
    """Adds the argument to the value"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def subtract(value, arg):
    """Subtracts the argument from the value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def default(value, arg):
    """Returns the value if it's not None, otherwise returns the argument"""
    return value if value is not None else arg