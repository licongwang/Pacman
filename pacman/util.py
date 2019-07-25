import os


def get_path(file_name, dir_name):
    full_path = os.path.abspath(os.path.join(dir_name, file_name))
    return full_path
