
import itertools
import os
import re

from licorice.helper import tokenize

class Project:
    ''' Project holding all files and their licenses '''
    def __init__(self, name, files):
        self.licenses = None
        self.name = name
        self.files = files
        self.license_file = None

class FileInProject:
    def __init__(self, path, licenses = []):
        self.path = path
        self.filename = os.path.basename(path)
        self.extension = os.path.splitext(self.filename)
        self.licenses = licenses
        self.skip = False

    def is_archive(self):
        return self.extension in { '.bz2', '.gz', '.tar', '.jar', '.war', '.zip' }

class License:
    def __init__(self, name, config, files):
        self.name = name
        self.config = config
        self.files = files
        self.cachedfiles = [CachedFile(f, parent=self) for f in self.files]



class CachedFile:
    def __init__(self, path, parent=None):
        self.path = os.path.abspath(os.path.expandvars(path))
        self.parent = parent
        self._lines = dict()
        self._locations = dict()
        self._iterators = dict()
        self._load_lines()
        self._wholetext = list(itertools.chain(*self._lines.values()))
        self.length = len(self._lines)

    def _load_lines(self):
        with open(self.path) as f:
            for index, line in enumerate(f):
                self._lines[index] = tokenize(line)

    def get_line(self, line_number):
        return self._lines[line_number]

    def length(self):
        return len(self._lines)

    def _cache_word_location(self, word):
        result = list()
        for index, iword in enumerate(CachedFileIterator(self._wholetext, 0)):
            if iword == word:
                result.append(index)
        self._locations[word] = result

    def get_locations(self, word):
        if word not in self._locations:
            self._cache_word_location(word)
        return self._locations[word]

    def _cache_iterator(self, starting_position, backwards):
        self._iterators[(starting_position, backwards)] = \
            CachedFileIterator(self._wholetext, starting_position, backwards)

    def iterator(self, starting_position, backwards=False):
        if (starting_position, backwards) not in self._iterators:
            self._cache_iterator(starting_position, backwards)
        self._iterators[(starting_position, backwards)].reset()
        return self._iterators[(starting_position, backwards)]

class CachedFileIterator:
    def __init__(self, text, offset, backwards=False):
        self._halted = False
        self.newline_seen = False
        self.finished = False
        self._text = text
        self._initial_offset = offset
        self._offset = offset
        self._coefficient = [1, -1][int(backwards)]

    def __iter__(self):
        return self

    def __next__(self):
        if self._offset < 0 or self._offset >= len(self._text):
            raise StopIteration()
        result = self._text[self._offset]
        if not self._halted:
            self._offset += self._coefficient
        return result

    def next(self):
        return self.__next__()

    def reset(self):
        self._offset = self._initial_offset
        self._halted = False
        self.newline_seen = False
        self.finished = False

    def halt(self):
        self._halted = True

    @property
    def halted(self):
        return self._halted

    def resume(self):
        self._halted = False
        self._offset += self._coefficient



class BackwardFileGenerator:
    def __init__(self, path, start_line, start_word, bufsize=2): # bufsize in lines
        self.path = os.path.abspath(os.path.expandvars(path))
        self.start_line = start_line
        self.start_word = start_word
        self._bufsize = bufsize
        self._buffer_start = None
        self._line_number = start_line

    def _load_buffer(self):
        result = list()
        with open(self.path) as f:
            for index, line in enumerate(f):
                if index > self._line_number: break # Reached far end of buffer
                if index == self._line_number - self._bufsize or index == 0:
                    self._buffer_start = index # Reached near end of buffer
                if index > self._line_number - self._bufsize:
                    if index == self.start_line:
                        result.extend(tokenize(line, with_newline=True)[:self.start_word])
                    else:
                        result.extend(tokenize(line, with_newline=True))
        return reversed(result)

    def get_words(self):
        while True: # needs to run once for line_number=0 too
            for word in self._load_buffer():
                yield word
            self._line_number = self._buffer_start
            if self._line_number <= 0: break



class ForwardFileGenerator:
    def __init__(self, path, start_line, start_word):
        self.path = os.path.abspath(os.path.expandvars(path))
        self._start_line = start_line
        self._start_word = start_word

    def get_words_with_coordinates(self):
        with open(self.path, 'r') as f:
            for line_index, line in enumerate(f):
                if line_index < self._start_line: continue
                if line_index == self._start_line:
                    current_line = tokenize(line, with_newline=True)[self._start_word:]
                else:
                    current_line = tokenize(line, with_newline=True)
                for word_index, word in enumerate(current_line):
                    yield word, line_index, word_index

    def get_words(self):
        for word, line_index, word_index in self.get_words_with_coordinates():
            yield word
