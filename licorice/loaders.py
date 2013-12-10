
import os
import re
import subprocess
from collections import defaultdict

from licorice import helper
from licorice.models import FileInProject, Project, License
from licorice.parser import LicenseParser

class ProjectLoader:
    @staticmethod
    def load_project(destinations):
        '''Load contents of a software project - file, directory, archive
        :param path: Path where the project is to be found
        '''
        filelist = set()
        for path in destinations:
            if os.path.isdir(path):
                filelist = ProjectLoader.load_directory(path)
            elif ProjectLoader.is_archive(path):
                filelist = ProjectLoader.load_archive(path)
            elif os.path.isfile(path):
                filelist.add(ProjectLoader.load_file(path))
            else:
                raise Exception('File type not supported: %s' % path)

        return Project(os.path.basename(destinations[0]), sorted(filelist,
            key=lambda x: x.path))

    @classmethod
    def load_directory(cls, path):
        '''Get files from a directory recursively
        :param path: Path to the directory
        '''
        filelist = set()
        if not os.path.isdir(path):
            raise IOError("%s is not a directory!" % path)
        for root, dirs, files in os.walk(path):
            for filename in files:
                full_path = os.path.join(root, filename)
                if os.path.isdir(full_path):
                    filelist.union(ProjectLoader.load_directory(full_path))
                elif ProjectLoader.is_archive(full_path):
                    filelist.union(ProjectLoader.load_archive(full_path))
                elif os.path.isfile(full_path):
                    filelist.add(ProjectLoader.load_file(full_path))
                else:
                    pass #raise OSError('Filetype not supported: %s' % full_path)
        return filelist

    @classmethod
    def load_file(cls, filename):
        '''Get a file
        :param filename: Full and expanded path to file
        '''
        if not os.path.isfile(filename):
            raise IOError("%s is not a file!" % filename)
        return FileInProject(filename)

    @staticmethod
    def load_archive(path, tmpdir=''):
        '''Get an archive. The archive is unpacked in the process
        :param path: Path to the archive
        :param tmpdir: Directory where to unpack the archive
        '''
        # TODO Checking if user has writing access + fallback
        if not tmpdir:
            tmpdir = path + '-unpacked'
        if not os.path.exists(tmpdir):
            os.mkdir(tmpdir)

        working_directory = os.getcwd()
        os.chdir(tmpdir)

        # Extract file based on the extension
        subprocess.call({
            '.bz2' : ["tar", "xjf", path],
            '.gz'  : ["tar", "xzf", path],
            '.jar' : ["jar", "xf", path],
            '.tar' : ["tar", "xf", path],
            '.war' : ["jar", "xf", path],
            '.zip' : ["unzip", '-f', path],
        }[os.path.splitext(path)[1]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        os.chdir(working_directory)
        return ProjectLoader.load_directory(path + '-unpacked')

    @staticmethod
    def is_archive(path):
        # TODO Code duplication with FileInProject
        return os.path.splitext(path)[1] in { '.bz2', '.gz', '.tar', '.jar', '.war', '.zip' }

class MainLicenseLoader:

    def get_license_parser(self, path):
        '''Get license parser with definitions obtained from a given directory
        :param path: License definitions directory
        '''
        (licenses, keywords) = self.get_all_licenses_and_keywords(path)
        return LicenseParser(licenses, keywords)

    def get_all_licenses_and_keywords(self, path):
        ''' Get a list of licenses and keywords to be searched.
            keywords is a dictionary in form
            { 'keyword' : [ its locations ] }
        '''
        words_occurrences = defaultdict(lambda: set())
        words_frequencies = defaultdict(lambda: 0)
        licenses = list()

        for f in helper.get_files(path):
            license = License(name=os.path.splitext(os.path.basename(f))[0], path=f)
            words = SingleLicenseLoader.get_words_from_license(f)
            self._merge_frequency_dicts(words_frequencies, words)

            for word in words.keys():
                words_occurrences[word].add(license)

            licenses.append(license)

        keywords = dict((w, words_occurrences[w]) for w \
                in self._select_keywords(words_frequencies, words_occurrences))

        return licenses, keywords

    def _merge_frequency_dicts(self, master, slave):
        # Expecting master to be an instance of defaultdict
        for keyword in slave.keys():
            master[keyword] += slave[keyword]

    def _select_keywords(self, frequency, occurrences):
        ordered = reversed(sorted(occurrences.keys(), key=lambda t: \
                    helper.search_score(len(occurrences[t]), frequency[t])))
        # Constructing a set of words covering the whole license set
        covered = set()
        results = list()
        for word in ordered:
            #print(word, helper.search_score(len(occurrences[word]), frequency[word]))
            if word in ['name', 'public']: continue # Optimization
            newly_covered = occurrences[word]
            if len(covered.union(newly_covered)) > len(covered):
                covered |= newly_covered
                results.append(word)
        return results


class SingleLicenseLoader:

    @classmethod
    def get_words_from_license(cls, filename):
        '''Get a dictionary of words and their frequencies from a license.
        Proper format: { 'word': frequency }
        :param filename: Path to the license file
        '''
        words = defaultdict(lambda: 0)
        with open(filename, 'r') as license:
            for line in license:
                for token in helper.tokenize(line):
                    if re.match(r'[a-z]+', token) and len(token) > 3:
                        words[token] += 1
        return words
