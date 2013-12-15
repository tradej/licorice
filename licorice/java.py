
import re

from licorice import models

class JavaHelper():

    import_string = 'import(?: static)? ([a-zA-Z0-9_.]+);'

    @classmethod
    def imports(cls, filename):
        '''Get all imported packages from a file'''
        result = set()
        for index, line in enumerate(open(filename)):
            matches = re.findall(cls.import_string, line)
            if matches:
                result |= set(([cls.get_package_name(path) for path in \
                        matches if not path.startswith('java')]))
        return result

    @classmethod
    def get_package_name(cls, string):
        '''Get the package name out of a string. A package name is the longest
        string of comma-separated, all-lowercase names. In case a wildcard is
        used at the end, it is stripped.'''
        if string.endswith('.*'):
            string = string[0:-2]

        for name in string.split('.'):
            if not name.islower():
                string = string[0:string.index(name)-1]
                break

        return string

    @classmethod
    def get_grupid_artifactid_from_maven(cls, string):
        pass

