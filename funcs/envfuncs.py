import os
from dotenv import load_dotenv


load_dotenv()


def get_var(key):
    return os.environ[key]
