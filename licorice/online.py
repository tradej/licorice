
from urllib import request
from urllib.parse import urlencode
from http.cookiejar import CookieJar
from lxml import html
import simplejson
import os

from licorice import config, helper, models

class Query:
    # Matching methods
    HASHSUM, SIZE, NAME = range(3)

    @classmethod
    def _get_file(cls, filename):
        url = config.ONLINE_FILE_URL.format(filename)
        response = request.urlopen(url).read()
        dictionary = simplejson.loads(response.decode('utf-8'))
        return dictionary

    @classmethod
    def _get_query(cls, full_path):
        filename = os.path.basename(full_path)
        hashsum = helper.hashsum(full_path)
        size = os.path.getsize(full_path)
        dictionary = cls._get_file(filename)

        # Three separate loops to ensure the ordering of matches
        for entry in dictionary:
            if hashsum == entry['fields']['hashsum']:
                return cls._form_query_result(entry['fields'], cls.HASHSUM)
        for entry in dictionary:
            if size == entry['fields']['size']:
                return cls._form_query_result(entry['fields'], cls.SIZE)
        for entry in dictionary:
            if filename == entry['fields']['filename']:
                return cls._form_query_result(entry['fields'], cls.NAME)
        return None

    def _form_query_result(dictionary, method):
        return models.QueryResult(\
                dictionary['filename'],
                method,
                dictionary['license'],
                dictionary['submitter'],
                dictionary['url'],
                dictionary['comment'],
                dictionary['upvotes'],
                dictionary['downvotes'])

    @classmethod
    def get_licenses(cls, full_path, licenses):
        result = set()
        query = cls._get_query(full_path)
        for shortname in query.licenses:
            for license in licenses:
                if shortname == license.short_name:
                    result.add(license)
                    break
        query.licenses = result
        return query

class Uploader:

    def __init__(self):
        self.login_url = config.ONLINE_LOGIN_URL
        self.add_url = config.ONLINE_ADD_URL
        self.opener = self._get_opener()
        self.logged_in = False

    def _get_opener(self):
        cj = CookieJar()
        return request.build_opener(request.HTTPCookieProcessor(cj),
                request.HTTPHandler(debuglevel=1))

    def _get_csrf_token(self, string):
        return html.fromstring(string).xpath(\
                '//input[@name="csrfmiddlewaretoken"]/@value')[0]

    def login(self, username, password):
        csrf_token = self._get_csrf_token(self.opener.open(self.login_url))
        values = {'login': username, 'password': password, \
                'csrfmiddlewaretoken': csrf_token}
        params = urlencode(values).encode('utf-8')
        self.opener.open(self.login_url)
        self.logged_in = True

    def upload(self, pfile):
        if not self.logged_in: self.login()
        csrf_token = self._get_csrf_token(self.opener.open(self.add_url))
        values = {
                'filename': pfile.filename,
                'size': os.path.getsize(pfile.path),
                'hashsum': helper.hashsum(pfile.path),
                'license': [l.shortname for l in pfile.licenses],
                'comment': 'Uploaded with licorice',
                'csrfmiddlewaretoken': csrf_token}

        params = urlencode(values).encode('utf-8')
        self.opener.open(self.add_url)
        self.logged_in = True
