import os
from newcomers_guide import exceptions


def read_task_data(root_folder):
    task_data = []
    for root, _, filenames in os.walk(root_folder, topdown=False):
        for filename in filenames:
            path = os.path.join(root, filename)
            if is_task_file(path):
                task_data.append([path, read_file_content(path)])
    return task_data


def read_article_data(root_folder):
    article_data = []
    for root, _, filenames in os.walk(root_folder, topdown=False):
        for filename in filenames:
            path = os.path.join(root, filename)
            if is_article_file(path):
                article_data.append([path, read_file_content(path)])
    return article_data


def read_taxonomy_data(root_folder):
    taxonomy_data = []
    for root, _, filenames in os.walk(root_folder, topdown=False):
        for filename in filenames:
            path = os.path.join(root, filename)
            if is_taxonomy_file(path):
                taxonomy_data.append([path, read_file_content(path)])
    return taxonomy_data


def read_file_content(path):
    with open(path, 'r') as file:
        try:
            content = file.read()
            return content
        except ValueError as error:
            raise exceptions.DecodeError(path)


def is_task_file(path):
    sep = os.sep
    return path.find(sep + 'tasks' + sep) > 0 and not is_taxonomy_file(path)


def is_article_file(path):
    sep = os.sep
    return path.find(sep + 'articles' + sep) > 0 and not is_taxonomy_file(path)


def is_taxonomy_file(path):
    sep = os.sep
    return path.find(sep + 'taxonomy.txt') > 0