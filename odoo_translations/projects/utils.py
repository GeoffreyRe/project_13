def nest_list(list):
    # refactoriser cette fonction avec une compréhension de liste
    index = 0
    max_index = len(list)
    nested = []
    while index < max_index:
        nested.append(list[index:index + 2])
        index += 2
    return nested