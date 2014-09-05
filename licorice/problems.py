
import re
from inspect import ismethod

from licorice import logger

class ProblemAnalyzer:
    '''
    Checks for problems:
    * Binary files found
    * Non-free license found
    * Unknown license found
    '''

    def __init__(self, project):
        self.project = project

    def _get_main_licenses(self):
        names = map(re.compile, ['licen[cs]e', 'copyright', 'copying'])
        results = set()
        for f in self.project.files:
            for n in names:
                if n.search(f.filename.lower()) and f.licenses:
                    results |= set(f.licenses)
        return results

    def problem_multiple_licenses_found(self):
        return (len(self.project.licenses) > 1, 'Found more than 1 license: {}'.format(\
                ', '.join([l.name for l in self.project.licenses])))

    def problem_files_with_errors(self):
        errors = [f.error_reading for f in self.project.files if f.error_reading]
        return (bool(len(errors)), 'Found {} files that could not be read'.format(len(errors)))

    def problem_files_with_errors(self):
        errors = [f.error_unpacking for f in self.project.files if f.error_unpacking]
        return (bool(len(errors)), 'Found {} archives that could not be unpacked'.format(len(errors)))

    def problem_no_main_license_file(self):
        return (not bool(self._get_main_licenses()), 'No main license file found')

    def problem_no_licensing_information_found(self):
        return (not self.project.licenses, 'No licensing information found')

    def problem_different_licenses_from_main_found(self):
        main_licenses = self._get_main_licenses()
        diff = self.project.licenses.difference(main_licenses)
        return (bool(diff and bool(main_licenses)), 'Found licenses different from the main license: {}'.format(\
                ', '.join([l.name for l in diff])))

    def problem_multiple_copyleft_licenses_found(self):
        copyleft_found = False
        for lic1 in self.project.licenses:
            if lic1.restrictions['copyleft']:
                if not copyleft_found: copyleft_found = True
                else: return (True, 'Multiple copyleft licenses found')
        return (False, None)

    def problem_non_copyleft_main_license(self):
        main_licenses = self._get_main_licenses()
        if False in [f.restrictions['copyleft'] for f in main_licenses]:
            if True in [l.restrictions['copyleft'] for l in self.project.licenses]:
                return (True, 'Copyleft license found, but main license is non-copyleft. Please check if relicensing is necessary')
        return (False, None)

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
                (result, comment) = attribute()
                if result: results.append(comment)

        logger.debug('Detected {} problems'.format(len(results)))
        if len(results) > 0: print('* Found problems: *')
        else: print('* No problems found. *')

        for comment in results: print(' - ', comment)



