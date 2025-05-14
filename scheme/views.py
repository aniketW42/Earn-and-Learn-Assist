from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import SchemeApplicationForm, WorkLogForm
from scheme.models import SchemeApplication, WorkLog
from django.utils.timezone import localdate
from datetime import timedelta
from django.db.models import Sum
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from users.decorators import role_required
from django.contrib import messages
from notifications.models import Notification
# Create your views here.
def home(request):
    return render(request, 'base.html')
def about(request):
    return render(request, 'scheme/about.html')

@login_required
@role_required('student')
def scheme_registration(request):
    if request.user.is_registered:
        return redirect('student_dashboard')
    if request.method == 'POST':
        form = SchemeApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            scheme_application = form.save(commit=False)
            scheme_application.student = request.user
            scheme_application.save()
            request.user.is_registered = True
            request.user.save()
            return redirect('student_dashboard')  
    else:
        form = SchemeApplicationForm()

    return render(request, 'scheme/scheme_registration.html', {'form': form})

@login_required
@role_required('student')
def student_dashboard(request):
    student = request.user  

    if not SchemeApplication.objects.filter(student=student).exists():
        return redirect('scheme_registration')

    today = localdate()  
  
    already_submitted = WorkLog.objects.filter(student=student, date=today).exists()

    work_logs = WorkLog.objects.filter(student=student).order_by('-date')

    last_work_log = WorkLog.objects.filter(student=student).order_by('-id').first()
    last_updated = {'date':last_work_log.date, 'time':last_work_log.time } if last_work_log else None  # Only date available

    total_hours = WorkLog.objects.filter(student=student, is_verified=True).aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0

    if request.method == "POST" and not already_submitted : 
        form = WorkLogForm(request.POST)
        if form.is_valid():
            work_log = form.save(commit=False)
            work_log.student = student
            work_log.date = today 
            work_log.save()
            return redirect('student_dashboard')  
    else:
        form = WorkLogForm()

    context = {
        'applicant': SchemeApplication.objects.get(student=student),
        'work_logs': work_logs,
        'already_submitted': already_submitted,
        'form': form,
        'total_hours': total_hours,
        'last_updated': last_updated, 
        
    }
    return render(request, 'scheme/dashboard.html', context)


@login_required
@role_required('student')
def submit_work_log(request):
    if request.method == "POST":
        form = WorkLogForm(request.POST)
        if form.is_valid():
            work_log = form.save(commit=False)
            work_log.student = request.user  
            work_log.save()
            return redirect("student_dashboard")  
    else:
        form = WorkLogForm()
    
    return render(request, "scheme/submit_work_log.html", {"form": form})


@login_required
@role_required('student')
def work_summary(request):
    student = request.user
    work_logs = WorkLog.objects.filter(student=student).order_by('-date')
    total_hours = WorkLog.objects.filter(student=student).aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0
    verified_hours = WorkLog.objects.filter(student=student, is_verified=True ).aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0

    context = {
        'work_logs': work_logs,
        'total_hours': total_hours,
        'verified_hours': verified_hours,
        'pending_hours': total_hours - verified_hours,
        'weekly_hours': WorkLog.objects.filter(student=student, date__gte=localdate() - timedelta(days=7)).aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0, 
    }
    return render(request, 'scheme/work_summary.html', context)


@login_required
@role_required('department_encharge')
def department_dashboard(request):

    # if not request.user.role == "Department Encharge":
    #     print('going home')
    #     return redirect('home')
        

    pending_work_logs = WorkLog.objects.filter(is_verified=False).order_by('date')

    verified_work_logs = WorkLog.objects.filter(is_verified=True).order_by('-date')

    student_hours = WorkLog.objects.filter(is_verified=True).values('student__username').annotate(total_hours=Sum('hours_worked')).order_by('-total_hours')

    context = {
        'pending_work_logs': pending_work_logs,
        'verified_work_logs': verified_work_logs,
        'student_hours': student_hours,
    }
    return render(request, 'scheme/department_dashboard.html', context)

@login_required
@role_required('department_encharge')
def approve_work_log(request, log_id):
    work_log = get_object_or_404(WorkLog, id=log_id)
    work_log.is_verified = True
    work_log.save()
    return HttpResponseRedirect(reverse('department_dashboard'))

@login_required
@role_required('department_encharge')
def reject_work_log(request, log_id):
    work_log = get_object_or_404(WorkLog, id=log_id)
    work_log.delete()  
    return HttpResponseRedirect(reverse('department_dashboard'))



@role_required('el_coordinator')
def el_coordinator_dashboard(request):
    pending_applications = SchemeApplication.objects.filter(status="Pending")
    approved_students = SchemeApplication.objects.filter(status="Approved")
    work_logs = WorkLog.objects.all().order_by('-date')
    total_hours = sum(work_log.hours_worked for work_log in work_logs)

    context = {
        "pending_applications": pending_applications,
        "approved_students": approved_students,
        "work_logs": work_logs,
        "total_hours": total_hours,
    }
    return render(request, "scheme/el_coordinator_dashboard.html", context)

@login_required
@role_required('el_coordinator')

def view_application(request, application_id):
    application = get_object_or_404(SchemeApplication, id=application_id)


    if request.method == "POST":
        action = request.POST.get("action")
        comments = request.POST.get("comments", "").strip()

        if action == "approve":
            application.status = "Approved"
            messages.success(request, "Application approved successfully.")
        elif action == "reject":
            application.status = "Rejected"
            messages.error(request, "Application has been rejected.")
        elif action == "notify":
            application.status = "Correction Required"
            messages.warning(request, "Student has been notified for corrections.")
            
        application.comments = comments
        application.save()
        Notification.objects.create(
            user=application.student,
            message=f'Your Earn & Learn application status has been updated to {application.status}. "{comments}"'
        )

        return redirect("el_coordinator_dashboard")

    context = {"application": application}
    return render(request, "scheme/view_application.html", context)


@login_required
@role_required('el_coordinator')
def registered_students_view(request):
    """View to display all approved students to E&L Coordinator."""
    
    approved_students = SchemeApplication.objects.filter(status='Approved').order_by('first_name', 'last_name')

    context = {
        'approved_students': approved_students
    }
    
    return render(request, 'scheme/registered_students.html', context)

@login_required
@role_required('el_coordinator')
def student_worklog_view(request, student_id):
    """
    Display worklogs for a specific student by ID.
    """
    student = get_object_or_404(SchemeApplication, id=student_id, status="Approved")

    worklogs = WorkLog.objects.filter(student=student.student).order_by('-date', '-time')

    verified_hours = WorkLog.objects.filter(student=student.student, is_verified=True ).aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0

    context = {
        'student': student,
        'worklogs': worklogs,
        'verified_hours': verified_hours
    }
    
    return render(request, 'scheme/student_worklog.html', context)

@login_required
@role_required('el_coordinator')
def mark_student_completed(request, student_id):
    student = get_object_or_404(SchemeApplication, student__id=student_id)
    
    if student.status == "Completed":
        student.student.is_active = False
        student.student.save()
        messages.success(request, f"{student.first_name} {student.last_name} has been marked as completed and deactivated.")
    else:
        messages.warning(request, "Only completed students can be deactivated.")

    return redirect('registered_students')  