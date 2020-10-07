from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.forms import modelformset_factory
import json
from .utils import nest_list
from .forms import ProjectCreationForm
from .models import Project, Invitation, UserProject
from .decorators import user_is_assigned_to_project

# Create your views here.

@login_required
def projects_list_view(request):
    # user = user connected
    user = request.user
    projects = user.userproject_set.all()
    # project_nested = we create a list of list for displaying projects correctly on page 
    projects_nested = nest_list(projects)
    project_form = ProjectCreationForm()
    context = {"projects" : projects_nested, "is_odds" : False if len(projects) % 2 == 0 else True,'form':project_form}
    return render(request, "projects/projects_list.html", context)

@login_required
def invitations_list_view(request):
    invitations = request.user.project_invitations.all()
    context = {'invitations': invitations}
    return render(request, "projects/invitations_list.html", context)

@login_required
def create_project(request):
    if request.method == 'POST':
        #import pdb; pdb.set_trace()
        """
        new_project = Project(name=request.POST['name'],
                            description=request.POST['description'],
                            creation_date=request.POST['initial-creation_date'],
                            creator=request.user)
        new_project.save()
        """
        vals = {'name' : request.POST['name'],
        'description' : request.POST['description'],
        'creation_date' : request.POST['initial-creation_date'],
        'creator' : request.user}
        Project.objects.create_new_project(vals)
    return redirect("projects_list")


@login_required
def view_verification_project_name(request):
    #import pdb;pdb.set_trace()
    if request.method == "POST":
        current_user = request.user
        project_name = request.POST.get('project_name', None)
        exists = Project.objects.project_already_exists_for_creator(current_user, project_name)
        return JsonResponse({'project_exists' : exists}, safe=False, status=200)

@login_required
def from_invitation_to_project(request):
    if request.method == "POST":
        """
        result = True
        invitation_id = request.POST.get('invitation_id', None)
        try:
            invitation_id = int(invitation_id)
        except ValueError:
            result = False
            return JsonResponse({'success' : result}, safe=False, status=200)

        invitation = Invitation.objects.get(id=invitation_id)
        if invitation is not None:
            result = invitation.from_invitation_to_project()
        return JsonResponse({'success' : result}, safe=False, status=200)
        """
        return JsonResponse({'success' : True}, safe=False, status=200)
    
@login_required
def invitation_refused(request):
    if request.method == "POST":
        """
        invitation_id = request.POST.get('invitation_id', None)
        success = False
        if invitation_id is not None:
            try:
                invitation_id = int(invitation_id)
            except ValueError:
                return JsonResponse({'success' : success}, safe=False, status=200)
            invitation = Invitation.objects.get(id=invitation_id)
            if invitation is not None:
                invitation.is_refused()
                success=True
            return JsonResponse({'success' : success}, safe=False, status=200)
        return JsonResponse({'success' : success}, safe=False, status=200)
    return JsonResponse({'success' : success}, safe=False, status=200)
    """
        return JsonResponse({'success' : True}, safe=False, status=200)

@login_required
@user_is_assigned_to_project # custom decorator : see decorators.py module
def detail_project(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except ObjectDoesNotExist:
        #TODO : à retravailler pour rediriger vers une page avec un message explicite
        return HttpResponse("Le projet demandé n'existe pas")
    users_on_project = UserProject.objects.filter(project=project)
    has_write_rights = request.user.has_rights_to_modify_project(project)
    context = {
        'users_on_project' : users_on_project,
        'project': project,
        'has_write_rights': has_write_rights,
        'modifications': False}

    return render(request, 'projects/project_general_infos.html', context)


@login_required
@user_is_assigned_to_project # custom decorator : see decorators.py module
def detail_project_modifications(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except ObjectDoesNotExist:
        #TODO : à retravailler pour rediriger vers une page avec un message explicite
        return HttpResponse("Le projet demandé n'existe pas")
    if not request.user.has_rights_to_modify_project(project):
        # if user has not the rights to modify project, we redirect it
        # TODO: we could add a message to display to inform user that he coudn't do that
        return redirect('project_detail')

    project_form = ProjectCreationForm({'name':project.name, 'description':project.description})
    UserProjectFormset = modelformset_factory(UserProject, fields = ('user', 'user_role'), extra=0)
    user_project_formset = UserProjectFormset(queryset=UserProject.objects.filter(project=project))
    #TODO: modifier ce bout de code car ce n'est pas le meilleur endroit pour le faire
    for form in user_project_formset:
        for field_name, field in form.fields.items():
            if field_name == "user":
                field.widget.attrs['disabled'] = True
    #import pdb;pdb.set_trace()
    context = {
        'users_on_project' : user_project_formset,
        'project': project,
        'project_f' : project_form,
        'modifications':True}

    return render(request, 'projects/project_general_infos.html', context)


@login_required
@user_is_assigned_to_project # custom decorator : see decorators.py module
def modify_project(request, project_id):
    import pdb; pdb.set_trace()
    if request.method == "POST":
        datas = request.POST['datas_to_modify']
        for project_tuple in datas['project']:
            pass