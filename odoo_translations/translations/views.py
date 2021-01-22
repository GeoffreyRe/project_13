from django.shortcuts import render
from django.apps import apps
from django.contrib.auth.decorators import login_required
from projects.decorators import user_is_assigned_to_project
# Create your views here.

@login_required
@user_is_assigned_to_project
def model_translation_list(request, project_id):
    Project = apps.get_model('projects.Project')
    project = Project.objects.get(id=project_id)
    models = project.all_model_instances()

    context = {'instances': models,
                'instance_type': 'Modèles'}
    return render(request, 'translations/instances_list.html', context)

@login_required
@user_is_assigned_to_project
def model_translations(request, project_id, model_id):
    Project = apps.get_model('projects.Project')
    project = Project.objects.get(id=project_id)
    model, translation_lines = project.translations_models(model_id=model_id)

    context = {'translation_lines': translation_lines,
                'instance': model}
    return render(request, 'translations/instance_translations.html', context)

    

