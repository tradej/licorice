#!/usr/bin/env python3

import os
import sys

from licorice import get_dir, argument, helper, logger, workflow, config


### ENTRY POINT ###
def run():
    args = argument.construct_argparser().parse_args() # Parse arguments
    argument.handle_args(args)

    logger.print_splash() # Header output

    parser = workflow.get_license_parser(get_dir(config.DEFINITIONS_DIR), vague=args.vague)
    project = workflow.get_project(args.file_list)

    project.licenses, project.online_result = workflow.get_projects_licenses(args, parser, project.files)
    logger.info('Found licenses: {}'.format(', '.join([l.name for l in project.licenses])))
    workflow.display_results(args, project)

    if args.detect_problems:
        workflow.detect_problems(project)

### MAIN ###
if __name__ == '__main__':
    run()
