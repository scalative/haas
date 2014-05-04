# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

import argparse
import os

import haas
from .discoverer import Discoverer
from .loader import Loader
from .plugin_context import PluginContext
from .plugin_manager import PluginError, PluginManager
from .result import TextTestResult
from .testing import unittest
from .utils import configure_logging


def create_argument_parser():
    """Creates the argument parser for haas.

    """
    parser = argparse.ArgumentParser(prog='haas')
    parser.add_argument('--version', action='version',
                        version='%(prog)s {0}'.format(haas.__version__))
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('-v', '--verbose', action='store_const', default=1,
                           dest='verbosity', const=2, help='Verbose output')
    verbosity.add_argument('-q', '--quiet', action='store_const', const=0,
                           dest='verbosity', help='Quiet output')
    parser.add_argument('-f', '--failfast', action='store_true', default=False,
                        help='Stop on first fail or error')
    parser.add_argument('-c', '--catch', dest='catch_interrupt',
                        action='store_true', default=False,
                        help=('(Ignored) Catch ctrl-C and display results so '
                              'far'))
    parser.add_argument('-b', '--buffer', action='store_true', default=False,
                        help='Buffer stdout and stderr during tests')
    parser.add_argument(
        'start', nargs='*', default=[os.getcwd()],
        help=('One or more directories or dotted package/module names from '
              'which to start searching for tests'))
    parser.add_argument('-p', '--pattern', default='test*.py',
                        help="Pattern to match tests ('test*.py' default)")
    parser.add_argument('-t', '--top-level-directory', default=None,
                        help=('Top level directory of project (defaults to '
                              'start directory)'))
    parser.add_argument('--environment-manager',
                        help='Class to use as the environment manager')
    parser.add_argument('--log-level', default=None,
                        choices=['critical', 'fatal', 'error', 'warning',
                                 'info', 'debug'],
                        help='Log level for haas logging')
    return parser


class HaasApplication(object):

    def __init__(self, argv, **kwargs):
        super(HaasApplication, self).__init__(**kwargs)
        self.argv = argv
        self.parser = create_argument_parser()
        self.args, self.unparsed_args = self.parser.parse_known_args(argv[1:])
        if self.args.log_level is not None:
            configure_logging(self.args.log_level)
        self.plugin_manager = PluginManager()

    def run(self):
        args = self.args
        try:
            environment_plugin = self.plugin_manager.load_plugin(
                args.environment_manager)
        except PluginError as e:
            self.parser.exit(2, 'haas: error: {0}\n'.format(e))
        with PluginContext([environment_plugin]):
            loader = Loader()
            discoverer = Discoverer(loader)
            suites = [
                discoverer.discover(
                    start=start,
                    top_level_directory=args.top_level_directory,
                    pattern=args.pattern,
                )
                for start in args.start
            ]
            if len(suites) == 1:
                suite = suites[0]
            else:
                suite = loader.create_suite(suites)
            test_count = suite.countTestCases()
            result_factory = lambda *args: TextTestResult(test_count, *args)
            runner = unittest.TextTestRunner(
                verbosity=args.verbosity,
                failfast=args.failfast,
                buffer=args.buffer,
                resultclass=result_factory,
            )
            result = runner.run(suite)
            return not result.wasSuccessful()
