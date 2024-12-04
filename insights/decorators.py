from django.http import HttpResponseForbidden

def role_required(required_role):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if hasattr(request.user, 'userprofile') and request.user.userprofile.role == required_role:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("⛔ You are not authorized to access this page.")
        return _wrapped_view
    return decorator

# touched on 2025-05-27T15:28:56.617211Z