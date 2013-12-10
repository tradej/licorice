#!/usr/bin/env python3

import os
import sys

from licorice import get_datadir, argument, helper, logger, workflow, config


### ENTRY POINT ###
def run():
    args = argument.construct_argparser().parse_args() # Parse arguments
    argument.handle_args(args)

    logger.print_splash() # Header output

    parser = workflow.get_license_parser(get_datadir(config.DEFINITIONS_DIR))
    project = workflow.get_project(args.file_list)

    project.licenses = workflow.get_projects_licenses(parser, project.files)

    workflow.display_results(args, project)

### MAIN ###
if __name__ == '__main__':
    run()
