
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
        if os.path.basename(path) in settings.IGNORED_FILES:
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
            for root, dirs, files in os.walk(path):
                results = get_paths([os.path.join(root, f) for f in files])
                nonexistent.extend(results['nonexistent'])
                archives.extend(results['archives'])
                ready.extend(results['ready'])
                errors.extend(results['errors'])
                ignored.extend(results['ignored'])
            continue

        # Block specials, devices, named pipes etc.
        else:
            errors.append(path)
            continue

    return {'ready': ready, 'nonexistent': nonexistent, 'archives': archives, 'errors': errors, 'ignored': ignored}

