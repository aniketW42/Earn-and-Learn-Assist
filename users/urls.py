from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', student_signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('student/<int:application_id>/profile/', applicant_profile, name='el_student_profile'),
    path('student/profile/', student_profile, name='student_profile'),
]
