
import configparser
import os
import re
import itertools
import subprocess
from collections import defaultdict

from licorice import config, helper, get_dir, logger
from licorice.models import FileInProject, Project, License
from licorice.parser import LicenseParser

class ProjectLoader:
    @classmethod
    def load_project(cls, destinations):
        '''Load contents of a software project - file, directory, archive
        :param path: Path where the project is to be found
        '''
        filelist = set()
        logger.debug('Loading {} files for analysis:'.format(len(destinations)))
        for path in destinations:
            logger.debug('Loading {}'.format(path))
            if os.path.isdir(path):
                filelist |= cls.load_directory(path)
            elif cls.is_archive(path):
                filelist |= cls.load_archive(path)
            elif os.path.isfile(path):
                filelist.add(cls.load_file(path))
            else:
                raise Exception('File does not exist or format not supported: {}'.format(path))

        return Project(os.path.basename(destinations[0]), sorted(filelist,
            key=lambda x: x.path))

    @classmethod
    def load_directory(cls, path):
        '''Get files from a directory recursively
        :param path: Path to the directory
        '''
        filelist = set()
        if not os.path.isdir(path):
            raise IOError("{} is not a directory!".format(path))
        for filename in helper.get_files(path):
            logger.debug('Loading {}'.format(filename))
            if os.path.isdir(filename):
                filelist |= cls.load_directory(filename)
            elif cls.is_archive(filename):
                filelist |= cls.load_archive(filename)
            elif os.path.isfile(filename):
                filelist.add(cls.load_file(filename))
            else:
                logger.error('File does not exist or format not supported: {}'.format(filename))
        return filelist

    @classmethod
    def load_file(cls, filename):
        '''Get a file
        :param filename: Full and expanded path to file
        '''
        if not os.path.isfile(filename):
            raise IOError("{} is not a file!".format(filename))
        return FileInProject(filename)

    @classmethod
    def load_archive(cls, path, tmpdir=''):
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
        try:
            subprocess.call({
                '.bz2' : ["tar", "xjf", path],
                '.gz'  : ["tar", "xzf", path],
                '.xz'  : ["tar", "xJf", path],
                '.jar' : ["jar", "xf", path],
                '.tar' : ["tar", "xf", path],
                '.rar' : ["unrar", "e", path],
                '.war' : ["jar", "xf", path],
                '.zip' : ["unzip", '', path],
            }[os.path.splitext(path)[1]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except:
            result = FileInProject(path)
            result.error_unpacking = True
            os.chdir(working_directory)
            return set([result])

        os.chdir(working_directory)
        result = cls.load_directory(path + '-unpacked')
        result.add(cls.load_file(path))
        return result

    @staticmethod
    def is_archive(path):
        return os.path.splitext(path)[1] in config.ARCHIVE_EXT

class MainLicenseLoader:
    '''Class obtaining license definition and configuration'''

    def get_license_parser(self, vague=False):
        '''Get an instance of LicenseParser with definitions obtained from a
        preconfigured directory.
        '''
        conf_path = helper.path(get_dir(helper.prepend_cwd(config.METADATA_DIR)))
        text_path = helper.path(get_dir(helper.prepend_cwd(config.DEFINITIONS_DIR)))

        (licenses, keywords) = self.get_all_licenses_and_keywords(conf_path, text_path)
        logger.info('Loaded {} licenses'.format(len(licenses)))
        return LicenseParser(keywords, licenses, vague)

    def get_all_licenses_and_keywords(self, conf_path, text_path):
        '''Get a list of licenses and keywords to be searched.
        keywords is a dictionary in form { 'keyword' : [ its locations ] }.

        Both licenses with metadata and without metadata are loaded.
        '''
        words_occurrences = defaultdict(lambda: set())
        words_frequencies = defaultdict(lambda: 0)
        licenses = self._load_licenses_from_configs(helper.get_files(conf_path))
        unconfigured_licenses = list( \
                set(helper.get_files(text_path)).difference(\
                set(itertools.chain(*[license.files for license in licenses]))))
        licenses += self._load_licenses_from_texts(unconfigured_licenses)

        for lic in licenses:
            for f in lic.cachedfiles:
                words = SingleLicenseLoader.get_words_from_license(f)
                self._merge_frequency_dicts(words_frequencies, words)
                for word in words.keys():
                    words_occurrences[word].add(f)


        keywords = dict((w, words_occurrences[w]) for w \
                in self._select_keywords(words_frequencies, words_occurrences))

        return licenses, keywords

    def _load_licenses_from_configs(self, filenames):
        '''Load licenses from metadata files specified by filenames'''
        result = list()
        for f in filenames:
            result.append(LicenseMetadataLoader.load_license(f))
        return result

    def _load_licenses_from_texts(self, filenames):
        '''Load license texts from files specified by filenames'''
        result = list()
        for f in filenames:
            result.append(LicenseTextLoader.load_license(f))
        return result


    def _merge_frequency_dicts(self, master, slave):
        # Expecting master to be an instance of defaultdict
        for keyword in slave.keys():
            master[keyword] += slave[keyword]

    def _select_keywords(self, frequency, occurrences):
        '''Select keywords based on license texts contents'''
        ordered = reversed(sorted(occurrences.keys(), key=lambda t: \
                    helper.search_score(len(occurrences[t]), frequency[t])))
        # Constructing a set of words covering the whole license set
        covered = set()
        results = list()
        for word in ordered:
            if word in ['name', 'public']: continue # Optimization
            newly_covered = occurrences[word]
            if len(covered.union(newly_covered)) > len(covered):
                covered |= newly_covered
                results.append(word)
        return results


class SingleLicenseLoader:

    @classmethod
    def get_words_from_license(cls, cachedfile):
        '''Get a dictionary of words and their frequencies from a license.
        Proper format: { 'word': frequency }
        '''
        words = defaultdict(lambda: 0)
        for word in cachedfile.iterator(0):
            if re.match(r'[a-z]+', word) and len(word) > 3:
                words[word] += 1
        return words

class LicenseMetadataLoader:
    '''Class loading metadata from a license file'''

    @classmethod
    def load_license(cls, path):
        cfp = configparser.ConfigParser()
        cfp.read_file(open(helper.path(path)))
        return License(
                cfp.get('Metadata', 'name'),\
                True,\
                cls._format_files(cfp.get('Metadata', 'files')),\
                cfp.get('Metadata', 'vague_words').split(' '),\
                cls._get_section(cfp, 'Freedoms'),\
                cls._get_section(cfp, 'Obligations'),\
                cls._get_section(cfp, 'Restrictions'),\
                cls._get_section(cfp, 'Compatibility'),\
                cfp.get('Metadata', 'short_name'))

    @classmethod
    def _get_section(cls, parser, section_name):
        result = dict()
        if parser.has_section(section_name):
            for (item, value) in parser.items(section_name):
                result[item] = cls._parse_value(value)
        return result

    @classmethod
    def _parse_value(cls, value):
        if   value == 'y': return True
        elif value == 'n': return False
        elif value == '':  return None
        else:              return value

    @classmethod
    def _format_files(cls, files):
        prefix = get_dir(config.DEFINITIONS_DIR)
        return [helper.path(os.path.join(prefix, f + '.txt')) \
                for f in files.split(' ')]


class LicenseTextLoader:

    @classmethod
    def load_license(cls, path):
        name = os.path.splitext(os.path.basename(path))[0]
        if name[0].islower():
            name = name.title()
        return License(name, False, [path])
