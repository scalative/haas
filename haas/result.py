# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from datetime import datetime
from enum import Enum
from functools import wraps
import sys
import traceback

from six.moves import StringIO


class TestCompletionStatus(Enum):
    """Enumeration to represent the status of a single test.

    """

    #: The test completed successfully.
    success = 1

    #: The test failed, but did not encounter an unexpected error.
    failure = 2

    #: The test encountered an unexpected error.
    error = 3

    #: A test marked as expected to fail unexpected passed.
    unexpected_success = 4

    #: A test failed as expected
    expected_failure = 5

    #: A test was skipped
    skipped = 6


_successful_results = set([TestCompletionStatus.success,
                           TestCompletionStatus.expected_failure,
                           TestCompletionStatus.skipped])

STDOUT_LINE = '\nStdout:\n%s'
STDERR_LINE = '\nStderr:\n%s'


def _is_relevant_tb_level(tb):
    return '__unittest' in tb.tb_frame.f_globals


def _count_relevant_tb_levels(tb):
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


class TestResult(object):
    """Container object for all information related to the run of a single
    test.  This contains the test itself, the actual status including
    the reason or error associated with status, along with timing
    information.

    """

    def __init__(self, test_class, test_method_name, status,  # started_time,
                 completed_time, exception=None, message=None):
        self.test_class = test_class
        self.test_method_name = test_method_name
        self.status = status
        self.exception = exception
        self.message = message
        # self.started_time = started_time
        self.completed_time = completed_time

    def __eq__(self, other):
        if not isinstance(other, TestResult):
            return NotImplemented
        return (
            self.test_class == other.test_class and
            self.test_method_name == other.test_method_name and
            self.status == other.status and
            self.exception == other.exception and
            self.message == other.message
        )

    def __ne__(self, other):
        return not (self == other)

    @classmethod
    def from_test_case(cls, test_case, status,  # started_time,
                       exception=None,
                       message=None, stdout=None, stderr=None):
        """Construct a :class:`~.TestResult` object from the test and a status.

        Parameters
        ----------
        test_case : unittest.TestCase
            The test that this result will represent.
        status : haas.result.TestCompletionStatus
            The status of the test.
        exception : tuple
            ``exc_info`` tuple ``(type, value, traceback)``.
        message : str
            Optional message associated with the result (e.g. skip
            reason).
        stdout : str
            The test stdout if stdout was buffered.
        stderr : str
            The test stderr if stderr was buffered.

        """
        test_class = type(test_case)
        test_method_name = test_case._testMethodName
        if exception is not None:
            exctype, value, tb = exception
            is_failure = exctype is test_case.failureException
            exception = _format_exception(
                exception, is_failure, stdout, stderr)
        completed_time = datetime.utcnow()
        return cls(test_class, test_method_name, status,  # started_time,
                   completed_time, exception, message)

    def __repr__(self):
        return '<{0} class={1}, method={2}, exc={3!r}>'.format(
            type(self).__name__, self.test_class.__name__,
            self.test_method_name, self.exception)

    @property
    def test(self):
        """The test case instance this result represents.

        """
        return self.test_class(self.test_method_name)

    def to_dict(self):
        """Serialize the ``TestResult`` to a dictionary.

        """
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
        """Create a ``TestResult`` from a dictionary created by
        :meth:`~.TestResult.to_dict`

        """
        return cls(**data)


# Temporary compatibility with unittest's runner
separator2 = '-' * 70


# Copied from unittest.result
def failfast(method):
    @wraps(method)
    def inner(self, *args, **kw):
        if self.failfast:
            self.stop()
        return method(self, *args, **kw)
    return inner


