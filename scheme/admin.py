from django.contrib import admin
from .models import SchemeApplication, WorkLog
# Register your models here.
admin.site.register(SchemeApplication)
# admin.site.register(WorkLog)

@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'hours_worked', 'is_verified')  # Ensure 'date' is here
    ordering = ('-date',)  # Sort by latest first
    list_filter = ('is_verified', 'date')  # Add filters