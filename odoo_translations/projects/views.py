from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .utils import nest_list
from .forms import ProjectCreationForm

# Create your views here.

@login_required
def projects_list_view(request):
    projects = request.user.userproject_set.all()
    projects = []
    projects_nested = nest_list(projects)
    project_form = ProjectCreationForm()
    context = {"projects" : [], "is_odds" : False if len(projects) % 2 == 0 else True,'form':project_form}
    return render(request, "projects/projects_list.html", context)

@login_required
def invitations_list_view(request):
    pass

@login_required
def create_project(request):
    if request.method == 'POST':
        project_form = ProjectCreationForm(request.POST)
        if project_form.is_valid():
            pass
    else:
        project_form = ProjectCreationForm()
