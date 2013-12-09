
import logging

LOGGER = logging.getLogger('licorice')
LOGGER.addHandler(logging.StreamHandler()) # TODO: Optional console handling

def print_splash():
    LOGGER.info("*** LICORICE pre-release version ***")
    LOGGER.info("Copyright 2013 Tomas Radej, Red Hat Inc.")
    LOGGER.info('')

def info(text):
    LOGGER.info(text)

def debug(text):
    LOGGER.debug(text)

def error(text):
    LOGGER.error(text)

def set_logfile(f):
    if f: LOGGER.addHandler(logging.FileHandler(f))

