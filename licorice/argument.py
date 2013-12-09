
import argparse
import logging

from licorice import logger

def construct_argparser():
    arg_parser = argparse.ArgumentParser(description='''
        * LIcensing and COpyright Reviewer, Information Collector and Examiner *

        Determine licenses and licensing problems of the given file, archive
        or directory. The program supports logging and is extensible.
        Currently only general files and projects written in Java are
        supported.''')
    arg_parser.add_argument('-v', '--verbose', required=False,
                            action='store_true', help='display extra information')
    arg_parser.add_argument('-d', '--debug', required=False,
                            action='store_true', help='include lot of debugging info')
    arg_parser.add_argument('-l', '--log-file', required=False,
                            default='', help='sent output to a log file')
    arg_parser.add_argument('-f', '--list-files', required=False,
                            action='store_true', help='display licenses for each file')
    arg_parser.add_argument('-p', '--detect-problems', required=False,
                            action='store_true', help='attempt to detect problems with licensing')
    arg_parser.add_argument('-o', '--one-line', required=False,
                            action='store_true', help='print one license per line')
    arg_parser.add_argument('-u', '--skip-unknown', required=False,
                            action='store_true', help='when outputting, skip files with unknown licenses')
#    arg_parser.add_argument('-s', '--strictness', required=False,
#                            type=int, default=2, help='strictness of matching (from 1 to 3, default: 2)')
    arg_parser.add_argument('file_list', help='list of files to be processed')
    return arg_parser

def handle_args(args):
    if args.verbose:
        logger.LOGGER.setLevel(logging.INFO)
    if args.debug:
        logger.LOGGER.setLevel(logging.DEBUG)
    if args.log_file:
        logger.set_logfile(args.log_file)
        # TODO check if file is writable
