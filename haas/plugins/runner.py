# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from .i_runner_plugin import IRunnerPlugin
import warnings


class _WritelnDecorator(object):
    """Used to decorate file-like objects with a handy 'writeln' method"""
    def __init__(self, stream):
        self.stream = stream

    def __getattr__(self, attr):
        if attr in ('stream', '__getstate__'):
            raise AttributeError(attr)
        return getattr(self.stream, attr)

    def writeln(self, arg=None):
        if arg:
            self.write(arg)
        self.write('\n')  # text-mode streams translate to \r\n if needed


class BaseTestRunner(IRunnerPlugin):
    """A test runner class that does not print any output itself.

    """

    def __init__(self, warnings=None):
        self.warnings = warnings

    @classmethod
    def from_args(cls, args, arg_prefix):
        return cls()

    @classmethod
    def add_parser_arguments(self, parser, option_prefix, dest_prefix):
        pass

    def run(self, result_collector, test):
        """Run the given test case or test suite.

        """
        with warnings.catch_warnings():
            if self.warnings:
                # if self.warnings is set, use it to filter all the warnings
                warnings.simplefilter(self.warnings)
                # if the filter is 'default' or 'always', special-case the
                # warnings from the deprecated unittest methods to show them
                # no more than once per module, because they can be fairly
                # noisy.  The -Wd and -Wa flags can be used to bypass this
                # only when self.warnings is None.
                if self.warnings in ['default', 'always']:
                    warnings.filterwarnings(
                        'module',
                        category=DeprecationWarning,
                        message='Please use assert\w+ instead.')
            startTestRun = getattr(result_collector, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()
            try:
                test(result_collector)
            finally:
                stopTestRun = getattr(result_collector, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()

        return result_collector
