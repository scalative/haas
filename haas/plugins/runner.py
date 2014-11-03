# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from .i_runner_plugin import IRunnerPlugin
import sys
import time
import warnings

from ..testing import unittest


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
    resultclass = unittest.TestResult

    def __init__(self, failfast=False, resultclass=None, warnings=None):
        self.failfast = failfast
        self.warnings = warnings
        if resultclass is not None:
            self.resultclass = resultclass

    @classmethod
    def from_args(cls, args, arg_prefix):
        return cls(
            failfast=args.failfast,
        )

    @classmethod
    def add_parser_arguments(self, parser, option_prefix, dest_prefix):
        pass

    def _makeResult(self):
        result = self.resultclass()
        unittest.registerResult(result)
        return result

    def _run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
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
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()
            try:
                test(result)
            finally:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()

        return result

    def run(self, test):
        return self._run(test)


class TextTestRunner(BaseTestRunner):
    """A test runner class that displays results in textual form.

    It prints out the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.
    """
    resultclass = unittest.TextTestResult

    def __init__(self, stream=None, descriptions=True, verbosity=1,
                 failfast=False, buffer=False, resultclass=None,
                 warnings=None):
        super(TextTestRunner, self).__init__(
            failfast=failfast, resultclass=resultclass, warnings=warnings)
        if stream is None:
            stream = sys.stderr
        self.stream = _WritelnDecorator(stream)
        self.descriptions = descriptions
        self.verbosity = verbosity
        self.buffer = buffer

    @classmethod
    def from_args(cls, args, arg_prefix):
        return cls(
            verbosity=args.verbosity,
            failfast=args.failfast,
            buffer=args.buffer,
        )

    def _makeResult(self):
        result = self.resultclass(
            self.stream, self.descriptions, self.verbosity)
        result.failfast = self.failfast
        result.buffer = self.buffer
        return result

    def run(self, test):
        return self._run(test)
