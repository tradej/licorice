
import os
import re

from fnmatch import fnmatch
from licorice import settings

def is_archive(path):
    '''
    Find if a given path is an archive
    '''
    return os.path.isfile(path) and os.path.splitext(path)[1] in settings.ARCHIVE_EXT


def is_ignored(path):
    '''
    Find if a given path is ignored and the file should not be loaded.
    '''
    for pattern in settings.IGNORED_FILES:
        if fnmatch(os.path.basename(path), pattern):
            return True
    return False


def get_word_frequencies(string):
    '''
    Get a dictionary of words and their frequencies in a string.
    '''
    result = dict()
    words = re.sub('[\W]', ' ', string)

    for word in words.split():
        if word not in result:
            result[word] = 1
        else:
            result[word] += 1

    return result
