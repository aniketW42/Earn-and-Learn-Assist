from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import StudentSignupForm
from .models import User, StudentProfile
from scheme.models import SchemeApplication

def student_signup(request):
    # Redirect if user is already logged in
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        if request.user.role == 'student':
            return redirect('student_dashboard')
        elif request.user.role == 'department_encharge':
            return redirect('department_dashboard')
        elif request.user.role == 'el_coordinator':
            return redirect('el_coordinator_dashboard')
        elif request.user.role == 'admin':
            return redirect('/admin/')
        else:
            return redirect('home')
    
    if request.method == "POST":
        form = StudentSignupForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.role = 'student'  
                user.save()
                
                # Create StudentProfile with the roll number
                StudentProfile.objects.create(
                    user=user,
                    roll_number=form.cleaned_data['roll_number'],
                    department='',  # Will be filled during scheme application
                    is_registered=False
                )
                
                login(request, user)
                messages.success(request, f"Welcome {user.get_full_name()}! Your account has been created successfully. Please complete your scheme application.")
                return redirect('scheme_registration')
                
            except Exception as e:
                messages.error(request, "An error occurred during registration. Please try again.")
                # Log the error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Student signup error: {e}")
        else:
            # Form has validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
    else:
        form = StudentSignupForm()
    
    return render(request, 'users/signup.html', {'form': form})

def user_login(request):
    # Redirect if user is already logged in
    if request.user.is_authenticated:
        if request.user.role == 'student':
            # Check if student has a scheme application
            from scheme.models import SchemeApplication
            if not SchemeApplication.objects.filter(student=request.user).exists():
                return redirect('scheme_registration')
            return redirect('student_dashboard')
        elif request.user.role == 'department_encharge':
            return redirect('department_dashboard')
        elif request.user.role == 'el_coordinator':
            return redirect('el_coordinator_dashboard')
        elif request.user.role == 'admin':
            return redirect('/admin/')
        else:
            return redirect('home')
    
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, "Please enter both username and password")
            return render(request, 'users/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Get the 'next' parameter for redirect after login
                next_url = request.POST.get('next') or request.GET.get('next')
                
                if next_url:
                    return redirect(next_url)
                
                # Role-based redirects with scheme application check for students
                if user.role == 'student':
                    # Check if student has a scheme application
                    from scheme.models import SchemeApplication
                    if not SchemeApplication.objects.filter(student=user).exists():
                        messages.info(request, "Please complete your scheme application to access all features.")
                        return redirect('scheme_registration')
                    return redirect('student_dashboard')
                elif user.role == 'department_encharge':
                    return redirect('department_dashboard')
                elif user.role == 'el_coordinator':
                    return redirect('el_coordinator_dashboard')
                elif user.role == 'admin':
                    return redirect('/admin/')
                else:
                    return redirect('home')
            else:
                messages.error(request, "Your account has been deactivated. Please contact the administrator.")
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, 'users/login.html')

def user_logout(request):
    if request.user.is_authenticated:
        user_name = request.user.get_full_name() or request.user.username
        logout(request)
        messages.success(request, f"You have been successfully logged out. See you soon, {user_name}!")
    else:
        messages.info(request, "You were not logged in.")
    
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