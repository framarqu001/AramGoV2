from django import template

register = template.Library()


@register.filter(name='to_float')
def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


@register.filter(name='format_number')
def format_number(value):
    """
    Format large numbers with K (thousands) or M (millions) suffix
    Example: 1500 -> 1.5K, 1500000 -> 1.5M
    """
    try:
        value = float(value)
        if value >= 1000000:
            return f"{value/1000000:.1f}M"
        elif value >= 1000:
            return f"{value/1000:.1f}K"
        else:
            return f"{value:.0f}"
    except (ValueError, TypeError):
        return "0"


@register.filter(name='format_damage')
def format_damage(value):
    """
    Format damage numbers with K (thousands) suffix
    Example: 15000 -> 15K
    """
    try:
        value = float(value.replace(',', ''))
        if value >= 1000:
            return f"{value/1000:.1f}K"
        else:
            return f"{value:.0f}"
    except (ValueError, TypeError):
        return "0"


@register.filter(name='format_gold')
def format_gold(value):
    """
    Format gold numbers with K (thousands) suffix
    Example: 15000 -> 15K
    """
    try:
        value = float(value.replace(',', ''))
        if value >= 1000:
            return f"{value/1000:.1f}K"
        else:
            return f"{value:.0f}"
    except (ValueError, TypeError):
        return "0"
