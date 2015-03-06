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
