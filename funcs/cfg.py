import os
import ast
import logging
from dotenv import load_dotenv
load_dotenv()

if not os.path.exists("dat"):
    os.mkdir("dat")
if not os.path.exists("dat/ords"):
    os.mkdir("dat/ords")
if not os.path.exists("log"):
    os.mkdir("log")
if not os.path.exists("out"):
    os.mkdir("out")

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "dat", "")
ORDS_DIR = os.path.join(ROOT_DIR, "dat/ords")
LOG_DIR = os.path.join(ROOT_DIR, "log", "")
OUT_DIR = os.path.join(ROOT_DIR, "out", "")

def init_logger(caller):

    filename, file_ext = os.path.splitext(os.path.basename(caller))
    path = os.path.join(LOG_DIR, filename + '.log')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(path, mode='w')
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    return logger

def get_envvar(key):

    if key in os.environ:
        return os.environ[key]
    else:
        print('ERROR! {} NOT FOUND!'.format(key))
        return False

def get_dbvars(con="ORDS_DB_CONN"):

    try:
        dbstr = os.environ.get(con)
        dbdict = ast.literal_eval(dbstr)
        return dbdict
    except Exception as error:
        print("Exception: {}".format(error))
        return False

def get_version():

    return "0.0.1"

