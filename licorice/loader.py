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
from licorice import exceptions, helper, settings

def get_paths(path_list):
    nonexistent = list()
    archives = list()
    ready = list()
    errors = list()
    ignored = list()

    for path in path_list:

        # Nonexistent paths
        if not os.path.exists(path):
            nonexistent.append(path)
            continue

        # Ignored files
        if helper.is_ignored(path):
            ignored.append(path)
            continue

        # Files
        if os.path.isfile(path):
            if helper.is_archive(path):
                archives.append(path)
            else:
                ready.append(path)
            continue

        # Directories
        if os.path.isdir(path):
            results = get_paths([os.path.join(path, f) for f in os.listdir(path)])

            nonexistent.extend(results['nonexistent'])
            archives.extend(results['archives'])
            ready.extend(results['ready'])
            errors.extend(results['errors'])
            ignored.extend(results['ignored'])

            continue

        # Block specials, devices, named pipes etc.
        errors.append(path)
        continue

    return {'ready': ready, 'nonexistent': nonexistent, 'archives': archives, 'errors': errors, 'ignored': ignored}

