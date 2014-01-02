#!/usr/bin/env python3

from setuptools import setup

setup(
    name = 'licorice',
    version = '0.1.0',
    description = 'Licensing scanner and analyser',
    long_description = '''Licorice helps you determine the licensing situation
    of computer code, and try to pinpoint certain issues if found. This program
    is not legal advice, no guarantees provided.''',
    keywords = 'develop,licensing,legal',
    author = 'Tomas Radej',
    author_email = 'tradej@redhat.com',
    url = 'https://github.com/tradej/licorice',
    license = 'GPLv3',
    packages = ['licorice'],
    include_package_data = True,
    entry_points = {'console_scripts':['licorice=licorice.bin:run']},
    install_requires=['simplejson'],
    setup_requires = [],
    classifiers = [ 'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python',
                   'Topic :: Software Development',
                  ],
)
