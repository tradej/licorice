
import os

_ROOT = os.path.abspath(os.path.dirname(__file__))

def get_dir(path):
    return os.path.join(_ROOT, path)
