from django.urls import path
from .views import *
from users.views import applicant_profile

urlpatterns = [
    path('', home, name='home'),
    path('register/', scheme_registration, name='scheme_registration'),
    path('update-application/', update_scheme_application, name='update_scheme_application'),
    path("student-dashboard/", student_dashboard, name="student_dashboard"),
    path('about/', about, name='about'),
    # Removed submit_work_log - functionality integrated into student_dashboard
    path("student/work_summary/", work_summary, name="work_summary"),
    path('department-dashboard/', department_dashboard, name='department_dashboard'),
    path('approve-work-log/<int:log_id>/', approve_work_log, name='approve_work_log'),
    path('reject-work-log/<int:log_id>/', reject_work_log, name='reject_work_log'),
    path("el-coordinator-dashboard/", el_coordinator_dashboard, name="el_coordinator_dashboard"),
    path("application/<int:application_id>/", view_application, name="view_application"),
    path('registered-students-list/', registered_students_view, name='registered_students'),
    path('student/<int:student_id>/worklog/', student_worklog_view, name='student_worklog'),
    path('student/<int:application_id>/profile/', applicant_profile, name='el_student_profile'),
    
    # Department Management URLs
    path('departments/', department_list, name='department_list'),
    path('departments/add/', add_department, name='add_department'),
    path('departments/<int:department_id>/', department_detail, name='department_detail'),
    path('departments/<int:department_id>/edit/', edit_department, name='edit_department'),
    path('departments/create-incharge/', create_department_incharge, name='create_department_incharge'),
    path('departments/assign-student/', assign_student_to_department, name='assign_student_to_department'),
    path('departments/bulk-assign/', bulk_assign_students, name='bulk_assign_students'),
    path('departments/unassign/<int:assignment_id>/', unassign_student, name='unassign_student'),
    
    # Scheme approval required page
    path('scheme-approval-required/', scheme_approval_required_view, name='scheme_application_required'),
    
    # Payment Module URLs
    path('payments/', payment_reports, name='payment_reports'),
    path('payments/rates/', payment_rate_management, name='payment_rate_management'),
    path('payments/calculate/', payment_calculation_bulk, name='payment_calculation_bulk'),
    path('payments/calculation/<int:record_id>/', payment_calculation_detail, name='payment_calculation_detail'),
    path('payments/export/', export_payment_report, name='export_payment_report'),
    path('payments/budget/', department_payment_budget, name='department_payment_budget'),
    path('student/payments/', student_payment_dashboard, name='student_payment_dashboard'),
]
