# decorators.py
from functools import wraps
from django.http import HttpResponseForbidden


def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("You must be logged in to access this page.")

            if request.user.role != required_role:
                return HttpResponseForbidden("You do not have the necessary permissions to view this page.")

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
