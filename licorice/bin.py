#!/usr/bin/env python3

import os
import sys

from licorice import get_dir, argument, helper, logger, workflow, config


### ENTRY POINT ###
def run():
    # Parse arguments
    args = argument.construct_argparser().parse_args()
    argument.handle_args(args)

    # Header output
    logger.print_splash()

    # Main work
    parser = workflow.get_license_parser(get_dir(config.DEFINITIONS_DIR), vague=args.vague)
    project = workflow.get_project(args.file_list)

    project.licenses = workflow.get_projects_licenses(args, parser, project.files)
    logger.info('Found licenses: {}'.format(', '.join([l.name for l in project.licenses])))

    # Display results
    workflow.display_results(args, project)

    # Detect licensing problems
    if args.detect_problems:
        workflow.detect_problems(project)

### MAIN ###
if __name__ == '__main__':
    run()
