
import linecache
from collections import defaultdict
from licorice.helper import get_chunk_from_list, load_file_to_str

class License(object):

    def __init__(self, name, path, **kwargs):
        self.name = name
        self.path = path
        self.contents = load_file_to_str(path)
        self.splitcontents = self.contents.split()
        self.keyword_positions = defaultdict(lambda: list())

        self._chunks = dict()

    def chunks(self, keyword, offset):
#        try:
#            return self._chunks[keyword]
#        except KeyError:
#            result = list()
#            for pos in self.keyword_positions[keyword]:
#                result.append(' '.join(get_chunk_from_list(self.splitcontents, pos, 10)))
#            self._chunks[keyword] = result
#            return result
        result = list()
        for pos in self.keyword_positions[keyword]:
            result.append(' '.join(get_chunk_from_list(self.splitcontents, pos, offset)))
        return result


class LargeFile(object):

    def __init__(self, path):
        self.path = path
        self.handle = open(path, 'r')

