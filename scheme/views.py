from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import SchemeApplicationForm
from scheme.models import SchemeApplication, WorkLog
from payments.models import Salary
from .models import WorkLog
from .forms import WorkLogForm
from django.utils.timezone import localdate
from datetime import timedelta
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.urls import reverse
from users.decorators import role_required

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
            return redirect('student_dashboard')  # Redirect to student dashboard after submission
    else:
        form = SchemeApplicationForm()

    return render(request, 'scheme/scheme_registration.html', {'form': form})

@login_required
@role_required('student')
def student_dashboard(request):
    student = request.user  # Assuming student is authenticated

    if not SchemeApplication.objects.filter(student=student).exists():
        return redirect('scheme_registration')

    today = localdate()  # Get current date in local timezone
    # Check if the student has already logged hours today
    already_submitted = WorkLog.objects.filter(student=student, date=today).exists()

    # Fetch past work logs
    work_logs = WorkLog.objects.filter(student=student).order_by('-date')

    # Get the latest work log entry (to access timestamp)
    last_work_log = WorkLog.objects.filter(student=student).order_by('-id').first()
    last_updated = {'date':last_work_log.date, 'time':last_work_log.time } if last_work_log else None  # Only date available
    # Calculate total approved hours
    total_hours = WorkLog.objects.filter(student=student, is_verified=True).aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0

    # Fetch salary details
    pending_salary = Salary.objects.filter(student=student, is_paid=False).aggregate(total=Sum('amount'))['total'] or 0
    completed_salary = Salary.objects.filter(student=student, is_paid=True).aggregate(total=Sum('amount'))['total'] or 0

    # Work log form
    if request.method == "POST" and not already_submitted : 
        form = WorkLogForm(request.POST)
        if form.is_valid():
            work_log = form.save(commit=False)
            work_log.student = student
            work_log.date = today  # Ensure today's date is set
            work_log.save()
            return redirect('student_dashboard')  # Reload the page
    else:
        form = WorkLogForm()

    context = {
        'status': SchemeApplication.objects.get(student=student).status,
        'work_logs': work_logs,
        'already_submitted': already_submitted,
        'form': form,
        'pending_salary': pending_salary,
        'completed_salary': completed_salary,
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
            work_log.student = request.user  # Assign the logged-in student
            work_log.save()
            return redirect("student_dashboard")  # Redirect to dashboard after submission
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
        

    # Fetch pending work logs (not verified)
    pending_work_logs = WorkLog.objects.filter(is_verified=False).order_by('date')

    # Fetch verified work logs
    verified_work_logs = WorkLog.objects.filter(is_verified=True).order_by('-date')

    # Total hours worked per student (Summary)
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
    work_log.delete()  # Or mark as rejected
    return HttpResponseRedirect(reverse('department_dashboard'))