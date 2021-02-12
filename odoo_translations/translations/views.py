from django.shortcuts import render
from django.apps import apps
from django.contrib.auth.decorators import login_required
from projects.decorators import user_is_assigned_to_project
from django.http import HttpResponse, JsonResponse
# Create your views here.

INSTANCES_DICT = {'models': 'ir.model',
    'views': 'ir.ui.view',
    'menus': 'ir.ui.menu',
    'action-windows': 'ir.actions.act_window',
    'codes': 'code',
    'other': 'other'}

@login_required
@user_is_assigned_to_project
def instance_translation_list(request, project_id, instance_type):
    
    Project = apps.get_model('projects.Project')
    project = Project.objects.get(id=project_id)
    instances = project.all_instances(type=INSTANCES_DICT[instance_type])

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



@login_required
@user_is_assigned_to_project
def all_instance_translations(request, project_id, instance_type):
    Project = apps.get_model('projects.Project')
    project = Project.objects.get(id=project_id)
    instances, translation_lines = project.translations_instances(type=INSTANCES_DICT[instance_type])

    context = {'translation_lines': translation_lines,
                'instance_type': instance_type,
                'project': project}
    return render(request, 'translations/instance_translations.html', context)


@login_required
def get_block_translation(request):
    if request.method == "GET":
        
        block_id = int(request.GET['block'])
        Block = apps.get_model('translations.TranslationBlock')
        block = Block.objects.get(id=block_id)
        
        return JsonResponse({'success' : True, 'translation': block.translated_text}, safe=False, status=200)
    

