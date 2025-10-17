from django.http import HttpResponseForbidden
from django.shortcuts import render
from functools import wraps

def role_required(required_role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and hasattr(request.user, 'role'):
                # Handle both single role and list of roles
                if isinstance(required_role, list):
                    if request.user.role in required_role:
                        return view_func(request, *args, **kwargs)
                else:
                    if request.user.role == required_role:
                        return view_func(request, *args, **kwargs)
                return HttpResponseForbidden("You are not authorized to access this page.")
            return HttpResponseForbidden("You are not authorized to access this page.")
        return wrapper
    return decorator


def approved_scheme_required(view_func):
    """
    Decorator to ensure student has an approved scheme application before accessing scheme benefits
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in to access this page.")
        
        # Only apply this check to students
        if request.user.role != 'student':
            return view_func(request, *args, **kwargs)
        
        # Check if student has any scheme application first
        from scheme.models import SchemeApplication
        from django.shortcuts import redirect
        
        scheme_applications = SchemeApplication.objects.filter(student=request.user)
        
        if not scheme_applications.exists():
            # No application at all - redirect to registration
            from django.contrib import messages
            messages.info(request, 'Please complete your scheme application to access this feature.')
            return redirect('scheme_registration')
        
        # Check if student has approved scheme application
        try:
            scheme_app = SchemeApplication.objects.get(
                student=request.user,
                status='Approved'
            )
            return view_func(request, *args, **kwargs)
        except SchemeApplication.DoesNotExist:
            # Has application but not approved - show approval required page
            return render(request, 'scheme/scheme_approval_required.html', {
                'message': 'You need an approved scheme application to access this feature.',
                'help_text': 'Please ensure your scheme application has been approved by the EL Coordinator before accessing work logs and payment features.'
            })
    
    return wrapper


def scheme_benefits_required(view_func):
    """
    Combined decorator for role and approved scheme requirement
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # First check role
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in to access this page.")
        
        if request.user.role not in ['student', 'el_coordinator', 'department_encharge']:
            return HttpResponseForbidden("You are not authorized to access this page.")
        
        # If student, check for approved scheme application
        if request.user.role == 'student':
            from scheme.models import SchemeApplication
            try:
                scheme_app = SchemeApplication.objects.get(
                    student=request.user,
                    status='Approved'
                )
            except SchemeApplication.DoesNotExist:
                return render(request, 'scheme/scheme_approval_required.html', {
                    'message': 'You need an approved scheme application to access this feature.',
                    'help_text': 'Please ensure your scheme application has been approved by the EL Coordinator before accessing work logs and payment features.'
                })
        
        return view_func(request, *args, **kwargs)
    
    return wrapper