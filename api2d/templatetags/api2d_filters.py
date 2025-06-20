import base64
from django import template

register = template.Library()


@register.filter
def base64encode(value):
    """Convert value to base64"""
    if not value:
        return ""
    return base64.b64encode(str(value).encode("utf-8")).decode("utf-8")
