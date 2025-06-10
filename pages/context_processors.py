from django.utils import timezone
from .models import Notification

def active_notifications(request):
    """
    Context processor that makes active notifications available to all templates.
    """
    if not hasattr(request, 'user'):
        return {'notifications': []}
        
    now = timezone.now()
    notifications = Notification.objects.filter(
        is_active=True,
        start_date__lte=now,
    ).exclude(
        end_date__lt=now
    ).order_by('-start_date')
    
    return {
        'notifications': notifications
    }
