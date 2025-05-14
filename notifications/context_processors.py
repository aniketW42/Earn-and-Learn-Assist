from .models import Notification

def unread_notifications_count(request):
    """ Add unread notification count to context """
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        count = 0

    return {'unread_notifications_count': count}
