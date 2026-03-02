import jpype.imports
# # jpype.startJVM(classpath=['gumtree0.8.jar'])
# jpype.startJVM(classpath=['/Users/siqiwang/Desktop/MyProjects/jar/gumtree_str_loc.jar'])


jpype.startJVM(classpath=['/home/siqiwang/Refactoring/ActRef/jar/gumtreet2.jar'])


# jpype.startJVM(classpath=['/Users/siqiwang/Desktop/MyProjects/jar/gumtree.jar'])
import os
from jpype import JException
# 导入必要的 GumTree 类
from com.github.gumtreediff.client import Run
from com.github.gumtreediff.gen import TreeGenerators
from com.github.gumtreediff.tree import FakeTree
from com.github.gumtreediff.matchers import Matchers, MappingStore

from com.github.gumtreediff.matchers.heuristic.gt import GreedySubtreeMatcher
from com.github.gumtreediff.matchers.CompositeMatchers import ClassicGumtree

from com.github.gumtreediff.actions import SimplifiedChawatheScriptGenerator,ChawatheScriptGenerator
from com.github.gumtreediff.actions.model import TreeAction, TreeAddition, TreeDelete, TreeInsert, Move, Update, Addition, Delete, Insert


def determine_node_type(node):
    node_type = node.getType().name
    return node_type

def determine_parent_node_type(node):
    parent_node = node.getParent()
    if parent_node:
        parent_type = determine_node_type(parent_node)
        return parent_type
    else:
        return 'Unknown'
    
def get_subtree_info(node, level=0):
    indent = "  " * level
    node_type = determine_node_type(node)
    info = f"{indent}- {node.getLabel()} (Type: {node_type})"
    for child in node.getChildren():
        info += "\n" + get_subtree_info(child, level + 1)
    return info


def parse(src_file, dst_file):
    Run.initGenerators()
    res = []
    try:
        src_tree_context = TreeGenerators.getInstance().getTree(src_file)  
        dst_tree_context = TreeGenerators.getInstance().getTree(dst_file)
    except JException as ex:
        print(f"SyntaxException encountered: {ex}")
        return None, None 
    src_root = src_tree_context.getRoot()
    dst_root = dst_tree_context.getRoot()
    default_matcher = Matchers.getInstance().getMatcher()
    mappings = default_matcher.match(src_root, dst_root)
    # matcher = GreedySubtreeMatcher()
    # # # # 或者：使用 ZsMatcher
    # # # # matcher = ZsMatcher()
    # # # 或者：使用 ClassicGumtree 复合匹配器
    # # matcher = ClassicGumtree()
    # # # 使用自定义的 matcher 进行匹配
    # mappings = matcher.match(src_root, dst_root)
    edit_script_generator = SimplifiedChawatheScriptGenerator()
    edit_script = edit_script_generator.computeActions(mappings)
    actions = []
    for action in edit_script:
        actions.append(action)
    return actions



def str_parse(src, dst):
    Run.initGenerators()

    try:
        src_tree_context = TreeGenerators.getInstance().getTreeFromCodeSnippet(src, "python-pythonparser")
        dst_tree_context = TreeGenerators.getInstance().getTreeFromCodeSnippet(dst, "python-pythonparser")
    except JException as ex:
        print(f"SyntaxException encountered (cross): {ex}")
        return None, None  


    src_root = src_tree_context.getRoot()
    dst_root = dst_tree_context.getRoot()
    default_matcher = Matchers.getInstance().getMatcher()
    mappings = default_matcher.match(src_root, dst_root)

    # matcher = GreedySubtreeMatcher()
    # # # 或者：使用 ZsMatcher
    # # # matcher = ZsMatcher()
    # # 或者：使用 ClassicGumtree 复合匹配器
    # # matcher = ClassicGumtree()

    # # 使用自定义的 matcher 进行匹配
    # mappings = matcher.match(src_root, dst_root)
    edit_script_generator = SimplifiedChawatheScriptGenerator()
    edit_script = edit_script_generator.computeActions(mappings)
    actions = []
    for action in edit_script:
        actions.append(action)
        # print('cross: ')
        # print(action)
    return actions
    
    

   




# actions = parse('/Users/siqiwang/Desktop/MyProjects/commits/1f023926d224cc0108073e33f913a5c6b98972ed/Before/pyro#distributions#constraints.py','/Users/siqiwang/Desktop/MyProjects/commits/1f023926d224cc0108073e33f913a5c6b98972ed/After/pyro#distributions#constraints.py')
# # for acti in actions:
# #     print(acti)