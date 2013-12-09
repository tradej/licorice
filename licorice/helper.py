
import re
import os

def tokenize(line, with_newline=False):
    ''' Split a line to a list of lowercase strings '''
    result = [str.lower(word) for word in re.compile(r'[^A-Za-z1-9%]').split(line) if word != '']
    if with_newline: return result + ['\n']
    else: return result


def search_score(no_of_locations, frequency):
    ''' Return search score of the word based on the wideness of use and
        frequency '''
    return float(no_of_locations) ** 2 / frequency

def get_files(path):
    ''' Get abspaths of all regular files in given path and subdirectories '''
    result = list()
    for root, dirs, files in os.walk(os.path.expandvars(path)):
        for f in [os.path.join(root, f) for f in files if os.path.isfile(os.path.join(root, f))]:
            result.append(os.path.abspath(f))
    return result

def path(path):
    return os.path.abspath(os.path.expandvars(path))
