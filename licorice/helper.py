
import os
import re

def sanitize(string, to_replace=None):
    '''
    Translate special characters to spaces and squash any multiple spaces
    into one space.

    to_replace: regex to replace with a space. [\W] by default

    returns: lowercase string of non-whitespace chars and spaces
    '''
    first_pass = re.sub('[\W]', ' ', string) # Special chars
    second_pass = re.sub('  +', ' ', first_pass) # Multiple spaces
    return second_pass.lower().strip()


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


def load_file_to_str(path):
    '''
    Load file to a string and sanitize it.

    path: path to file (variables will be expanded)
    '''
    if not os.path.isfile(path):
        raise IOError('Can not load {path}: not a file'.format(path=path))

    with open(path) as fh:
        contents = fh.read()

    return sanitize(contents)


def get_chunk_from_list(words, index, offset):
    beginning = max(0, index-offset)
    end = min(index+offset, len(words))
    return words[beginning:end]
