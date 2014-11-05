# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

import logging
import os
import sys
import re

import six

import haas


LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'fatal': logging.FATAL,
    'critical': logging.CRITICAL,
}


def configure_logging(level):
    actual_level = LEVELS.get(level, logging.WARNING)
    format_ = '%(asctime)s %(levelname)-8.8s [%(name)s:%(lineno)s] %(message)s'
    formatter = logging.Formatter(format_)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(actual_level)
    logger = logging.getLogger(haas.__name__)
    logger.addHandler(handler)
    logger.setLevel(actual_level)
    logger.info('Logging configured for haas at level %r',
                logging.getLevelName(actual_level))


if six.PY2:
    def get_module_by_name(name):
        """Import a module and return the imported module object.

        """
        __import__(name)
        return sys.modules[name]
else:
    import importlib
    get_module_by_name = importlib.import_module


UNCAMELCASE_FIRST_PASS = re.compile(
    r'(?P<before>.)(?P<caps>[A-Z]+)')
UNCAMELCASE_SECOND_PASS = re.compile(
    r'(?P<before>.)(?<=[A-Z])(?P<caps>[A-Z][a-z]+)')


def uncamelcase(string, sep='_'):
    replace = '\g<before>{0}\g<caps>'.format(sep)
    temp = UNCAMELCASE_FIRST_PASS.sub(replace, string)
    return UNCAMELCASE_SECOND_PASS.sub(replace, temp).lower()


class cd(object):

    def __init__(self, destdir):
        self.destdir = destdir
        self.startdir = None

    def __enter__(self):
        self.startdir = os.getcwd()
        os.chdir(self.destdir)

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.startdir)
        self.startdir = None


if sys.version_info < (3, 2):  # pragma: no cover
    # Copied from Python 3.2 abc.py
    class abstractclassmethod(classmethod):
        """A decorator indicating abstract classmethods.

        Similar to abstractmethod.

        Usage:

            class C(metaclass=ABCMeta):
                @abstractclassmethod
                def my_abstract_classmethod(cls, ...):
                    ...
        """

        __isabstractmethod__ = True

        def __init__(self, callable):
            callable.__isabstractmethod__ = True
            super(abstractclassmethod, self).__init__(callable)
else:  # pragma: no cover
    from abc import abstractclassmethod  # noqa
