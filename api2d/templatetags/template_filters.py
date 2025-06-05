# api2d/templatetags/template_filters.py
from django import template
from django.contrib.messages import constants

register = template.Library()

@register.filter
def bootstrap_alert_class(message_tag):
    """
    Maps Django's message tags to Bootstrap's alert classes.
    Django passes message tags as strings (e.g., 'error', 'success'),
    so we map these directly to Bootstrap's alert classes.
    """
    MAPPING = {
        'error': 'danger',
        'success': 'success',
        'info': 'info',
        'warning': 'warning',
        'debug': 'secondary',
    }
    # Convert to lowercase to handle case variations
    return MAPPING.get(message_tag.lower(), message_tag)