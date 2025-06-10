from django import template
from django.contrib.sites.models import Site

register = template.Library()

@register.simple_tag
def site_name():
    """
    Returns the name of the current site from the database.
    Defaults to 'My Django Project' if the site is not found.
    """
    try:
        current_site = Site.objects.get_current()
        return current_site.name
    except (Site.DoesNotExist, Site.MultipleObjectsReturned):
        return 'My Django Project'  # Default fallback
