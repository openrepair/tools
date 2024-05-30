import os
import sys
import ast
import logging
from dotenv import load_dotenv

load_dotenv()


def init_dirs():
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)
    if not os.path.exists(OUT_DIR):
        os.mkdir(OUT_DIR)


# ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = sys.prefix
DATA_DIR = os.path.join(ROOT_DIR, "dat", "")
ORDS_DIR = os.path.join(ROOT_DIR, "dat/ords")
LOG_DIR = os.path.join(ROOT_DIR, "log", "")
OUT_DIR = os.path.join(ROOT_DIR, "out", "")

init_dirs()


def init_logger(caller):

    venv = sys.prefix != sys.base_prefix
    filename, file_ext = os.path.splitext(os.path.basename(caller))
    path = os.path.join(LOG_DIR, filename + ".log")
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(path, mode="w")
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    logger.debug(f"VENV? {venv}")
    logger.debug(f"ROOT_DIR {ROOT_DIR}")
    logger.debug(f"DATA_DIR {DATA_DIR}")
    logger.debug(f"LOG_DIR {LOG_DIR}")
    logger.debug(f"OUT_DIR {OUT_DIR}")
    return logger


def get_envvar(key):

    if not key in os.environ:
        raise KeyError(f"KEY NOT FOUND {key}")
    return os.environ[key]


def get_dbvars(key="ORDS_DB_CONN"):

    val = get_envvar(key)
    vars = ast.literal_eval(val)
    assert vars["host"]
    assert vars["database"]
    assert vars["user"]
    assert vars["pwd"]
    assert vars["collation"]
    return vars
