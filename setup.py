# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
import os

from setuptools import setup


VERSION = u'0.2.1.dev'


def write_version_py(filename=None):
    if filename is None:
        filename = os.path.join(os.path.dirname(__file__),
                                'haas', 'version.py')
    ver = u"""\
version = '{version}'
"""
    fh = open(filename, 'wb')
    try:
        fh.write(ver.format(version=VERSION).encode('utf-8'))
    finally:
        fh.close()


write_version_py()


with open('README.rst') as fh:
    long_description = fh.read()


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
)
