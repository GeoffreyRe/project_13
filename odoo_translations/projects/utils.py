import json
from django.apps import apps
def nest_list(list):
    index = 0
    max_index = len(list)
    nested = []
    while index < max_index:
        nested.append(list[index:index + 2])
        index += 2
    return nested

def organise_datas(datas, files):
    organised_datas = {}
    organised_datas['infos_user'] = json.loads(datas['infos_user'])

    new_files = []
    files_number = json.loads(datas['files_total'])
    for file_number in range(files_number):
        file_infos = {
            'lang': datas['lang_' + str(file_number)],
            'template': json.loads(datas['template_' + str(file_number)]),
            'file': files['file_' + str(file_number)]
        }
        new_files.append(file_infos)
    organised_datas['files'] = new_files
    organised_datas['files_to_delete'] = json.loads(datas['files_to_delete'])
    organised_datas['config_files_to_delete'] = json.loads(datas['config_files_to_delete'])
    if files.get('config_file', False):
        organised_datas['config_file'] = files['config_file']

    return organised_datas

def regroup_lines_by_block(lines):
    """
    This function will regroup lines into block for presentation purpose
    lines --> TranslationLine object
    return --> a list of lists. each sublist is a "block"
    """
    lines_in_blocks = []
    blocks = []
    InstanceType = apps.get_model('translations.InstanceType')
    module_type = InstanceType.objects.get(name="module")
    for line in lines:
        # for each line, we check if we already add it into a block
        # if it is the case, we don't add it a second time (but can be changed)
        # else, we find other lines of the block of the line (excepted module line and the line itself)
        if line.id in lines_in_blocks:
            continue

        lines_in_blocks.append(line.id)
        related_lines =line.block.translation_lines.exclude(
            instance__instance_type=module_type).exclude(
                instance__instance_type=module_type).exclude(id=line.id)
        related_lines_ids = related_lines.values_list('id', flat=True)
        
        lines_in_blocks += related_lines_ids
        blocks.append({'id':line.block.id,
        'lines': [line] + [related_line for related_line in related_lines]})
    return blocks

