from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
import json
from .utils import nest_list
from .forms import ProjectCreationForm
from .models import Project

# Create your views here.

@login_required
def projects_list_view(request):
    # to be changed : it is for testing only, we have to find projects in many to many table
    projects = Project.objects.filter(creator=request.user)
    projects_nested = nest_list(projects)
    project_form = ProjectCreationForm()
    context = {"projects" : projects_nested, "is_odds" : False if len(projects) % 2 == 0 else True,'form':project_form}
    return render(request, "projects/projects_list.html", context)

@login_required
def invitations_list_view(request):
    pass

@login_required
def create_project(request):
    if request.method == 'POST':
        #import pdb; pdb.set_trace()
        new_project = Project(name=request.POST['name'],
                            description=request.POST['description'],
                            creation_date=request.POST['initial-creation_date'],
                            creator=request.user)
        new_project.save()
    return redirect("projects_list")


@login_required
def view_verification_project_name(request):
    #import pdb;pdb.set_trace()
    if request.method == "POST":
        current_user = request.user
        project_name = request.POST.get('project_name', None)
        exists = Project.objects.project_already_exists_for_creator(current_user, project_name)
        return JsonResponse({'project_exists' : exists}, safe=False, status=200)