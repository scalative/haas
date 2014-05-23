# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
import os
import sys

from setuptools import setup


VERSION = '0.2.3'


def write_version_py(filename=None):
    if filename is None:
        filename = os.path.join(os.path.dirname(__file__),
                                'haas', 'version.py')
    ver = """\
version = {version!r}
"""
    fh = open(filename, 'w')
    try:
        fh.write(ver.format(version=VERSION))
    finally:
        fh.close()


write_version_py()


with open('README.rst') as fh:
    long_description = fh.read()


if sys.version_info < (2, 7):
    setup_kwargs = {
        'install_requires': ['unittest2', 'argparse'],
    }
else:
    setup_kwargs = {}


setup(
    name='haas',
    version=VERSION,
    url='https://github.com/sjagoe/haas',
    author='Simon Jagoe',
    author_email='simon@simonjagoe.com',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Software Development :: Testing',
    ],
    description='Extensible Python Test Runner',
    long_description=long_description,
    license='BSD',
    packages=['haas'],
    entry_points={
        'console_scripts': [
            'haas=haas.main:main',
        ],
    },
    **setup_kwargs
)
