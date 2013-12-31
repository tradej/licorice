
from http.client import HTTPConnection
import simplejson
import os

from licorice import config, helper

class Server:
    # Matching methods
    HASHSUM, SIZE, NAME = range(3)

    @classmethod
    def _get_file(cls, filename):
        conn = HTTPConnection(config.ONLINE_HOST, port=config.ONLINE_PORT)
        conn.request('GET', config.ONLINE_URL.format(filename))
        val = conn.getresponse().read()
        dictionary = simplejson.loads(val.decode('utf-8'))
        return dictionary

    @classmethod
    def get_licenses(cls, full_path):
        filename = os.path.basename(full_path)
        hashsum = helper.md5(full_path)
        size = os.path.getsize(full_path)
        dictionary = cls._get_file(filename)

        for entry in dictionary:
            print(size, entry['fields']['size'])
            if hashsum == entry['fields']['hashsum']:
                result = entry['fields']['license']
                return result, cls.HASHSUM
            if size == entry['fields']['size']:
                result = entry['fields']['license']
                return result, cls.SIZE
            if filename == entry['fields']['filename']:
                result = entry['fields']['license']
                return result, cls.NAME
