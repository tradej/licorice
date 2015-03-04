
import mmap
import operator
import os
import re
import sys

from collections import defaultdict
from fuzzywuzzy import fuzz
from licorice import helper, model, settings
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


def get_longest_licence(licences):
    return max([len(l.contents) for l in licences])

def analyze_file(path, keywords, licences, lookahead):
    m = model.MappedFile(path)

    found_licences = defaultdict(lambda: 0)
    for kw in keywords:
        occurrences = m.occurrences(kw)
        for occurrence in occurrences:
            for licence in (l for l in licences if l.contains(kw)):
                match = 0
                for l_occurrence in licence.positions(kw):
                    if occurrence - l_occurrence < 0: # License's prefix is longer than file's prefix
                        continue

                    end = len(licence.contents) - l_occurrence
                    if end > m.length: # License's suffix is longer than the file's length
                        continue

                    bad = False
                    for offset in [10, 50, 300, end]:
                        if bad:
                            break
                        temp_start = max(l_occurrence - offset, 0)
                        temp_end = min(l_occurrence + offset, len(licence.contents))
#                        print('matching', licence.name, temp_start, temp_end)
                        lic_str = re.sub('[\W]+', ' ', licence.contents[temp_start:temp_end])
                        try:
                            matched_str = re.sub('[\W]+', ' ', m.get(occurrence - l_occurrence, occurrence + temp_end))
                        except UnicodeDecodeError:
                            print('Error reading {}'.format(m.path))
                            return

                        match = fuzz.token_set_ratio(lic_str, matched_str)
                        if match < 95:
                            bad = True
                            match = 0
                            continue

                    if match > found_licences[licence]:
                        found_licences[licence] = match

#                        print('matched', licence.name)
#                        print('.', end='')
#                        match = fuzz.partial_ratio(lic_str, matched_str)
#                        if match < 90:
#                            bad = True
#                            match = 0
#                            continue


    result = [(licence, value) for (licence, value) in found_licences.items() if value > 0]
    if result:
        lic_str = ' '.join(('{lic} ({res}%)'.format(lic=l.name, res=match) for (l, match) in result))
    else:
        lic_str = 'unknown'
    print('{file}: {licenses}'.format(file=m.path,
        licenses=lic_str))


def main():
    '''
    Main function
    '''
    licences = load_licences()
    logger.info('Loaded {n} licences'.format(n=len(licences)))

    keywords = find_keywords(licences)
    logger.info('Keywords: {list}'.format(list=', '.join(keywords)))

    for f in sys.argv[1:]:
        analyze_file(f, keywords, licences, get_longest_licence(licences))
