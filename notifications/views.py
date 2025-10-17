from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification

@login_required
def notifications_view(request):
    # Filtering unread and read notifications
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    read_notifications = Notification.objects.filter(user=request.user, is_read=True).order_by('-created_at')[:50]  # Limit to most recent 50 read notifications

    context = {
        'unread_notifications': unread_notifications,
        'read_notifications': read_notifications,
    }
    return render(request, 'notifications/notifications.html', context)

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    messages.success(request, "Notification marked as read.")
    return redirect('notifications')

@login_required
def mark_all_notifications_as_read(request):
    # Update all unread notifications for the current user
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    count = notifications.count()
    
    # Use update for efficiency instead of looping
    notifications.update(is_read=True)
    
    if count > 0:
        messages.success(request, f"{count} notification{'s' if count > 1 else ''} marked as read.")
    else:
        messages.info(request, "No unread notifications to mark as read.")
    
    return redirect('notifications')