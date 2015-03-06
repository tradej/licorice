
import argparse
import sys
from licorice import logging

def get_arg_parser():
    arg_parser = argparse.ArgumentParser(description='''
    Licorice: The licensing information analyser and examiner
    ''')
    arg_parser.add_argument('-v', '--verbose', required=False,
                            action='store_true', help='Display extra information')
    arg_parser.add_argument('-d', '--debug', required=False,
                            action='store_true', help='Include lot of debugging info')
    arg_parser.add_argument('-u', '--skip-unknown', required=False, action='store_true',
                            help='when outputting, skip files with unknown licenses')
    arg_parser.add_argument('file_list', help='list of files to be processed', nargs='*')
#    arg_parser.add_argument('-p', '--detect-problems', required=False, action='store_true',
#                            help='attempt to detect problems with licensing')
#    arg_parser.add_argument('-l', '--log-file', required=False,
#                            default='', help='sent output to a log file')
#    arg_parser.add_argument('-f', '--list-files', required=False, action='store_true',
#                            help='display licenses for each file')
    return arg_parser


def process_args(argdict):
    if argdict.debug:
        logging.set_debug()
