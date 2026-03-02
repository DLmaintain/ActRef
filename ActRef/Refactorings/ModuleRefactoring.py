# from Utils.GetFile import get_python_files
# from Utils.FileProcess import is_empty_file, split_into_code_blocks, file_similarity
import os
from difflib import SequenceMatcher
import sys
sys.path.append("..")
# import Utils.GetFile
# import Utils.FileProcess
from Utils import FileProcess,GetFile


def GetModuleRefactoring(SHA):
    folder1 = 'commits/' + SHA + '/Before'
    folder2 = 'commits/' + SHA + '/After'

    
    files1 = GetFile.get_python_files(folder1)
    files2 = GetFile.get_python_files(folder2)

    Before_unpair_files = []
    After_unpair_files = []
    pairs = []
    refactoring_list = []



    relative_files1 = {os.path.relpath(f, folder1): f for f in files1}
    relative_files2 = {os.path.relpath(f, folder2): f for f in files2}
    all_files = set(relative_files1.keys()).union(set(relative_files2.keys()))
    # print(all_files)
    detect_inlineM = []
    detect_extractM = []
    caled = []
    for file in all_files:
        path1 = relative_files1.get(file)
        path2 = relative_files2.get(file)
        if path1 and path2:

            if FileProcess.is_empty_file('commits/' + SHA + '/Before/' + path1):

                After_unpair_files.append('commits/' + SHA + '/After/' + path2)
            elif FileProcess.is_empty_file('commits/' + SHA + '/After/' + path2):

                Before_unpair_files.append('commits/' + SHA + '/Before/' + path1)
            else:
                if not FileProcess.file_similarity('commits/' + SHA + '/Before/' + path1, 'commits/' + SHA + '/After/' + path2):
                    detect_extractM.append('commits/' + SHA + '/Before/' + path1)
                    detect_inlineM.append('commits/' + SHA + '/After/' + path2)
           

                pairs.append(['commits/' + SHA + '/Before/' + path1, 'commits/' + SHA + '/After/' + path2])
            relative_files1.pop(file, None)
            relative_files2.pop(file, None)
        elif path1 and not path2:

            Npath1 = 'commits/' + SHA + '/Before/' + path1
            if path1 in caled:
                continue
            pairable = False
     
            for relative_file, path_in_folder2 in relative_files2.items():
                similarity_score = FileProcess.file_similarity(Npath1, 'commits/' + SHA + '/After/' + path_in_folder2)
                if similarity_score:
                    caled.append(path1)
                    caled.append(path_in_folder2)
                    relative_files1.pop(path1, None)
                    relative_files2.pop(path_in_folder2, None)
       
                    pairable = True

                    if (path1.split('#')[0:-1]) == (path_in_folder2.split('#')[0:-1]):
                        refactoring_list.append(['Rename Module',path1,path_in_folder2])
     
                  
                        # print(f'[Rename Module] {path1} is renamed to {path_in_folder2}')
                    else:
                        move_path = path_in_folder2.rsplit('#', 1)
                        move_path = move_path[0]
                        from_path = path1.rsplit('#', 1)
                        from_path = from_path[0]
                        refactoring_list.append(['Move Module',path1, from_path, move_path])

                    if 'commits/' + SHA + '/Before/' + path1 in Before_unpair_files:
                        Before_unpair_files.remove('commits/' + SHA + '/Before/' + path1)
                    if 'commits/' + SHA + '/After/' + path_in_folder2 in After_unpair_files:
                        After_unpair_files.remove('commits/' + SHA + '/After/' + path_in_folder2)
                        # print(f'[Move Module] {path1} is moved to path {move_path}')
                    # pairs.append([Npath1, 'commits/' + SHA + '/After/' + path_in_folder2])
                    break
            if pairable == False :
                Before_unpair_files.append(Npath1)
        elif path2 and not path1:
            if path2 in caled:
                continue
            Npath2 = 'commits/' + SHA + '/After/' + path2
     
            pairable = False
            for relative_file, path_in_folder1 in relative_files1.items():
                similarity_score = FileProcess.file_similarity('commits/' + SHA + '/Before/' + path_in_folder1, Npath2)
                if similarity_score:
                    caled.append(path2)
                    caled.append(path_in_folder1)
             
                    pairable = True

                    relative_files1.pop(path_in_folder1, None)
                    relative_files2.pop(path2, None)
                    if path_in_folder1.split('#')[0:-1] == path2.split('#')[0:-1]:
                        # print(f'[Rename Module] {path_in_folder1} is renamed to {path2}')
                        refactoring_list.append(['Rename Module',path_in_folder1,path2])
                    else:
                        # print(f'[Move Module] {path_in_folder1} is moved to path {path2.rsplit("#", 1)[0]}')
                        refactoring_list.append(['Move Module',path_in_folder1, path2.rsplit("#", 1)[0]])

                    if 'commits/' + SHA + '/Before/' + path_in_folder1 in Before_unpair_files:
                        Before_unpair_files.remove('commits/' + SHA + '/Before/' + path_in_folder1)
                    if 'commits/' + SHA + '/After/' + path2 in After_unpair_files:
                        After_unpair_files.remove('commits/' + SHA + '/After/' + path2)
                        
                    # pairs.append(['commits/' + SHA + '/Before/' + path_in_folder1, Npath2])
                    break

            if pairable == False:
                After_unpair_files.append(Npath2)
    for before in Before_unpair_files:
        matches, refactoring_list = detect_inline_module(before, detect_inlineM, refactoring_list)
        if matches:
            Before_unpair_files.remove(before)

    for after in After_unpair_files:

        matches, refactoring_list = detect_extract_module(detect_extractM, after, refactoring_list)
        if matches:
            After_unpair_files.remove(after)

    return pairs, Before_unpair_files,After_unpair_files, refactoring_list



