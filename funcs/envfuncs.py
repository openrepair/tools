import os
from dotenv import load_dotenv


load_dotenv()


def get_var(key):
    if key in os.environ:
        return os.environ[key]
    else:
        print('ERROR! {} NOT FOUND!'.format(key))
        return False
