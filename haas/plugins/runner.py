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
            startTime = time.time()
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()
            try:
                test(result)
            finally:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()
            stopTime = time.time()

        return result, startTime, stopTime

    def run(self, test):
        result, _, _ = self._run(test)
        return result


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
        result, startTime, stopTime = self._run(test)
        timeTaken = stopTime - startTime

        result.printErrors()
        if hasattr(result, 'separator2'):
            self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.writeln("Ran %d test%s in %.3fs" %
                            (run, run != 1 and "s" or "", timeTaken))
        self.stream.writeln()

        expectedFails = unexpectedSuccesses = skipped = 0
        try:
            results = map(len, (result.expectedFailures,
                                result.unexpectedSuccesses,
                                result.skipped))
        except AttributeError:
            pass
        else:
            expectedFails, unexpectedSuccesses, skipped = results

        infos = []
        if not result.wasSuccessful():
            self.stream.write("FAILED")
            failed, errored = len(result.failures), len(result.errors)
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
        else:
            self.stream.write("OK")
        if skipped:
            infos.append("skipped=%d" % skipped)
        if expectedFails:
            infos.append("expected failures=%d" % expectedFails)
        if unexpectedSuccesses:
            infos.append("unexpected successes=%d" % unexpectedSuccesses)
        if infos:
            self.stream.writeln(" (%s)" % (", ".join(infos),))
        else:
            self.stream.write("\n")
        return result