def detect_extract_module(before_files, new_file, refactoring_list):
    new_code = open(new_file, 'r', encoding='utf-8').read()
    new_code_blocks = FileProcess.split_into_code_blocks(new_code) 
    if len(new_code_blocks) <= 1:
        return False, refactoring_list
    matched_blocks = []
    from_files = []
    for before_file in before_files:
        before_code = open(before_file, 'r', encoding='utf-8').read()
        before_code_blocks = FileProcess.split_into_code_blocks(before_code)  
        if len(before_code_blocks) <= 1:
            continue
        for new_block in new_code_blocks:
            for before_block in before_code_blocks:
                if  SequenceMatcher(None, new_block, before_block).ratio() >= 0.7:  
                    matched_blocks.append(new_block)
                    from_files.append(before_file)


    if len(matched_blocks) / len(new_code_blocks) > 0.7:
        # print(f"[Extract Module] New file {new_file} extracted from previous files")
        refactoring_list.append(['Extract Module', new_file, set(from_files)])
        return True, refactoring_list
    else:
        return False, refactoring_list




def detect_inline_module(old_file, after_files, refactoring_list):
    old_code  = open(old_file, 'r', encoding='utf-8').read()
    old_code_blocks = FileProcess.split_into_code_blocks(old_code)  
    if len(old_code_blocks) <= 1:
        return False, refactoring_list
    matched_blocks = []
    to_files = []
    for after_file in after_files:
        after_code = open(after_file, 'r', encoding='utf-8').read()
        after_code_blocks = FileProcess.split_into_code_blocks(after_code)  
        if len(after_code_blocks) <= 1:
            continue
        for old_block in old_code_blocks:
            for after_block in after_code_blocks:
                if SequenceMatcher(None, old_block, after_block).ratio() >= 0.7:  
                    matched_blocks.append(old_block)
                    to_files.append(after_file)

    if len(matched_blocks) / len(old_code_blocks) > 0.7:
        # print(f"[Inline Module] Old file {old_file} inlined into new files")
        refactoring_list.append(['Inline Module', old_file, set(to_files)])
        return True, refactoring_list
    else:
        return False, refactoring_list


