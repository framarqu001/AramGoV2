from django import template

register = template.Library()

@register.simple_tag
def zip_lists(*args):
    """A template tag that zips lists, allowing multiple lists to be iterated simultaneously in templates."""
    return zip(*args)