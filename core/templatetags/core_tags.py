from django import template

register = template.Library()

@register.filter
def get_list(dictionary, key):
    """
    برای چک کردن اینکه آیا یک مقدار در لیست پارامترهای GET هست یا نه
    استفاده: request.GET|get_list:'spec_ram'
    """
    full_key = f"spec_{key}"
    return dictionary.getlist(full_key)