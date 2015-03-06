# Copyright (C) 2015  Tomas Radej <tradej@redhat.com> #
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re

from collections import defaultdict
from fuzzywuzzy import fuzz

class LicenceMatcher(object):
    '''
    Class matching licences, snippets, copyright notices etc. in files
    '''

    def __init__(self, licences, keywords):
        self.licences = licences
        self.keywords = keywords

    def get_licences(self, mappedfile, threshold=95):
        '''
        Get all licences from a given file with a given threshold

        mappedfile: a model.MappedFile instance to be analyzed
        threshold: a threshold for licences to be recognized
        '''
        found_licences = defaultdict(lambda: 0)
        for kw in self.keywords:
            m_occurrences = mappedfile.occurrences(kw)
            for m_occurrence in m_occurrences:
                for licence in (l for l in self.licences if l.contains(kw) and found_licences[l] < threshold):
#                    if licence.name == 'gpl3-snippet':
#                        print('TEXT', m_occurrence, mappedfile.get(m_occurrence-10, m_occurrence+10))
                    match = 0
                    for l_occurrence in licence.positions(kw):
#                        if licence.name == 'gpl3-snippet':
#                            print('LICENCE', licence.contents[l_occurrence-10:l_occurrence+10])
                        if m_occurrence - l_occurrence < 0: # License's prefix is longer than file's prefix
                            continue

                        end = len(licence.contents) - l_occurrence
                        if end > mappedfile.length: # License's suffix is longer than the file's length
                            continue

                        bad = False
                        for offset in (o for o in (10, 50, 200, end) if o <= end):
                            if bad:
                                break
                            temp_start = max(l_occurrence - offset - len(kw), 0)
                            temp_end = min(l_occurrence + offset + len(kw), len(licence.contents))
                            lic_str = re.sub('[\W]+', ' ', licence.contents[temp_start:temp_end])
                            try:
                                matched_str = re.sub('[\W]+', ' ', mappedfile.get(m_occurrence - l_occurrence, m_occurrence + temp_end))
                            except UnicodeDecodeError:
                                raise exceptions.RunTimeError('Error reading {}'.format(mappedfile.path))

                            match = fuzz.token_set_ratio(lic_str, matched_str)
                            if match < threshold:
                                bad = True
                                match = 0
                                continue

                        if match > found_licences[licence]:
                            found_licences[licence] = match

        return dict([(l, score) for l, score in found_licences.items() if score > 0])
