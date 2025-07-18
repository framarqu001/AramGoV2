from django import template

register = template.Library()


@register.filter(name='to_float')
def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter(name='add')
def add(value, arg):
    try:
        return int(value) + int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter(name='intdiv')
def intdiv(value, arg):
    try:
        return int(value) // int(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
