from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.forms import modelformset_factory
from django.db import transaction
from users.models import User
from translations.forms import TranslationFileForm
from translations.models import TranslationFile
from .utils import nest_list, organise_datas
from .forms import ProjectCreationForm, RoleForm
from .models import Project, Invitation, UserProject
from .decorators import user_is_assigned_to_project
from translations.exceptions import FileParsingError


@login_required
def projects_list_view(request):
    # user = user connected
    user = request.user
    projects = user.userproject_set.all()
    # project_nested = we create a list of list for displaying projects correctly on page
    projects_nested = nest_list(projects)
    project_form = ProjectCreationForm()
    context = {
        "projects": projects_nested,
        "is_odds": False if len(projects) % 2 == 0 else True,
        'form': project_form}
    return render(request, "projects/projects_list.html", context)


@login_required
def invitations_list_view(request):
    invitations = request.user.project_invitations.all()
    context = {'invitations': invitations}
    return render(request, "projects/invitations_list.html", context)


@login_required
def create_project(request):
    if request.method == 'POST':
        vals = {
            'name': request.POST['name'],
            'description': request.POST['description'],
            'creation_date': request.POST['initial-creation_date'],
            'creator': request.user}
        Project.objects.create_new_project(vals)
    return redirect("projects_list")


@login_required
def view_verification_project_name(request):
    if request.method == "POST":
        current_user = request.user
        project_name = request.POST.get('project_name', None)
        exists = Project.objects.project_already_exists_for_creator(current_user, project_name)
        return JsonResponse({'project_exists': exists}, safe=False, status=200)


@login_required
def from_invitation_to_project(request):
    if request.method == "POST":
        result = True
        invitation_id = request.POST.get('invitation_id', None)
        try:
            invitation_id = int(invitation_id)
        except ValueError:
            result = False
            return JsonResponse({'success': result}, safe=False, status=200)

        invitation = Invitation.objects.get(id=invitation_id)
        if invitation is not None:
            result = invitation.from_invitation_to_project()
        return JsonResponse({'success': result}, safe=False, status=200)


@login_required
def invitation_refused(request):
    if request.method == "POST":
        invitation_id = request.POST.get('invitation_id', None)
        success = False
        if invitation_id is not None:
            try:
                invitation_id = int(invitation_id)
            except ValueError:
                return JsonResponse({'success': success}, safe=False, status=200)
            invitation = Invitation.objects.get(id=invitation_id)
            if invitation is not None:
                invitation.is_refused()
                success = True
            return JsonResponse({'success': success}, safe=False, status=200)
        return JsonResponse({'success': success}, safe=False, status=200)


@login_required
@user_is_assigned_to_project  # custom decorator : see decorators.py module
def detail_project(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except ObjectDoesNotExist:
        # TODO : à retravailler pour rediriger vers une page avec un message explicite
        return HttpResponse("Le projet demandé n'existe pas")
    users_on_project = UserProject.objects.filter(project=project)
    has_write_rights = request.user.has_rights_to_modify_project(project)
    translation_files = TranslationFile.objects.filter(project=project)
    context = {
        'users_on_project': users_on_project,
        'project': project,
        'files': translation_files,
        'config_files': project.config_files.all(),
        'has_write_rights': has_write_rights,
        'modifications': False}

    return render(request, 'projects/project_general_infos.html', context)


@login_required
@user_is_assigned_to_project  # custom decorator : see decorators.py module
def detail_project_modifications(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except ObjectDoesNotExist:
        # TODO : à retravailler pour rediriger vers une page avec un message explicite
        return HttpResponse("Le projet demandé n'existe pas")
    if not request.user.has_rights_to_modify_project(project):
        # if user has not the rights to modify project, we redirect it
        # TODO: we could add a message to display to inform user that he coudn't do that
        return redirect('detail_project', project_id=project.id)

    project_form = ProjectCreationForm({'name': project.name, 'description': project.description})
    UserProjectFormset = modelformset_factory(UserProject, fields=('user', 'user_role'), extra=0)
    user_project_formset = UserProjectFormset(queryset=UserProject.objects.filter(project=project))
    new_file_form = TranslationFileForm()
    translation_files = TranslationFile.objects.filter(project=project)

    context = {
        'users_on_project': user_project_formset,
        'project': project,
        'files': translation_files,
        'config_files': project.config_files.all(),
        'project_f': project_form,
        'modifications': True,
        'role_form': RoleForm,
        'file_form': new_file_form}

    return render(request, 'projects/project_general_infos.html', context)


@login_required
@user_is_assigned_to_project  # custom decorator : see decorators.py module
def modify_project(request, project_id):
    if request.method == "POST":
        user = request.user
        datas = organise_datas(request.POST, request.FILES)
        project_to_modify = Project.objects.get(id=datas['infos_user']['project']['id'])
        project_to_modify.update_project(datas, user)

        return JsonResponse({'success': True}, safe=False, status=200)


def check_if_users_can_be_added_to_project(request):
    if request.method == 'POST':
        datas = request.POST['datas']
        for user_email, user_role, project_id in datas:
            try:
                user = User.objects.get(email=user_email)
            except ObjectDoesNotExist:
                return JsonResponse({'success': False}, safe=False, status=200)
            if not user.is_on_project(project_id):
                return JsonResponse({'success': False}, safe=False, status=200)

        return JsonResponse({'success': True}, safe=False, status=200)


def launch_analysis(request, project_id):
    success = True
    error_message = ""
    try:
        project = Project.objects.get(id=project_id)
    except ObjectDoesNotExist:
        success = False

    if success:
        try:
            with transaction.atomic():
                project.delete_translations()
                project.analyze_translation_files()
        except FileParsingError as e:
            success = False
            error_message = str(e)

    return JsonResponse({
        'success': success,
        'error_message': error_message
        }, safe=False, status=200)


@login_required
@user_is_assigned_to_project  # custom decorator : see decorators.py module
def export_translation_file(request, project_id, lang):
    if request.method == "GET":
        project = apps.get_model('projects.Project').objects.get(id=project_id)
        filename = lang + ".po"
        content = project.export_translations(lang=lang)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
        return response
