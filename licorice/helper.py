
import os
import re
from licorice import settings

def is_archive(path):
    return os.path.isfile(path) and os.path.splitext(path)[1] in settings.ARCHIVE_EXT

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
