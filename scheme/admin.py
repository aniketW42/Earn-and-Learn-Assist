from django.contrib import admin
from .models import SchemeApplication, WorkLog

@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'hours_worked', 'is_verified')
    ordering = ('-date',)  #sort by latestfirst
    list_filter = ('is_verified', 'date')  #add filters


@admin.action(description="Mark selected students as Completed")
def mark_as_completed(modeladmin, request, queryset):
    queryset.update(status="Completed")

class SchemeApplicationAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "prn_number", "status")
    list_filter = ("status", "department")
    actions = [mark_as_completed]

admin.site.register(SchemeApplication, SchemeApplicationAdmin)