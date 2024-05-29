import os
from pathlib import Path


def check_path(path):
    return os.path.exists(path)


def get_path(path_list):
    return Path(*path_list)


def get_filename(path):
    return Path(path).name


def get_filestem(path):
    return Path(path).stem


def rm_file(path):
    if os.path.exists(path):
        os.remove(path)
    return not os.path.exists(path)


def copy_file(src, dst):
    os.system(f'cp "{src}" "{dst}"')


def file_list(path):
    filelist = []
    for row in os.walk(path):
        for filename in row[2]:
            full_path: Path = Path(row[0]) / Path(filename)
            filelist.append(
                [path, filename, full_path.stat().st_mtime, full_path.stat().st_size]
            )
    return filelist