class ResultCollecter(object):
    """Collecter for test results.  This handles creating
    :class:`~.TestResult` instances and handing them off the registered
    result output handlers.

    """

    # Temporary compatibility with unittest's runner
    separator2 = separator2

    def __init__(self, buffer=False, failfast=False):
        self.buffer = buffer
        self.failfast = failfast
        self._handlers = []
        self.testsRun = 0
        self.expectedFailures = []
        self.unexpectedSuccesses = []
        self.skipped = []
        self.failures = []
        self.errors = []
        self.shouldStop = False
        self._successful = True
        self._mirror_output = False
        self._stderr_buffer = None
        self._stdout_buffer = None
        self._original_stderr = sys.stderr
        self._original_stdout = sys.stdout

    def _setup_stdout(self):
        """Hook stdout and stderr if buffering is enabled.

        """
        if self.buffer:
            if self._stderr_buffer is None:
                self._stderr_buffer = StringIO()
                self._stdout_buffer = StringIO()
            sys.stdout = self._stdout_buffer
            sys.stderr = self._stderr_buffer

    def _restore_stdout(self):
        """Unhook stdout and stderr if buffering is enabled.

        """
        if self.buffer:
            if self._mirror_output:
                output = sys.stdout.getvalue()
                error = sys.stderr.getvalue()
                if output:
                    if not output.endswith('\n'):
                        output += '\n'
                    self._original_stdout.write(STDOUT_LINE % output)
                if error:
                    if not error.endswith('\n'):
                        error += '\n'
                    self._original_stderr.write(STDERR_LINE % error)

            sys.stdout = self._original_stdout
            sys.stderr = self._original_stderr
            self._stdout_buffer.seek(0)
            self._stdout_buffer.truncate()
            self._stderr_buffer.seek(0)
            self._stderr_buffer.truncate()

    def printErrors(self):  # pragma: no cover
        # FIXME: Remove
        pass

    def add_result_handler(self, handler):
        """Register a new result handler.

        """
        self._handlers.append(handler)

    def startTest(self, test):
        """Indicate that an individual test is starting.

        Parameters
        ----------
        test : unittest.TestCase
            The test that is starting.

        """
        self._mirror_output = False
        self._setup_stdout()
        self.testsRun += 1
        for handler in self._handlers:
            handler.start_test(test)

    def stopTest(self, test):
        """Indicate that an individual test has completed.

        Parameters
        ----------
        test : unittest.TestCase
            The test that has completed.

        """
        for handler in self._handlers:
            handler.stop_test(test)
        self._restore_stdout()
        self._mirror_output = False

    def startTestRun(self):
        """Indicate that the test run is starting.

        """
        for handler in self._handlers:
            handler.start_test_run()

    def stopTestRun(self):
        """Indicate that the test run has completed.

        """
        for handler in self._handlers:
            handler.stop_test_run()

    def add_result(self, result):
        """Add an already-constructed :class:`~.TestResult` to this
        :class:`~.ResultCollecter`.

        This may be used when collecting results created by other
        ResultCollecters (e.g. in subprocesses).

        """
        for handler in self._handlers:
            handler(result)
        if self._successful and result.status not in _successful_results:
            self._successful = False

    def _handle_result(self, test, status, exception=None, message=None):
        """Create a :class:`~.TestResult` and add it to this
        :class:`~ResultCollecter`.

        Parameters
        ----------
        test : unittest.TestCase
            The test that this result will represent.
        status : haas.result.TestCompletionStatus
            The status of the test.
        exception : tuple
            ``exc_info`` tuple ``(type, value, traceback)``.
        message : str
            Optional message associated with the result (e.g. skip
            reason).

        """
        if self.buffer:
            stderr = self._stderr_buffer.getvalue()
            stdout = self._stdout_buffer.getvalue()
        else:
            stderr = stdout = None
        result = TestResult.from_test_case(
            test,
            status,
            exception=exception,
            message=message,
            stdout=stdout,
            stderr=stderr,
        )
        self.add_result(result)
        return result

    @failfast
    def addError(self, test, exception):
        """Register that a test ended in an error.

        Parameters
        ----------
        test : unittest.TestCase
            The test that has completed.
        exception : tuple
            ``exc_info`` tuple ``(type, value, traceback)``.

        """
        result = self._handle_result(
            test, TestCompletionStatus.error, exception=exception)
        self.errors.append(result)
        self._mirror_output = True

    @failfast
    def addFailure(self, test, exception):
        """Register that a test ended with a failure.

        Parameters
        ----------
        test : unittest.TestCase
            The test that has completed.
        exception : tuple
            ``exc_info`` tuple ``(type, value, traceback)``.

        """
        result = self._handle_result(
            test, TestCompletionStatus.failure, exception=exception)
        self.failures.append(result)
        self._mirror_output = True

    def addSuccess(self, test):
        """Register that a test ended in success.

        Parameters
        ----------
        test : unittest.TestCase
            The test that has completed.

        """
        self._handle_result(test, TestCompletionStatus.success)

    def addSkip(self, test, reason):
        """Register that a test that was skipped.

        Parameters
        ----------
        test : unittest.TestCase
            The test that has completed.
        reason : str
            The reason the test was skipped.

        """
        result = self._handle_result(
            test, TestCompletionStatus.skipped, message=reason)
        self.skipped.append(result)

    def addExpectedFailure(self, test, exception):
        """Register that a test that failed and was expected to fail.

        Parameters
        ----------
        test : unittest.TestCase
            The test that has completed.
        exception : tuple
            ``exc_info`` tuple ``(type, value, traceback)``.

        """
        result = self._handle_result(
            test, TestCompletionStatus.expected_failure, exception=exception)
        self.expectedFailures.append(result)

    @failfast
    def addUnexpectedSuccess(self, test):
        """Register a test that passed unexpectedly.

        Parameters
        ----------
        test : unittest.TestCase
            The test that has completed.

        """
        result = self._handle_result(
            test, TestCompletionStatus.unexpected_success)
        self.unexpectedSuccesses.append(result)

    def wasSuccessful(self):
        """Return ``True`` if the run was successful.

        """
        return self._successful

    def stop(self):
        """Set the ``shouldStop`` flag, used by the test cases to determine if
        they should terminate early.

        """
        self.shouldStop = True
