from django.http import HttpResponseForbidden

def role_required(required_role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and hasattr(request.user, 'role'):
                if request.user.role == required_role:
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponseForbidden("You are not authorized to access this page.")
            return HttpResponseForbidden("You are not authorized to access this page.")
        return wrapper
    return decorator