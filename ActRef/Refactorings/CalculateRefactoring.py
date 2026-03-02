from Utils.ParseFile import str_parse
from Utils.ActionProcess import process_action, get_location, get_Name_Type
from difflib import SequenceMatcher

def is_child(parent,node):
    for child in parent.getChildren():
        if ('name' in child.toString()) and (node.getLabel() ==  child.getLabel()):
            return True
    return False

def get_code_snip(file, l, r):
    with open(file) as f:
        src = f.read()
        return src[l:r]

# def get_params(Node):
#     params = []
#     if ('def' in Node.getType().toString()):
#         for child in Node.getChildren():
#             if 'param' in child.toString():
#                 for gChild in child.getChildren():
#                     if 'param' in gChild.toString():
#                         for ggchild in gChild.getChildren():
#                             print(ggchild)
    

def calculate_pair(insert_node,  delete_node,  move_tree, update_node, refactoring_list):
    rename = []
    tmp_list = []

    for item in update_node[:]:
        # print('Update!!!!')

        # print(item.getNode().getParent())

        used = False
    

        old_type, old_location, new_type, new_location = get_location(item[0])
        node = item[0].getNode()
        newnode = item[0].getNewNode()
        if node.getType().toString() !='name' :
            continue
        # l = node[0].getNode().getPos()
        # r = node[0].getNode().getEndPos()
 
        # print(get_code_snip(file,l,r))

        parent = node.getParent()


  
        if [node.getLabel().toString(), item[0].getValue()] in rename:
            continue
        Name = node.getLabel().toString()
        if parent.getType().toString() == 'classdef':
            for child in parent.getChildren():
                if 'name' in child.toString():
                    Name = child.getLabel()
                    break
            if Name != node.getLabel().toString():
                continue
            

            # print(f'[Rename Class] Class {node.getLabel()} is renamed to {item.getValue()}')
            # rename.append([node.getLabel().toString(), item.getValue()])
            
            for insert in insert_node[:]:
                inode = insert[0].getNode()

                if Name == inode.getLabel().toString():
                    if 'classdef' in inode.getParent().toString():
                        refactoring_list.append(['Extract Class', item[0].getValue(),  node.getLabel(), old_type, old_location, item[1], item[2]])
                        used = True
                        break
            for delete in delete_node[:]:
                dnode = delete[0].getNode()
                if item[0].getValue().toString() == dnode.getLabel().toString():
                    if 'classdef' in dnode.getParent().toString():
                        refactoring_list.append(['Inline Class', Name, item[0].getValue(), old_type, old_location, item[1], item[2]])
                        used = True
                        break
            if used == True:
                continue
            tmp = True
            for sublist in refactoring_list[:]:
                if (str(node.getLabel()) == sublist[2] and
                    str(item[0].getValue()) == sublist[1] and
                    'Rename ' in sublist[0]):
                    refactoring_list.remove(sublist)
                    tmp = False
                    continue            
            if tmp == False:
                continue
            refactoring_list.append(['Rename Class', node.getLabel(), item[0].getValue(), old_type, old_location, item[1], item[2]])
            update_node.remove(item)

        elif parent.getType().toString() == 'funcdef':
         
            # print(f'[Rename Method] Method {node.getLabel()} is renamed to {item.getValue()}')
            # rename.append([node.getLabel().toString(), item.getValue()])
            for insert in insert_node[:]:
                inode = insert[0].getNode()

                if node.getLabel().toString() == inode.getLabel().toString():

                    if 'funcdef' in inode.getParent().toString():
                        refactoring_list.append(['Extract Method', item[0].getValue(),  node.getLabel(), old_type, old_location, item[1], item[2]])
                        used = True
                        break
            for delete in delete_node[:]:
                dnode = delete[0].getNode()
                if item[0].getValue().toString() == dnode.getLabel().toString():
                    if 'funcdef' in dnode.getParent().toString():
                        refactoring_list.append(['Inline Method', Name, item[0].getValue(), old_type, old_location, item[1], item[2]])
                        used = True
                        break
            if used == True:
                continue

            if '__init__' in node.getLabel().toString() or '__init__' in item[0].getValue():
                continue
            tmp = True
            for sublist in refactoring_list[:]:
                if (str(node.getLabel()) == sublist[2] and
                    str(item[0].getValue()) == sublist[1] and
                    'Rename ' in sublist[0]):

                    refactoring_list.remove(sublist)
                    tmp = False
                    continue            
            if tmp == False:
                continue
            refactoring_list.append(['Rename Method', node.getLabel(), item[0].getValue(), old_type, old_location, item[1], item[2]])
            update_node.remove(item)
        elif 'expr_stmt' in parent.getType().toString():
            # print(f'[Rename Variable] Variable {node.getLabel()} is renamed to {item.getValue()}')
            # rename.append([node.getLabel().toString(),item.getValue()])
            if node.getPos() - parent.getPos() >=2:
                continue
            if '__init__' in str(old_location):
                refactoring_list.append(['Rename Parameter', node.getLabel(), item[0].getValue(), old_type, old_location, item[1], item[2]])
                continue
                # print('maybe is parameter')
            # news = item[0].getValue()
            # java_class = news.getClass()
            # java_method = java_class.getMethods()
            # for j in java_method:
            #     print('heres!')
            #     print(j)
            old_expression = get_code_snip(item[1], node.getEndPos(), parent.getEndPos())
            new_expression = get_code_snip(item[2], newnode.getEndPos(), newnode.getParent().getEndPos())
            if SequenceMatcher(None, old_expression, new_expression).ratio() < 0.7:
                # print('Not a Rename Variable!!!')
                # print(old_expression)
                # print(new_expression)
                continue


            if old_location != new_location:
                tmp = True
                for ref in refactoring_list:
                    if 'Method' in ref[0]:
                        if old_location == ref[1] or old_location == ref[2]:
                            tmp = False
                            break
                if tmp == True:
                    continue
            tmp = True
            for sublist in refactoring_list[:]:
                
                if (str(node.getLabel()) == sublist[2] and
                    str(item[0].getValue()) == sublist[1] and
                    'Rename ' in sublist[0]):
                    refactoring_list.remove(sublist)
                    tmp = False
                    continue 
            if tmp == False:
                continue
            refactoring_list.append(['Rename Variable', node.getLabel(), item[0].getValue(), old_type, old_location, item[1], item[2]])
   
            # print(parent.getParent())
            update_node.remove(item)

        # elif 'para' in parent.getType().toString():
        #     # print(f'[Rename Parameter] Parameter {node.getLabel()} is renamed to {item.getValue()}')
        #     # rename.append([node.getLabel().toString(), item.getValue()])
        #     if 'def' not in parent.getParent().getType().toString():
        #         continue
        #     refactoring_list.append(['Rename Parameter', node.getLabel(), item[0].getValue(), old_type, old_location, item[1], item[2]])
        #     update_node.remove(item)


    for item in move_tree[:]:

        node = item[0].getNode()
        dst_loc = item[0].getParent()
        dl = dst_loc.getPos()
        dr = dst_loc.getEndPos()
        l = node.getPos()
        r = node.getEndPos()
        old_type, old_location, new_type, new_location = get_location(item[0])
        # print(old_type, old_location, new_type, new_location)
        # print(item)
        # print('0000000000000000')
        
        if node.getType().toString() == 'suit' or 'stmt' in node.getType().toString():
            
            used = False
            for del_item in delete_node[:]:
                del_node = del_item[0].getNode()
                if used == True:
                    break
                if ('def' in del_node.getType().toString()) and 0<=(l - del_node.getPos()) and 0<=(del_node.getEndPos() - r):
                    for child in del_node.getChildren():
                        if 'name' in child.toString():
                            Name = child.getLabel()
                            break
                    if old_location != Name:
                        # print(f'Not inlined: {old_location} or {Name}')
                        continue
                    inline_type = del_node.getType().toString()
                    if inline_type == 'funcdef':
                        element_type = 'Method'
                    elif inline_type == 'classdef':
                        element_type = 'Class'
                    else:
                        continue
                    if any((Name in sublist) and 'Rename ' in sublist[0] for sublist in refactoring_list):
                        continue
                    if Name == new_location:
                        continue
                    refactoring_list.append(['Inline '+element_type, Name , old_location, new_type, new_location,item[1], item[2]])
                    
                    # print(f'[Inline {element_type}] {element_type} {Name} is inlined')

                    delete_node.remove(del_item)
                    used = True
            
            for add_item in insert_node[:]:
                if used == True:
                    break
                add_node = add_item[0].getNode()
                # print(add_item.getParent().getPos(),add_item.getParent().getEndPos(),dl,dr)
     
                if 'def' in add_node.getType().toString() and ( add_item[0].getParent().getPos() <= dl) and (dr<=add_item[0].getParent().getEndPos()):
                    Name = add_node.getLabel()
                    for child in add_node.getChildren():
                        if 'name' in child.toString():
                            Name = child.getLabel()
                            break
                    # print(Name,new_location,'@@@@')
                    if new_location != Name:
                        # print(f'Not extracted, {new_location} or {Name}')
                        continue
                    extract_type = add_node.getType().toString()
                    if extract_type == 'funcdef':
                        element_type = 'Method'
                    elif extract_type == 'classdef':
                        element_type = 'Class'
                    for child in add_node.getChildren():
                        if 'name' in child.toString():
                            Name = child.getLabel()
                            break
                    
                    if Name.toString() == old_location:
                        continue
                    # if str(Name.toString()) not in str(get_code_snip(item[2],dl,dr)):
                    #     print(Name)
                    #     print(get_code_snip(item[2],dl,dr))
                    #     print('Not match')
                    #     continue
                    refactoring_list.append(['Extract '+element_type, Name, old_location, old_location,item[1], item[2]])
                    
                    # print(f'[Extract {element_type}] {element_type} {Name} is extracted')
                    insert_node.remove(add_item)
                    used = True

        elif node.getType().toString() == 'atom_expr':
            dst_loc = item[0].getParent()
            dl = dst_loc.getPos()
            dr = dst_loc.getEndPos()
            l = node.getPos()
            r = node.getEndPos()
            used = False
            for del_item in delete_node[:]:
                if used == True:
                    break
                if del_item[0].getNode().getType().toString() == 'name' and  0<=(l - del_item[0].getNode().getEndPos())<=3 and del_item[0].getNode().getParent().getType().toString() == 'expr_stmt':
                    if 'expr_stmt' not in node.getParent().getType().toString():
                        continue
                    if old_location != new_location:
                        tmp = True
                        for ref in refactoring_list:
                            if 'Method' in ref[0]:
                                if old_location == ref[1] or old_location == ref[2]:
                                    tmp = False
                                    break
                        if tmp == True:
                            continue
                    
                    refactoring_list.append(['Inline Variable', del_item[0].getNode().getLabel(), old_location, new_type, new_location,item[1], item[2]])
                    # print('!!!!!!!', del_item[0].getNode().getParent())
                    # print(item)
                    # print(del_item[0])
                    delete_node.remove(del_item)
                    used = True
            if dst_loc.getType().toString() == 'expr_stmt':
                for add_item in insert_node[:]:
                    if add_item[0].getNode().getType().toString() == 'name':
                        if add_item[0].getParent() == dst_loc:
                            # if str(add_item[0].getNode().getLabel()) not in str(get_code_snip(item[2],dl,dr)):
                            VariableName = str(add_item[0].getNode().getLabel())
                            Expression = get_code_snip(add_item[2], add_item[0].getParent().getPos()-1, add_item[0].getParent().getEndPos())
                            Expression = Expression.lstrip()
                            if not Expression.startswith(VariableName):
                                # print('Not Extract Variable')
                                # print(Expression)
                                # print(VariableName)
                                continue
                            if old_location != new_location:
                                tmp = True
                                for ref in refactoring_list:
                                    if 'Method' in ref[0]:
                                        if old_location == ref[1] or old_location == ref[2]:
                                            tmp = False
                                            break
                                if tmp == True:
                                    continue
                            refactoring_list.append(['Extract Variable', VariableName,Expression, old_location, new_location, item[1], item[2]])
                            insert_node.remove(add_item)
                            # print(f'[Extract Variable] Variable {add_item[0].getNode().getLabel()} is extracted')
        elif 'def' in node.getType().toString():
            # if old_location == new_location:
            #     continue
            # print(item)
            
            
            # print('src is: ',src)
            # print('dst is: ',item.getParent())
            # srcName = old_location
            # newdst = None
            # while src and src.getParent() and 'def' not in src.toString():
            #     src = src.getParent()
            # # print(src)
            # for child in src.getChildren():
            #     if 'name' in child.toString():
            #         srcName = child.getLabel()
            #         break
            Name = None
            for child in node.getChildren():
                if 'name' in child.toString():
                    Name = child.getLabel()
                    break
            if Name == '__init__':
                continue
            move_type =node.getType().toString()
            if move_type == 'funcdef':
                element_type = 'Method'
            elif move_type == 'classdef':
                element_type = 'Class'
            else:
                continue
            # dst = item.getParent()
            # print('dst is: ',dst.toString())
            # print('dstn is:',  )
            # while dst.getParent() and 'def' not in dst.toString() :
            #     dst = dst.getParent()
            #     # print('dstnn is:', dst.toString())
            # if 'def' not in dst.toString() or not dst.getParent():
            #     continue
            # # print('dsts is: ',dst.toString())
            # dst = dst.getParent()
            # while dst.getParent() and 'def' not in dst.toString() :
            #     dst = dst.getParent()
            #     # print('dstnn1 is:', dst.toString())
            
            # for child in dst.getChildren():
            #     newdst = None
            #     if 'name' in child.toString():
            #         newdst = child.getLabel()
            #         # print('new dst name is:', newdst)
            #         break
            
            # if 'funcdef' in dst.toString():
            #     dst_type = 'Method'
            # elif 'classdef' in dst.toString():
            #     dst_type = 'Class'
            # else:
            #     # print(dst.toString())
            #     dst_type = ''
            # if not newdst:
            #     continue
            tmp = ['Class', 'Method', 'Module']
            if (new_type not in tmp) or (old_type not in tmp):
         
                continue
            if not Name:
                continue
            Name = str(Name)
            if old_location and (old_location != new_location):
  
                dstcode = get_code_snip(item[2], dl,dr)

                # if ('def '+Name not in dstcode) and ('class '+Name not in dstcode):
                #     print(item[0])
                #     print(f'action destination error: move action for {Name} to {item[0].getParent()} in {item[1]} and {item[2]}')
                #     continue
                # srccode = get_code_snip(item[1], dl,dr)
                # if ('def '+Name in srccode) or ('class '+Name in srccode):
                #     print(item[0])
                #     print(f'gumtree error : action destination error: move action for {Name} to {item[0].getParent()} in {item[1]} and {item[2]}')
                #     continue
                extract = False
                exclass = False
                for ins in insert_node[:]:
                    if str(new_location) in ins[0].getNode().getLabel():
                        exclass = True
                if exclass == True:
                    for i in range(len(refactoring_list)):
                        if 'Move '+ element_type in refactoring_list[i][0]:
                            if refactoring_list[i][5] == str(new_location) and element_type == 'Method' and new_location == 'Class':
                                refactoring_list[i][0] = 'Extract Class'
                                refactoring_list[i][1] = new_location
                                refactoring_list[i][2] = old_location
                                refactoring_list[i][3] = item[1]
                                refactoring_list[i][4] = item[2]
                                extract = True
                if extract == True:
                    continue
                refactoring_list.append(['Move '+ element_type, Name,old_type, old_location, new_type, new_location,item[1], item[2]])
                # print(f'[Move {element_type}] {element_type} {Name} is moved  from {srcName} to {dst_type} {newdst}')
    
    # for item in insert_node:
    #     node = item.getNode()
    #     if 'def' in node.getType().toString():
    #         tmp_list.append(['insert',node, item.getParent()])
    # for item in delete_node:
    #     node = item.getNode()
    #     parent = node.getParent()
    #     if 'def' in node.getType().toString():
    #         tmp_list.append([node, parent,'Method'])
    #     elif ('name' in node.getType().toString()) and (parent.getType().toString() == 'expr_stmt'):
    #         tmp_list.append([node, parent,'Variable'])
    # print('remaining!!!')
    # for de in delete_node:
    #     print(de[0])
    # for ins in insert_node:
    #     print(ins[0])
    # print('Remaining over@@@@')


    return insert_node, delete_node, refactoring_list


