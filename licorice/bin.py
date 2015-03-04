
import operator
import os
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
    f = model.LargeFile(path)

    index = 0
    prev_chunk = ''
    positions = dict()
    lic_results = dict()
    while True:
        print('chunk read')
        chunk = f.handle.read(2*lookahead)
        if not chunk:
            break

        sanitized = helper.sanitize(chunk).split()

        # Find keyword position in sanitized chunk
        for word in sanitized:
            index += 1
            if word in keywords:
                current_licences = licences
                results = dict()
                for a in (2,4,10):
                    cmp_file = ' '.join(helper.get_chunk_from_list(sanitized, index, 2*a))
                    for lic in current_licences:
                        max_ratio = 0
                        for ch in lic.chunks(word, a):
                            ratio = fuzz.partial_ratio(ch, cmp_file)
                            if ratio > max_ratio:
                                max_ratio = ratio
                        results[lic] = max_ratio
                    current_licences = [l for l,v in results.items() if v > 70]
                for l in current_licences:
                    lic_results[l] = results[l]

    print('\n'.join(['{name} - {score}'.format(name=l.name, score=v) for (l,v) in lic_results.items() if v > 70]))




def main():
    '''
    Main function
    '''
    licences = load_licences()
    logger.info('Loaded {n} licences'.format(n=len(licences)))

    keywords = find_keywords(licences)
    logger.info('Keywords: {list}'.format(list=', '.join(keywords)))

    assign_keyword_positions(keywords, licences)

    print(get_longest_licence(licences))
    analyze_file(sys.argv[1], keywords, licences, get_longest_licence(licences))
