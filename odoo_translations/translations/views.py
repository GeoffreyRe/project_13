from django.shortcuts import render
from django.apps import apps
from django.contrib.auth.decorators import login_required
from projects.decorators import user_is_assigned_to_project
# Create your views here.

@login_required
@user_is_assigned_to_project
def instance_translation_list(request, project_id, instance_type):
    instances_dict = {'models': 'ir.model', 'views': 'ir.ui.view'}
    Project = apps.get_model('projects.Project')
    project = Project.objects.get(id=project_id)
    instances = project.all_instances(type=instances_dict[instance_type])

    context = {'instances': instances,
                'instance_type': instance_type,
                'project': project}
    return render(request, 'translations/instances_list.html', context)

@login_required
@user_is_assigned_to_project
def instance_translations(request, project_id, instance_id, instance_type):
    Project = apps.get_model('projects.Project')
    project = Project.objects.get(id=project_id)
    instance, translation_lines = project.translations_instances(instance_id=instance_id)

    context = {'translation_lines': translation_lines,
                'instance': instance,
                'project': project}
    return render(request, 'translations/instance_translations.html', context)
    

