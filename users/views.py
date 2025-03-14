from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import StudentSignupForm
from .models import User

def student_signup(request):
    if request.method == "POST":
        form = StudentSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'student'  # Assign student role by default
            user.save()
            login(request, user)
            return redirect('student_dashboard')  # Redirect to student dashboard
    else:
        form = StudentSignupForm()
    return render(request, 'users/signup.html', {'form': form})

def user_login(request):
    if request.method == "POST":
        roll_number = request.POST['roll_number']
        password = request.POST['password']
        user = authenticate(request, username=roll_number, password=password)
        
        if user is not None:
            login(request, user)
            # Redirect based on role
            if user.role == 'student':
                return redirect('student_dashboard')
            elif user.role == 'department_encharge':
                return redirect('department_dashboard')
            elif user.role == 'coordinator':
                return redirect('coordinator_dashboard')
            elif user.role == 'admin':
                return redirect('/admin/')  
        else:
            messages.error(request, "Invalid credentials")
    
    return render(request, 'users/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')
