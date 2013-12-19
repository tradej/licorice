
import os, sys

from licorice import logger
from licorice import helper
from licorice import parser
from licorice import loaders

### GET LICENSE PARSER ###

def get_license_parser(path, vague):
    logger.info("Loading license definitions:")
    parser = None
    try:
        parser = loaders.MainLicenseLoader().get_license_parser(vague)
        logger.debug('Keywords selected: {}'.format(' '.join(parser.file_locations.keys())))
    except OSError as e:
        logger.error("Loading licenses failed with this error: {0}".format(str(e)))
        sys.exit(1)
    return parser

### GET PROJECT ###

def get_project(paths):
    project = None
    try:
        logger.info("Loading project")
        if isinstance(paths, str): paths = [paths]
        project = loaders.ProjectLoader.load_project(list(map(helper.path, paths)))
        logger.info("Loading complete, {0} files loaded.".format(len(project.files)))
        return project
    except Exception as e:
        logger.error("Loading project failed with this error: {0}".format(str(e)))
        sys.exit(1)

def get_projects_licenses(parser, filelist):
    licenses_found = set()
    for f in filelist:
        logger.info("Processing {}".format(f.path))
        try:
            f.licenses = parser.get_licenses(f.path)
        except UnicodeDecodeError:
            logger.error("Error reading {}".format(f.path))
        licenses_found |= set(f.licenses)
    return licenses_found

def display_results(args, project):
    # Display results
    if args.list_files:
        for pfile in project.files:
            if not pfile.licenses:
                if not args.skip_unknown:
                    print('{}: UNKNOWN'.format(pfile.path))
            elif args.one_line:
                for lic in pfile.licenses:
                   print('{}: {}'.format(pfile.path, lic.name))
            else:
                print('{}:'.format(pfile.path),
                    ' '.join(lic.name for lic in pfile.licenses))
    print(' '.join(sorted(x.name for x in project.licenses)))
