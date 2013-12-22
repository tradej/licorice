
import re
from inspect import ismethod

from licorice import logger

class ProblemAnalyzer:
    '''
    Checks for problems:
    * Binary files found
    * No main license file found (applicable to archives and directories)
    * No licensing information found
    * Multiple licenses found
    * Non-free license found
    * Unknown license found
    * Different licenses from main license found
    * Two copyleft licenses found
    * Main licenses is non-copyleft, found copyleft
    '''

    def __init__(self, project):
        self.project = project

    def _get_main_license_files(self):
        names = map(re.compile, ['licen[cs]e', 'copyright', 'copying'])
        results = set()
        for f in self.project.files:
            for n in names:
                if n.search(f.filename.lower()) and f.licenses:
                    results.add(f)
        return results

    def problem_no_main_license_file(self):
        return (not bool(self._get_main_license_files()), 'No main license file found')

    def problem_no_licensing_information_found(self):
        return (not self.project.licenses, 'No licensing information found')

#    def problem_other_licenses_from_main_found(self):
#        main_licenses = set()
#        for f in self._get_main_license_files():
#            for l in f.licenses:
#                main_licenses.add(l)
#
#        diff = main_licenses.difference(self.project.licenses)
#        return (bool(diff), 'Additional licenses to the main one found: {}'.format(', '.join(diff)))

    def problem_incompatible_licenses_found(self):
        results = list()
        for lic1 in self.project.licenses:
            for lic2 in self.project.licenses:
                if lic2.short_name in lic1.compatibility and lic1.compatibility[lic2.short_name] is False:
                    results.append('{} with {}'.format(lic1.name, lic2.name))
        return (bool(results), 'License incompatibility: {}'.format('; '.join(results)))

    def detect(self):
        results = list()
        for name in dir(self):
            attribute = getattr(self, name)
            if ismethod(attribute) and attribute.__name__.startswith('problem'):
                result, comment = attribute()
                if result: results.append(comment)

        logger.debug('Detected {} problems'.format(len(results)))
        if len(results) > 0: print('Found problems:')
        else: print('No problems found.')

        for comment in results: print('* ', comment)



