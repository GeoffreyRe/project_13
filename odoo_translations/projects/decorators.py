from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def user_is_assigned_to_project(view_func):
    """
    This custom decorator will check if user is assigned to a project (the one he wants to access)
    if not : redirects to home page
    else : continue normal processing
    warning : this decorator must be preceded by is_authenticated decorator
    """
    @wraps(view_func)
    def actual_decorator(request, project_id, *args, **kwargs):
        if request.user is not None:
            requested_project = request.user.userproject_set.filter(project=project_id)
            if len(requested_project) != 1:
                messages.add_message(
                    request,
                    messages.INFO,
                    "Vous ne pouvez pas accéder à ce projet")
                return redirect('view_home')

        return view_func(request, project_id, *args, **kwargs)

    return actual_decorator
