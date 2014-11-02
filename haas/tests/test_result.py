# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from contextlib import contextmanager
import sys

from mock import Mock

from ..plugins.i_result_handler_plugin import IResultHandlerPlugin
from ..result import ResultCollecter, TestResult, TestCompletionStatus
from ..testing import unittest


class TestTextTestResult(unittest.TestCase):

    @contextmanager
    def exc_info(self, cls):
        try:
            raise cls()
        except cls:
            yield sys.exc_info()

    def test_result_collector_calls_handlers_start_stop_methods(self):
        # Given
        handler = Mock(spec=IResultHandlerPlugin)
        collector = ResultCollecter()
        collector.add_result_handler(handler)

        # When
        handler.reset_mock()
        collector.startTestRun()

        # Then
        handler.start_test_run.assert_called_once_with()
        self.assertFalse(handler.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)

        # When
        handler.reset_mock()
        collector.stopTestRun()

        # Then
        handler.stop_test_run.assert_called_once_with()
        self.assertFalse(handler.called)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)

        # When
        handler.reset_mock()
        collector.startTest(self)

        # Then
        handler.start_test.assert_called_once_with(self)
        self.assertFalse(handler.called)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.stop_test.called)

        # When
        handler.reset_mock()
        collector.stopTest(self)

        # Then
        handler.stop_test.assert_called_once_with(self)
        self.assertFalse(handler.called)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)

    def test_result_collector_calls_handlers_call_method(self):
        # Given
        handler = Mock(spec=IResultHandlerPlugin)
        collector = ResultCollecter()
        collector.add_result_handler(handler)

        # When
        handler.reset_mock()
        with self.exc_info(RuntimeError) as exc_info:
            # Given
            expected_result = TestResult.from_test_case(
                self, TestCompletionStatus.error, exception=exc_info)
            collector.addError(self, exc_info)

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)

        # When
        handler.reset_mock()
        with self.exc_info(AssertionError) as exc_info:
            # Given
            expected_result = TestResult.from_test_case(
                self, TestCompletionStatus.failure, exception=exc_info)
            collector.addFailure(self, exc_info)

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)

        # When
        handler.reset_mock()
        expected_result = TestResult.from_test_case(
            self, TestCompletionStatus.success)
        collector.addSuccess(self)

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)

        # When
        handler.reset_mock()
        expected_result = TestResult.from_test_case(
            self, TestCompletionStatus.skipped, message='reason')
        collector.addSkip(self, 'reason')

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)

        # When
        handler.reset_mock()
        with self.exc_info(RuntimeError) as exc_info:
            # Given
            expected_result = TestResult.from_test_case(
                self, TestCompletionStatus.expected_failure,
                exception=exc_info)
            collector.addExpectedFailure(self, exc_info)

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)

        # When
        handler.reset_mock()
        expected_result = TestResult.from_test_case(
            self, TestCompletionStatus.unexpected_success)
        collector.addUnexpectedSuccess(self)

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)
