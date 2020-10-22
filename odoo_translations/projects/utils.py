import json

def nest_list(list):
    # refactoriser cette fonction avec une compréhension de liste
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

    return organised_datas