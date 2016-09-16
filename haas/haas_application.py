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
from .loader import Loader
from .plugin_context import PluginContext
from .plugin_manager import PluginManager
from .result import ResultCollector
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
    _add_log_level_option(parser)
    return parser


def _create_log_level_parser():
    parser = argparse.ArgumentParser(prog='haas', add_help=False)
    _add_log_level_option(parser)
    return parser


def _add_log_level_option(parser):
    parser.add_argument('--log-level', default=None,
                        choices=['critical', 'fatal', 'error', 'warning',
                                 'info', 'debug'],
                        help='Log level for haas logging')


class HaasApplication(object):
    """Main haas application entry-point.

    """

    def __init__(self, argv, **kwargs):
        super(HaasApplication, self).__init__(**kwargs)
        self.argv = argv

        initial_parser = _create_log_level_parser()
        initial_args, _ = initial_parser.parse_known_args(argv[1:])
        if initial_args.log_level is not None:
            configure_logging(initial_args.log_level)

        self.parser = create_argument_parser()

    def run(self, plugin_manager=None):
        """Run the haas test runner.

        This will load and configure the selected plugins, set up the
        environment and begin test discovery, loading and running.

        Parameters
        ----------
        plugin_manager : haas.plugin_manager.PluginManager
            [Optional] Override the use of the default plugin manager.

        """
        if plugin_manager is None:
            plugin_manager = PluginManager()
        plugin_manager.add_plugin_arguments(self.parser)

        args = self.parser.parse_args(self.argv[1:])

        environment_plugins = plugin_manager.get_enabled_hook_plugins(
            plugin_manager.ENVIRONMENT_HOOK, args)
        runner = plugin_manager.get_driver(
            plugin_manager.TEST_RUNNER, args)

        with PluginContext(environment_plugins):
            loader = Loader()
            discoverer = plugin_manager.get_driver(
                plugin_manager.TEST_DISCOVERY, args, loader=loader)
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
            result_handlers = plugin_manager.get_enabled_hook_plugins(
                plugin_manager.RESULT_HANDLERS, args, test_count=test_count)

            result_collector = ResultCollector(
                buffer=args.buffer, failfast=args.failfast)

            for result_handler in result_handlers:
                result_collector.add_result_handler(result_handler)

            result = runner.run(result_collector, suite)
            return not result.wasSuccessful()
