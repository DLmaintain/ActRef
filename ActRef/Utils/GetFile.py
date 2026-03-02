import os

def get_python_files(folder_path):
    python_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.py') and file != 'merged.py':
                relative_path = os.path.relpath(os.path.join(root, file), folder_path)
                python_files.append(relative_path)
    return python_files

def getCommits(commits_folder_path):
    subfolders = [f for f in os.listdir(commits_folder_path) if os.path.isdir(os.path.join(commits_folder_path, f))]

    return subfolders