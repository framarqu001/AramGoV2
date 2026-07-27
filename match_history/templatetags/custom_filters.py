from django import template

register = template.Library()


@register.filter(name='to_float')
def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


@register.filter(name='divisibleby')
def divisibleby(value, arg):
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
