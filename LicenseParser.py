#!/usr/bin/env python

import os
import re

class Project:
    ''' Project holding all files and their licenses '''
    def __init__(self, name, files = [], licenses = [])
        self.name = name
        self.files = dict(zip(files, licenses))

class License:
    ''' License '''

    def __init__(self, name, regex):
        self.name = str(name)
        self.regex = str(regex)
        self.matcher = re.compile(self.regex)

class LicenseParser:
    ''' Parse license in list of lines '''

    def __init__(self, licenses):
        self.licenses = licenses

    def find_license(self, lines):
        for line in lines:
            for license in self.licenses:
                print license.name + ' ' + str(license.matcher.match(line))
                    
if __name__ == '__main__':
    licenses = [License(x,y) for x,y in [
        ('GPL v1', ''), 
        ('ASL 1.0', 'a*d'), 
        ('GPL v3', '.*b.f')]]
    parser = LicenseParser(licenses)
    parser.find_license(['abc', 'def', 'abdef', 'defabc'])

        