def cross_file_match(refactoring_list, delete_nodes, insert_nodes):
    # dele = False
    # ins = False
    # print('here cross')
    deletes = delete_nodes
    inserts = insert_nodes 
    # print(deletes)
    # print('1111111111')
    # print(inserts)
    # print('222222222')
    for delete_node in deletes[:]:
        dele = False
        # if dele:
        #     continue
        for insert_node in inserts[:]:

            if dele:
                break
            if insert_node[2].split('/')[-1] == delete_node[1].split('/')[-1]:

                continue

            delete_code = extract_code_from_node(delete_node)
            insert_code = extract_code_from_node(insert_node)
            if len(delete_code.split(' ')) <= 3 or len(insert_code.split(' ')) <= 3:
                continue
            if SequenceMatcher(None, delete_code, insert_code).ratio() < 0.5:
                continue
  
            actions = str_parse(delete_code, insert_code)
            if len(actions) == 0 and SequenceMatcher(None, delete_code, insert_code).ratio() > 0.7:
                if 'def' in delete_node[0].getNode().toString():
                    OName = delete_node[0].getNode().getLabel()
                    if 'def' in insert_node[0].getNode().toString():
                        new_N, new_T = get_Name_Type(delete_node[0].getNode())
                        old_N, old_T = get_Name_Type(insert_node[0].getNode())
                        if new_T == old_T:
                            
                            for child in delete_node[0].getNode().getChildren():
                                if 'name' in child.toString():
                                    OName = child.getLabel()
                                    break
                            NName = insert_node[0].getNode().getLabel()
                            for child in insert_node[0].getNode().getChildren():
                                if 'name' in child.toString():
                                    NName = child.getLabel()
                                    break
                            
                            refactoring_list.append([f'Move {new_T}',OName, NName, old_N, new_N, delete_node[1], insert_node[2] ])
                            # print(delete_code)
                            # print(insert_code)
                            print(f'Move {new_T}',OName, NName, old_N, new_N, delete_node[1], insert_node[2])
                            dele = True
                            break
            for i, action in enumerate(actions):
                if action is None:

                    continue

                if 'move' in action.getName():
                    if 'def' in delete_node[0].getNode().toString():
                        OName = delete_node[0].getNode().getLabel()
                        if 'def' in insert_node[0].getNode().toString():
                            for child in delete_node[0].getNode().getChildren():
                                if 'name' in child.toString():
                                    OName = child.getLabel()
                                    break
                            NName = insert_node[0].getNode().getLabel()
                            for child in insert_node[0].getNode().getChildren():
                                if 'name' in child.toString():
                                    NName = child.getLabel()
                                    break
                            new_N, new_T = get_Name_Type(insert_node[0].getNode())
                            old_N, old_T = get_Name_Type(delete_node[0].getNode())
                            if new_T == old_T:
                                
                                for i in range(len(refactoring_list)):
                                    if 'Inline' in refactoring_list[i][0]:
                                        element = refactoring_list[i][0].replace('Inline ','')
                                        name = refactoring_list[i][1]
                                        if name == OName:
                                            continue
                                    if 'Extract' in refactoring_list[i][0]:
                                        element = refactoring_list[i][0].replace('Extract ','')
                                        name = refactoring_list[i][1]
                                        if name == NName:
                                            continue
                                refactoring_list.append([f'Move {new_T}',OName, NName, old_N, new_N, delete_node[1], insert_node[2] ])
                                # print(delete_code)
                                # print(insert_code)
                                print(f'Move {new_T}',OName, NName, old_N, new_N, delete_node[1], insert_node[2])
                                dele = True
                                break
                            elif new_T == 'Class':
                                dele = True
                                exits = False
                                for i in range(len(refactoring_list)):
                                    if 'Extract' in refactoring_list[i][0]:
                                        if NName == refactoring_list[i][1] and delete_node[1] == refactoring_list[i][5]:
                                            refactoring_list[i][2] = 'Module '+ refactoring_list[i][5]
                                            refactoring_list[i][3] = 'Module '+ refactoring_list[i][5]
                                            exits = True
                                if exits == True:
                                    break
                                refactoring_list.append(['Extract Class', NName, OName, old_N, new_N, delete_node[1], insert_node[2]])
                                break
                            else:
                                if not new_N or not old_N:
                                    continue       
                                exits = False
                                for i in range(len(refactoring_list)):
                                    if 'Inline' in refactoring_list[i][0]:
                                        if NName == refactoring_list[i][1] and delete_node[1] == refactoring_list[i][5]:
                                            refactoring_list[i][2] = 'Module '+ refactoring_list[i][5]
                                            refactoring_list[i][3] = 'Module '+ refactoring_list[i][5]
                                            exits = True
                                if exits == True:
                                    break                        
                                refactoring_list.append(['Inline Class',  NName, OName,old_N,new_N, delete_node[1], insert_node[2]])

                                # print(delete_code)
                                # print(insert_code)
                                print('Inline Class',  NName, OName,old_N,new_N, delete_node[1], insert_node[2])

                                dele = True
                                break
                            # print(delete_node)
                            # deletes.remove(delete_node)
                            # inserts.remove(insert_node)
                            # dele = True
                            # ins = True

                        else:
                            old_N, old_T = get_Name_Type(delete_node[0].getNode())
                            old_type, old_location, new_type, new_location = get_location(insert_node[0])
                            for i in range(len(refactoring_list)):
                                if 'Inline' in refactoring_list[i][0]:
                                    element = refactoring_list[i][0].replace('Inline ','')
                                    name = refactoring_list[i][1]
                                    if name == OName:
                                        continue
                            # print('here111111')
                            # print(action)
                            # print('here2222222')
                            # print(insert_code)
                            refactoring_list.append([f'Inline {old_T}', old_N, 'Statements',new_type, new_location, delete_node[1], insert_node[2]])
                            print(f'Inline {old_T}', old_N, 'Statements',new_type, new_location, delete_node[1], insert_node[2])

                            dele = True
                            break
                            # deletes.remove(delete_node)
                            # inserts.remove(insert_node)
                            # dele = True
                            # ins = True
                    else:
                        if 'def' in insert_node[0].getNode().toString():
                            new_N, new_T = get_Name_Type(insert_node[0].getNode())

                            old_type, old_location, new_type, new_location = get_location(delete_node[0])

                            refactoring_list.append([f'Extract {new_T}', new_N, 'Statements',old_type, old_location, delete_node[1], insert_node[2]])
                            dele = True
                            print(f'Extract {new_T}', new_N, 'Statements',old_type, old_location, delete_node[1], insert_node[2])

                            break
                            # deletes.remove(delete_node)
                            # inserts.remove(insert_node)
                            # dele = True
                            # ins = True
                elif 'update' in action.getName():

                    if ('classdef' in insert_node[0].getNode().toString()) and 'classdef' in delete_node[0].getNode().toString():
                        new_N, new_T = get_Name_Type(delete_node[0].getNode())
                        old_N, old_T = get_Name_Type(insert_node[0].getNode())
                        refactoring_list.append(['Rename Class', old_N, new_N, delete_node[1],insert_node[1],delete_node[1],insert_node[1]])
                        dele = True
                        break
                    elif ('funcdef' in insert_node[0].getNode().toString()) and 'classdef' in delete_node[0].getNode().toString():
                        new_N, new_T = get_Name_Type(delete_node[0].getNode())
                        old_N, old_T = get_Name_Type(insert_node[0].getNode())
                        if '__init__' in old_N or '__init__' in new_N:
                            continue
                        refactoring_list.append(['Rename Method', old_N, new_N, delete_node[1],insert_node[1],delete_node[1],insert_node[1]])
                        dele = True
                        break
    return refactoring_list

def extract_code_from_node(node):
    if 'delete' in node[0].getName().toString():
        file = node[1]
    else:
        file = node[2]
    l = node[0].getNode().getPos()
    r = node[0].getNode().getEndPos()
    return get_code_snip(file,l,r)


