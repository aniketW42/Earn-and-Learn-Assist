from django.urls import path
from .views import *
from .views import submit_work_log
from users.views import applicant_profile
urlpatterns = [
    path('', home, name='home'),
    path('register/', scheme_registration, name='scheme_registration'),
    path("student-dashboard/", student_dashboard, name="student_dashboard"),
    path('about/', about, name='about'),
    path("submit-work-log/", submit_work_log, name="submit_work_log"),
    path("student/work_summary/", work_summary, name="work_summary"),
    path('department-dashboard/', department_dashboard, name='department_dashboard'),
    path('approve-work-log/<int:log_id>/', approve_work_log, name='approve_work_log'),
    path('reject-work-log/<int:log_id>/', reject_work_log, name='reject_work_log'),
    path("el-coordinator-dashboard/", el_coordinator_dashboard, name="el_coordinator_dashboard"),
    path("application/<int:application_id>/", view_application, name="view_application"),
    path('registered-students-list/', registered_students_view, name='registered_students'),
    path('student/<int:student_id>/worklog/', student_worklog_view, name='student_worklog'),
    path('student/<int:application_id>/profile/', applicant_profile, name='el_student_profile'),
]
