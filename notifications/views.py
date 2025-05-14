from django.shortcuts import render , redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notifications_view(request):
    # filtering unread and read notifications
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    read_notifications = Notification.objects.filter(user=request.user, is_read=True).order_by('-created_at')

    # mark u nread notifications as read

    context = {
        'unread_notifications': unread_notifications,   # Fixed variable name
        'read_notifications': read_notifications,
    }
    return render(request, 'notifications/notifications.html', context)

@login_required
def mark_notification_as_read(request, notification_id):

    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')