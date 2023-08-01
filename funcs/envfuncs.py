import os
from dotenv import load_dotenv


load_dotenv()


def get_var(key):
    foo = os.environ
    if key in os.environ:
        return os.environ[key]
    else:
        print('ERROR! {} NOT FOUND!'.format(key))
        return False
