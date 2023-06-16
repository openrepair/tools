import os
from pathlib import Path
from funcs import envfuncs


ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(ROOT_DIR, 'dat')
ORDS_DIR = os.path.join(ROOT_DIR, 'dat/ords')
OUT_DIR = os.path.join(ROOT_DIR, 'out')
LOG_DIR = os.path.join(ROOT_DIR, 'log')


if (not os.path.exists('dat')):
    os.mkdir('dat')
if (not os.path.exists('dat/ords')):
    os.mkdir('dat/ords')
if (not os.path.exists('out')):
    os.mkdir('out')
if (not os.path.exists('log')):
    os.mkdir('log')


def path_to_ords_csv():
    return ORDS_DIR + '/{}.csv'.format(envfuncs.get_var('ORDS_DATA'))


def check_path(path):
    return os.path.exists(path)


def get_path(path_list):
    return Path(*path_list)


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
                [path, filename, full_path.stat().st_mtime, full_path.stat().st_size])
    return filelist
