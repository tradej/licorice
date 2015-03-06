
import mmap
import operator
import os
import re
import sys

from collections import defaultdict
from fuzzywuzzy import fuzz
from licorice import args, exceptions, helper, loader, matcher, model, settings
from licorice.logging import logger

def load_licences(path=settings.LICENSE_TEXTS_PATH):
    '''
    Load all licenses on the given path (sane defaults).
    '''
    licences = []
    for f in os.listdir(path):
        name = os.path.basename(f).replace('.txt', '')
        licences.append(model.License(name, os.path.join(path, f)))

    return licences


def find_keywords(licences, rejects=settings.REJECTED_WORDS):
    '''
    Find keywords that occur in all licenses with greatest frequency

    licences: list of Licence instances
    rejects: list of words that are to be excluded from the result

    returns: list of keywords
    '''
    # Load words
    dicts = dict()
    for licence in licences:
        dicts[licence] = helper.get_word_frequencies(licence.contents)

    # Assign frequencies
    used_in_files = defaultdict(lambda: set())
    used_times = defaultdict(lambda: 0)
    for license, dictionary in dicts.items():
        for word in dictionary:
            used_in_files[word].add(license)
            used_times[word] += dictionary[word]

    # Assign scores to words
    score = dict()
    for word in used_in_files.keys():
        score[word] = len(used_in_files[word]) ** 2 / used_times[word]

    scores_sorted = sorted(score.items(), key=operator.itemgetter(1), reverse=True)

    # Select best words based on scores until all licences are covered
    covered = set()
    keywords = list()
    for word, score in scores_sorted:
        if word in rejects or len(word) < 3:
            continue # Undesirable words
        if covered == licences:
            break # We're finished
        if covered | used_in_files[word] > covered:
            covered |= used_in_files[word]
            keywords.append(word)

    return keywords

def assign_keyword_positions(keywords, licences):
    for licence in licences:
        for keyword in keywords:
            for index in range(0, len(licence.splitcontents)): # sic!
                if licence.splitcontents[index] == keyword:
                    licence.keyword_positions[keyword].append(index)

def load_files(file_list):
    return [model.MappedFile(path) for path in loader.get_paths(file_list)['ready']]

def main():
    '''
    Main function
    '''
    argdict = args.get_arg_parser().parse_args()
    args.process_args(argdict)

    licences = load_licences()
    logger.debug('Loaded {n} licences'.format(n=len(licences)))

    keywords = find_keywords(licences)
    logger.debug('Keywords: {list}'.format(list=', '.join(keywords)))

    projectfiles = sorted(load_files(argdict.file_list), key=lambda x: x.path)
    logger.info('Loaded {n} files'.format(n=len(projectfiles)))

    licencematcher = matcher.LicenceMatcher(licences, keywords)

    for pf in projectfiles:
        try:
            pf.open()
            logger.debug('Processing {path} ({len} bytes)'.format(path=pf.path, len=pf.length))
            found_licences = licencematcher.get_licences(pf)
        except exceptions.RunTimeException as e:
            logger.error(str(e))
        finally:
            pf.close()
        if found_licences:
            formatted_licences = ['{l} ({s}%)'.format(l=lic.name, s=score) for lic, score in found_licences.items()]
        else:
            formatted_licences = ['unknown']

        if argdict.skip_unknown and not found_licences:
            continue

        print('{path}: {licences}'.format(path=pf.path, licences=' '.join(formatted_licences)))
