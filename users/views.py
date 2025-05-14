from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import StudentSignupForm
from .models import User
from scheme.models import SchemeApplication

def student_signup(request):
    if request.method == "POST":
        form = StudentSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'student'  
            user.save()
            login(request, user)
            return redirect('student_dashboard') 
    else:
        form = StudentSignupForm()
    return render(request, 'users/signup.html', {'form': form})

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.role == 'student':
                return redirect('student_dashboard')
            elif user.role == 'department_encharge':
                return redirect('department_dashboard')
            elif user.role == 'el_coordinator':
                return redirect('el_coordinator_dashboard')
            elif user.role == 'admin':
                return redirect('/admin/')  
        else:
            messages.error(request, "Invalid credentials")
    
    return render(request, 'users/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

def applicant_profile(request, application_id):
    """
    View to display the profile of a specific student, including their personal details, college details, and uploaded documents.
    """
    student = get_object_or_404(SchemeApplication, id = application_id)

    context = {
        'student': student,
    }
    
    return render(request, 'users/student_profile.html', context)

def student_profile(request):
    student = get_object_or_404(SchemeApplication, student__id = request.user.id)

    context = {
        'student': student,
    }
    
    return render(request, 'users/student_profile.html', context)