from difflib import SequenceMatcher
import os


def split_into_code_blocks(code):
    blocks = code.split("\n\n")
    print(blocks)
    return blocks


import re


def get_code_snip(file, l, r):
    with open(file) as f:
        src = f.read()
        return src[l:r]
    
def file_similarity(file1, file2):
    with open(file1, 'r', encoding='utf-8', errors='ignore') as f1, open(file2, 'r', encoding='utf-8', errors='ignore') as f2:
        content1 = f1.read()
        content2 = f2.read()
        if SequenceMatcher(None, content1, content2).ratio() >= 0.9:
            return True
        else:
            return False


def is_empty_file(file_path):
    return os.path.getsize(file_path) <=10