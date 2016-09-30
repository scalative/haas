# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
import locale
import sys
import traceback
import warnings

import six
from six.moves import StringIO

from .error_holder import ErrorHolder


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


def _decode(line, encoding):
    if isinstance(line, six.text_type):
        return line
    try:
        return line.decode(encoding)
    except UnicodeDecodeError:
        return line.decode(encoding, 'replace')


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

    encoding = locale.getpreferredencoding()
    msgLines = [_decode(line, encoding) for line in msgLines]

    if stdout:
        if not stdout.endswith('\n'):
            stdout += '\n'
        msgLines.append(STDOUT_LINE % stdout)
    if stderr:
        if not stderr.endswith('\n'):
            stderr += '\n'
        msgLines.append(STDERR_LINE % stderr)
    return ''.join(msgLines)


class TestDuration(object):
    """An orderable representation of the duration of an individual test.

    """

    def __init__(self, start_time, stop_time=None):
        if stop_time is not None:
            self._start_time = start_time
            self._stop_time = stop_time
            self._duration = stop_time - start_time
        else:
            # Once calculations are done, start & stop are meaningless
            self._start_time = None
            self._stop_time = None
            duration = start_time
            if not isinstance(duration, timedelta):
                duration = timedelta(seconds=float(start_time))
            self._duration = duration
        self._total_seconds = None

    @property
    def start_time(self):
        return self._start_time

    @property
    def stop_time(self):
        return self._stop_time

    @property
    def duration(self):
        return self._duration

    @property
    def total_seconds(self):
        if self._total_seconds is None:
            if sys.version_info < (2, 7):
                delta = self._duration
                total_seconds = delta.microseconds / 1000000.0 + delta.seconds
                total_seconds += delta.days * 24 * 60 * 60
            else:
                total_seconds = self._duration.total_seconds()
            self._total_seconds = total_seconds
        return self._total_seconds

    def __repr__(self):
        return '<TestDuration {0}>'.format(str(self))

    def __str__(self):
        hours_template = '{hours: >3.0f}:'
        template = '{hours_fmt}{minutes:0>2.0f}:{seconds:0>6.3f}'
        minutes, seconds = divmod(self.total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            hours_fmt = hours_template.format(hours=hours)
        else:
            hours_fmt = ''
        return template.format(
            hours_fmt=hours_fmt,
            minutes=minutes,
            seconds=seconds,
        )

    def __eq__(self, other):
        if not hasattr(other, 'duration'):
            return NotImplemented
        return self.duration == other.duration

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        if not hasattr(other, 'duration'):
            return NotImplemented
        return self.duration < other.duration

    def __le__(self, other):
        return not (self > other)

    def __gt__(self, other):
        if not hasattr(other, 'duration'):
            return NotImplemented
        return self.duration > other.duration

    def __ge__(self, other):
        return not (self < other)

    def __hash__(self):
        return hash((self._start_time, self._stop_time))

    # To support statistics.mean() on TestDuration objects
    def as_integer_ratio(self):
        return self.total_seconds.as_integer_ratio()

    def __add__(self, other):
        if not isinstance(other, TestDuration):
            return NotImplemented
        return TestDuration(self.duration + other.duration)

    def __truediv__(self, divisor):
        if not isinstance(self, TestDuration) and isinstance(divisor, int):
            return NotImplemented
        return TestDuration(self.duration / divisor)


class TestResult(object):
    """Container object for all information related to the run of a single
    test.  This contains the test itself, the actual status including
    the reason or error associated with status, along with timing
    information.

    """

    def __init__(self, test_class, test_method_name, status, duration,
                 exception=None, message=None):
        self.test_class = test_class
        self.test_method_name = test_method_name
        self.status = status
        self.exception = exception
        self.message = message
        self.duration = duration

    def __repr__(self):
        template = ('<{0} class={1}, method={2}, exc={3!r}, status={4!r}, '
                    'duration={5!r}>')
        return template.format(
            type(self).__name__, self.test_class.__name__,
            self.test_method_name, self.exception, self.status,
            self.duration)

    def __eq__(self, other):
        if not isinstance(other, TestResult):
            return NotImplemented
        return (
            self.test_class == other.test_class and
            self.test_method_name == other.test_method_name and
            self.status == other.status and
            self.exception == other.exception and
            self.message == other.message and
            self.duration == other.duration
        )

    def __ne__(self, other):
        return not (self == other)

    @classmethod
    def from_test_case(cls, test_case, status, duration,
                       exception=None, message=None, stdout=None, stderr=None):
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
        return cls(test_class, test_method_name, status, duration,
                   exception, message)

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


class ResultCollector(object):
    """Collecter for test results.  This handles creating
    :class:`~.TestResult` instances and handing them off the registered
    result output handlers.

    """

    # Temporary compatibility with unittest's runner
    separator2 = separator2

    def __init__(self, buffer=False, failfast=False):
        self.buffer = buffer
        self.failfast = failfast
        self._result_handlers = []
        self._sorted_handlers = None
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
        self._test_timing = {}

    @property
    def _handlers(self):
        if self._sorted_handlers is None:
            from .plugins.result_handler import sort_result_handlers
            self._sorted_handlers = sort_result_handlers(self._result_handlers)
        return self._sorted_handlers

    @staticmethod
    def _testcase_to_key(test):
        return (type(test), test._testMethodName)

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
        self._result_handlers.append(handler)
        # Reset sorted handlers
        if self._sorted_handlers:
            self._sorted_handlers = None

    def startTest(self, test, start_time=None):
        """Indicate that an individual test is starting.

        Parameters
        ----------
        test : unittest.TestCase
            The test that is starting.
        start_time : datetime
            An internal parameter to allow the parallel test runner to
            set the actual start time of a test run in a subprocess.

        """
        if start_time is None:
            start_time = datetime.utcnow()
        self._test_timing[self._testcase_to_key(test)] = start_time
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
        :class:`~.ResultCollector`.

        This may be used when collecting results created by other
        ResultCollectors (e.g. in subprocesses).

        """
        for handler in self._handlers:
            handler(result)
        if self._successful and result.status not in _successful_results:
            self._successful = False

    def _handle_result(self, test, status, exception=None, message=None):
        """Create a :class:`~.TestResult` and add it to this
        :class:`~ResultCollector`.

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

        started_time = self._test_timing.get(self._testcase_to_key(test))
        if started_time is None and isinstance(test, ErrorHolder):
            started_time = datetime.utcnow()
        elif started_time is None:
            raise RuntimeError(
                'Missing test start! Please report this error as a bug in '
                'haas.')

        completion_time = datetime.utcnow()
        duration = TestDuration(started_time, completion_time)
        result = TestResult.from_test_case(
            test,
            status,
            duration=duration,
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


class ResultCollecter(ResultCollector):
    def __init__(self, *args, **kwargs):
        super(ResultCollecter, self).__init__(*args, **kwargs)
        warnings.warn(
            'ResultCollecter is deprecated in favour of ResultCollector and '
            'will be removed in the next release.',
            DeprecationWarning,
        )
