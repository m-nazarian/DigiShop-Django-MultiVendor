from django import template

register = template.Library()

@register.filter
def separator(value):
    """جدا کردن سه رقم سه رقم اعداد"""
    try:
        value = int(value)
        return "{:,}".format(value)
    except (ValueError, TypeError):
        return value