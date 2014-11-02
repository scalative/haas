# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from datetime import datetime
from enum import Enum
import time
import traceback

from .testing import unittest

STDOUT_LINE = '\nStdout:\n%s'
STDERR_LINE = '\nStderr:\n%s'


def _is_relevant_tb_level(self, tb):
    return '__unittest' in tb.tb_frame.f_globals


def _count_relevant_tb_levels(self, tb):
    length = 0
    while tb and not _is_relevant_tb_level(tb):
        length += 1
        tb = tb.tb_next
    return length


def _format_exception(err, is_failure, stdout=None, stderr=None):
    """Converts a sys.exc_info()-style tuple of values into a string."""
    exctype, value, tb = err
    # Skip test runner traceback levels
    while tb and _is_relevant_tb_level(tb):
        tb = tb.tb_next

    if is_failure:
        # Skip assert*() traceback levels
        length = _count_relevant_tb_levels(tb)
        msgLines = traceback.format_exception(exctype, value, tb, length)
    else:
        msgLines = traceback.format_exception(exctype, value, tb)

    if stdout:
        if not stdout.endswith('\n'):
            stdout += '\n'
        msgLines.append(STDOUT_LINE % stdout)
    if stderr:
        if not stderr.endswith('\n'):
            stderr += '\n'
        msgLines.append(STDERR_LINE % stderr)
    return ''.join(msgLines)


class TestCompletionStatus(Enum):
    success = 1
    failure = 2
    error = 3
    unexpected_success = 4
    expected_failure = 5
    skipped = 6


_successful_results = set([TestCompletionStatus.success,
                           TestCompletionStatus.expected_failure,
                           TestCompletionStatus.skipped])


class TestResult(object):

    def __init__(self, test_class, test_method_name, status,  # started_time,
                 completed_time, exception=None, message=None):
        self.test_class = test_class
        self.test_method_name = test_method_name
        self.status = status
        self.exception = exception
        self.message = message
        # self.started_time = started_time
        self.completed_time = completed_time

    @classmethod
    def from_test_case(cls, test_case, status,  # started_time,
                       exception=None,
                       message=None, stdout=None, stderr=None):
        test_class = type(test_case)
        test_method_name = test_case._testMethodName
        if exception is not None:
            is_failure = exception is test_case.failureException
            exception = _format_exception(
                exception, is_failure, stdout, stderr)
        completed_time = datetime.utcnow()
        return cls(test_class, test_method_name, status,  # started_time,
                   completed_time, exception, message)

    def __repr__(self):
        return '<{0} class={1}, method={2}>'.format(
            type(self).__name__, self.test_class.__name__,
            self.test_method_name)

    def to_dict(self):
        return {
            'test_class': self.test_class,
            'test_method_name': self.test_method_name,
            'status': self.status,
            'exception': self.exception,
            'message': self.message,
            # 'started_time': self.started_time,
            'completed_time': self.completed_time,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class ResultCollecter(object):

    def __init__(self, buffer=False):
        self.buffer = buffer
        self._handlers = []
        self.tests_run = 0
        self._test_results = []
        self._successful = True

    def add_result_handler(self, handler):
        self._handlers.append(handler)

    def startTest(self):
        self.tests_run += 1

    def stopTest(self):
        pass

    def startTestRun(self):
        pass

    def stopTestRun(self):
        pass

    def _handle_result(self, test, status, exception=None, message=None):
        result = TestResult.from_test_case(
            test,
            status,
            exception=exception,
            message=message,
        )
        for handler in self._handlers:
            handler(result)
        if self._successful and result.status not in _successful_results:
            self._successful = False
        self._test_results.append(result)

    def addError(self, test, exception):
        self._handle_result(
            test, TestCompletionStatus.error, exception=exception)

    def addFailure(self, test, exception):
        self._handle_result(
            test, TestCompletionStatus.failure, exception=exception)

    def addSuccess(self, test):
        self._handle_result(test, TestCompletionStatus.success)

    def addSkip(self, test, reason):
        self._handle_result(
            test, TestCompletionStatus.skipped, message=reason)

    def addExpectedFailure(self, test, exception):
        self._handle_result(
            test, TestCompletionStatus.expected_failure, exception=exception)

    def addUnexpectedSuccess(self, test):
        self._handle_result(test, TestCompletionStatus.unexpected_success)

    def wasSuccessful(self):
        return self._successful

    def stop(self):
        pass


class TextTestResult(unittest.TextTestResult):
    """A simple extension to ``unittest.TextTestResult`` that displays
    progression of testing when run in verbose mode.

    """

    def __init__(self, total_tests, stream, descriptions, verbosity):
        """Create a TextTestResult. The parameters ``stream``, ``descriptions``
        and ``verbosity`` are as in ``unittest.TextTestResult``.

        Parameters
        ----------
        total_tests : int
            The total number of tests in the suite to be run, as
            returned by ``Suite.countTestCases()``

        """
        self._total_tests = total_tests
        super(TextTestResult, self).__init__(stream, descriptions, verbosity)

    def startTest(self, test):
        if self.showAll:
            padding = len(str(self._total_tests))
            prefix = '[{timestamp}] ({run: >{padding}d}/{total:d}) '.format(
                timestamp=time.ctime(),
                run=self.testsRun + 1,
                padding=padding,
                total=self._total_tests,
            )
            self.stream.write(prefix)
        super(TextTestResult, self).startTest(test)

    startTest.__doc__ = unittest.TextTestResult.startTest.__doc__
