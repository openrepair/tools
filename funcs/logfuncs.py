import os
import logging
from funcs import pathfuncs


def init_logger(caller):

    filename, file_ext = os.path.splitext(os.path.basename(caller))
    path = os.path.join(pathfuncs.LOG_DIR, filename + '.log')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(path, mode='w')
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    return logger
