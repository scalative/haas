# Copyright 2013-2014 Simon Jagoe
import os

from setuptools import setup


VERSION = u'0.0.1dev1'


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


setup(
    name='haas',
    version=VERSION,
    url='https://github.com/sjagoe/haas',
    author='Simon Jagoe',
    author_email='simon@simonjagoe.com',
    description='Extensible Python Test Runner',
    packages=['haas'],
)
