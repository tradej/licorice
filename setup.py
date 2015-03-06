#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup, find_packages

setup(
    name='licorice',
    version='1.0alpha',
    description='Tool for licensing analysis and reporting',
    long_description=''.join(open('README.rst').readlines()),
    install_requires=['fuzzywuzzy'],
    keywords='licensing, licence, development',
    author='Tomas Radej',
    author_email='tradej@redhat.com',
    license='GPLv3',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        ]
)
