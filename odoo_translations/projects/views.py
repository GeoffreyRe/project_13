from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .utils import nest_list

# Create your views here.

@login_required
def projects_list_view(request):
    projects = request.user.userproject_set.all()
    projects = []
    projects_nested = nest_list(projects)
    context = {"projects" : [], "is_odds" : False if len(projects) % 2 == 0 else True}
    return render(request, "projects/projects_list.html", context)

@login_required
def invitations_list_view(request):
    pass
