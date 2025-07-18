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
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0.0
