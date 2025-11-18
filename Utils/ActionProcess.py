


def process_action(actions, src, dst):
    delete_node = []
    delete_tree = []
    insert_node = []
    insert_tree = []
    move_tree = []
    update_node = []

    for action in actions:

        if action is None:
            print('----------No diff-----------')
            continue
        # print(action)

        action_type = action.getName()
        # print(action)

        if action.getNode().getType().toString() not in ['classdef', 'funcdef','atom_expr', 'suite','name','parameters'] and ('stmt' not in action.getNode().getType().toString()):

            continue

        if action_type == 'move-tree':

            move_tree.append([action, src, dst])

        elif action_type == 'insert-node':


            insert_node.append([action, src, dst])
        elif action_type == 'delete-node':

            delete_node.append([action, src, dst])
        elif action_type == 'update-node':
            if action.getNode().getType().toString() != 'name':
                continue
            update_node.append([action,src,dst])

        elif action_type == 'delete-tree':
            delete_tree.append([action, src, dst])
        elif action_type == 'insert-tree':

            insert_tree.append([action,src, dst])
        else:
            print('action type error', action_type)
    return insert_node,insert_tree,delete_node,delete_tree,move_tree,update_node

def get_location(action):
    node = action.getNode()
    old = node.getParent()
    new_location = ''
    new_type = ''
    old_type = ''
    old_location = ''
    while old and 'def' not in old.toString() and 'file' not in old.toString():
        old = old.getParent()
    if 'file' in old.toString():
        old_location = 'Input Module'
        old_type = 'Module'
    else:
        old_type = ''
        old_location = ''
        for child in old.getChildren():
            if 'name' in child.toString():
                old_location = child.getLabel().toString()
                break
        if 'classdef' in old.toString():
            old_type = 'Class'
        elif 'funcdef' in old.toString():
            old_type = 'Method'
    
    if 'update' in action.getName():
        new_type = old_type
        new_location = old_location
    elif 'delete' in action.getName():
        new_type = None
        new_location = None
    elif 'move' in action.getName():
        
        _new_ = action.getParent()
        while _new_ and 'def' not in _new_.toString() and 'file' not in _new_.toString():
            _new_ = _new_.getParent()
        if 'file' in _new_.toString():
            new_location = 'Input Module'
            new_type = 'Module'
        else:
            new_type = ''
            new_location = ''
            for child in _new_.getChildren():
                if 'name' in child.toString():
                    new_location = child.getLabel()
                    break
            if 'classdef' in _new_.toString():
                new_type = 'Class'
            elif 'funcdef' in _new_.toString():
                new_type = 'Method'
            elif 'stmt' in _new_.toString():
                new_type = 'Expression'
    if 'insert' in action.getName():
        old_type = None
        old_location = None

    return old_type, old_location, new_type, new_location

def get_Name_Type(Node):
    Name = None
    if 'def' in Node.toString():
        for child in Node.getChildren():
            if 'name' in child.toString():
                Name = child.getLabel()
                break
        if 'classdef' in Node.toString():
            Type = 'Class'
        else:
            Type = 'Method'
        return Name, Type
    return None, None