# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import unicode_literals

import argparse
import os

from .loader import Loader
from .testing import unittest


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'start', nargs='?', default=os.getcwd(),
        help=('Directory or dotted package/module name to start searching for '
              'tests'))
    return parser.parse_args(argv[1:])


def main(argv):
    args = parse_args(argv)
    loader = Loader()
    suite = loader.discover(args.start)
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    return not result.wasSuccessful()
