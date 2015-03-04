
import mmap
import re

from collections import defaultdict
from licorice.helper import get_chunk_from_list, load_file_to_str

class License(object):

    def __init__(self, name, path, **kwargs):
        self.name = name
        self.path = path
        with open(path) as fh:
            self.contents = fh.read().lower()
        self._kw_positions = dict()

    def contains(self, word):
        return bool(self.positions(word))

    def positions(self, word):
        if word not in self._kw_positions:
            self._kw_positions[word] = [match.start() for match in re.finditer(word, self.contents)]

        return self._kw_positions[word]

    def first_offset(self, word):
        return self.positions(word)[0]

    def last_offset(self, word):
        return len(self.contents) - self.positions(word)[-1]


class MappedFile(object):

    def __init__(self, path):
        self.path = path
        with open(path, 'rb') as fh:
            try:
                self._mmap = mmap.mmap(fh.fileno(), 0, prot=mmap.PROT_READ)
            except ValueError:
                self._mmap = b''
        self._length = -1

    def occurrences(self, keyword):
        '''
        Get an iterator over positions of a keyword in file
        '''
        if isinstance(keyword, str):
            keyword = keyword.encode('utf-8')
        return (match.start() for match in re.finditer(keyword, self._mmap))

    def get(self, start, end):
        return self._mmap[start:end].decode('utf-8').lower()

    @property
    def length(self):
        if self._length == -1:
            self._length = len(self._mmap)
        return self._length
