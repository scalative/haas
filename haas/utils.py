# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
import logging
import os
import re

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


UNCAMELCASE_FIRST_PASS = re.compile(
    r'(?P<before>.)(?P<caps>[A-Z]+)')
UNCAMELCASE_SECOND_PASS = re.compile(
    r'(?P<before>.)(?<=[A-Z])(?P<caps>[A-Z][a-z]+)')


def uncamelcase(string, sep='_'):
    replace = r'\g<before>{0}\g<caps>'.format(sep)
    temp = UNCAMELCASE_FIRST_PASS.sub(replace, string)
    return UNCAMELCASE_SECOND_PASS.sub(replace, temp).lower()


class cd:

    def __init__(self, destdir):
        self.destdir = destdir
        self.startdir = None

    def __enter__(self):
        self.startdir = os.getcwd()
        os.chdir(self.destdir)

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.startdir)
        self.startdir = None
