
import os, sys

from licorice import helper, loaders, logger, parser, problems, java

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
    logger.debug([f.short_name for f in parser.licenses])
    return parser

### GET PROJECT ###

def get_project(paths):
    if not paths:
        logger.error("You must specify files to be analysed")
        sys.exit(1)
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

def get_projects_licenses(args, parser, filelist):
    licenses_found = set()
    queried_online = dict()
    for f in filelist:
        if f.is_archive: continue
        try:
            logger.info("Processing {}".format(f.path))
            f.licenses = parser.get_licenses(f.path)
        except UnicodeDecodeError:
            f.error_reading = True
            logger.error("Error reading {}".format(f.path))
        licenses_found |= set(f.licenses)

    # Adding licenses to archives
    for f in [f for f in filelist if f.is_archive]:
        f.licenses = set()
        for licenses in [g.licenses for g in filelist if g.path.startswith(f.path)]:
            f.licenses |= set(licenses)

    return licenses_found


def detect_problems(project):
    logger.debug('Detecting problems...')
    problems.ProblemAnalyzer(project).detect()


def display_results(args, project):
    # Display results
    splitter = [', ', ' '][int(args.fedora_naming)]
    if args.list_files:
        for pfile in project.files:
            if not pfile.licenses:
                if not args.skip_unknown:
                    print('{}: UNKNOWN'.format(pfile.path))
            elif args.one_line:
                for lic in sorted(pfile.licenses, key=lambda l: l.name):
                   print('{}: {}'.format(pfile.path, lic.name))
            else:
                print('{}:'.format(pfile.path),
                        splitter.join(sorted(lic.name for lic in pfile.licenses)))
    print(splitter.join(sorted(lic.name for lic in project.licenses)))

<<<<<<< HEAD
    if project.online_result:
        print('\nInformation obtained online:')
        for query in project.online_result:
            print('{}: {} ({} upvotes / {} downvotes)'.format(query.filename,
                ', '.join(query.licenses), query.upvotes, query.downvotes))

def process_java_project(project):
    pass

def upload_archive_data(project):
#    uploader = online.Uploader()
#    for f in [f in project.files if f.is_archive]:
#        uploader.upload(f)
    pass
=======
>>>>>>> Merged changes in code from final thesis version
