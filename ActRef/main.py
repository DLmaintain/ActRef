import Refactorings.ModuleRefactoring as ModuleRefactoring
from Utils.ParseFile import parse, str_parse
import os
from Utils.ActionProcess import process_action, get_location
from Refactorings.CalculateRefactoring import calculate_pair, cross_file_match
import csv
import time
import json


dir = 'commits'
subfolders = [f for f in os.listdir(dir) if os.path.isdir(os.path.join(dir, f))]

times = []
for subfolder in subfolders:
    print(f'----------!{subfolder}!----------')
    insert_nodes = []
    insert_trees = []
    delete_nodes = []
    delete_trees = []
    start_t = time.time()
    pairs, before_unpairs, after_unpairs, refactoring_list = ModuleRefactoring.GetModuleRefactoring(subfolder)
    empty = 'empty.py'

    if len(before_unpairs) + len(after_unpairs) <= 1:
        only_pair = True
    else:
        only_pair = False
    for pair in pairs:
        actions = parse(pair[0], pair[1])
        insert_node,insert_tree,delete_node,delete_tree,move_tree,update_node = process_action(actions,pair[0],pair[1])
        insert_node = insert_node + insert_tree
        delete_node = delete_node + delete_tree
        insert_node, delete_node, refactoring_list = calculate_pair(insert_node, delete_node, move_tree,update_node,refactoring_list)
        insert_nodes = insert_nodes + insert_node
        delete_nodes = delete_nodes + delete_node

    for before in before_unpairs:
        actions = parse(before, empty)
        insert_node,insert_tree,delete_node,delete_tree,move_tree,update_node = process_action(actions,before,empty)

        delete_nodes = delete_nodes + delete_node + delete_tree
    for after in after_unpairs:
        actions = parse(empty, after)
        insert_node,insert_tree,delete_node,delete_tree,move_tree,update_node = process_action(actions,empty,after)
        insert_nodes = insert_nodes + insert_node + insert_tree

    res = cross_file_match(refactoring_list, delete_nodes, insert_nodes)
    ref_lit = []
    if len(res) == 0:
        ref_lit = [[subfolder, None, None, None, None]]
    for r in res:
        if list([subfolder] + r) not in ref_lit:
            if 'empty.py' in r:
                continue
            ref_lit.append(list([subfolder] + r))
    end_t = time.time()

    for ref in ref_lit:
        print(ref)
    with open('result.csv','a+') as f:
        csv_write = csv.writer(f)
        for ref in ref_lit:
            
            csv_write.writerow(ref)
    times.append([subfolder, end_t-start_t])


    
