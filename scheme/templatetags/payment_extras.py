from django import template
from decimal import Decimal
import os

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def dict_key(dictionary, key):
    """Get value from dictionary by key."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

@register.filter
def replace_value(value, args):
    """Replace characters in a string."""
    try:
        if ',' in args:
            old, new = args.split(',', 1)
        else:
            old = args
            new = ' '
        return value.replace(old, new)
    except:
        return value

@register.filter
def file_name(file_path):
    """Extract filename from file path."""
    if file_path:
        return os.path.basename(str(file_path))
    return ''
