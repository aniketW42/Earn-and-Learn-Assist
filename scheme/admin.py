from django.contrib import admin
from .models import (SchemeApplication, WorkLog, Department, DepartmentIncharge,
                        StudentDepartmentAssignment, PaymentRate, PaymentCalculation,
                        DepartmentPaymentSummary, PaymentExport)
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


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code')


@admin.register(DepartmentIncharge)
class DepartmentInchargeAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'is_active', 'assigned_at')
    list_filter = ('is_active', 'assigned_at')
    search_fields = ('user__username', 'department__name')


@admin.register(StudentDepartmentAssignment)
class StudentDepartmentAssignmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'department', 'is_active', 'assigned_at')
    list_filter = ('is_active', 'assigned_at', 'department')
    search_fields = ('student__username', 'department__name')


@admin.register(PaymentRate)
class PaymentRateAdmin(admin.ModelAdmin):
    list_display = ('rate_per_hour', 'set_by', 'updated_at', 'created_at')
    list_filter = ('updated_at', 'set_by')
    search_fields = ('notes',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)


@admin.register(PaymentCalculation)
class PaymentCalculationAdmin(admin.ModelAdmin):
    list_display = ('student', 'department', 'calculation_month', 'total_hours', 
                   'rate_per_hour', 'total_amount', 'calculated_by')
    list_filter = ('calculation_month', 'department', 'created_at')
    search_fields = ('student__username', 'student__first_name', 'student__last_name')
    ordering = ('-calculation_month', 'student__first_name')
    readonly_fields = ('total_amount',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('student', 'calculation_month', 'total_hours', 'rate_per_hour')
        return self.readonly_fields


@admin.register(DepartmentPaymentSummary)
class DepartmentPaymentSummaryAdmin(admin.ModelAdmin):
    list_display = ('department', 'calculation_month', 'total_students', 
                   'total_hours', 'total_amount', 'average_hours_per_student')
    list_filter = ('calculation_month', 'department')
    ordering = ('-calculation_month', 'department__name')
    readonly_fields = ('total_students', 'total_hours', 'total_amount', 'average_hours_per_student')


@admin.register(PaymentExport)
class PaymentExportAdmin(admin.ModelAdmin):
    list_display = ('export_type', 'export_month', 'department', 'student', 
                   'file_name', 'exported_by', 'created_at')
    list_filter = ('export_type', 'export_month', 'created_at')
    search_fields = ('file_name', 'exported_by__username')
    ordering = ('-created_at',)


admin.site.register(SchemeApplication, SchemeApplicationAdmin)