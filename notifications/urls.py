from django.urls import path
from .views import notifications_view, mark_notification_as_read

urlpatterns = [
    path('notifications/', notifications_view, name='notifications'),
    path('notifications/mark-as-read/<int:notification_id>/', mark_notification_as_read, name='mark_notification_as_read'),
]
