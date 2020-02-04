# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from datetime import datetime, timedelta

from ..plugins.i_result_handler_plugin import IResultHandlerPlugin
from ..result import (
    ResultCollector, TestResult, TestCompletionStatus, TestDuration
)
from ..testing import unittest
from . import _test_cases, _test_case_data
from .fixtures import ExcInfoFixture, MockDateTime
from .compat import mock


class TestTextTestResult(ExcInfoFixture, unittest.TestCase):

    def test_result_collector_calls_handlers_start_stop_methods(self):
        # Given
        handler = mock.Mock(spec=IResultHandlerPlugin)
        collector = ResultCollector()
        collector.add_result_handler(handler)
        case = _test_cases.TestCase('test_method')

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
        collector.startTest(case)

        # Then
        handler.start_test.assert_called_once_with(case)
        self.assertFalse(handler.called)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.stop_test.called)

        # When
        handler.reset_mock()
        collector.stopTest(case)

        # Then
        handler.stop_test.assert_called_once_with(case)
        self.assertFalse(handler.called)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)

    def test_unicode_traceback(self):
        # Given
        handler = mock.Mock(spec=IResultHandlerPlugin)
        collector = ResultCollector()
        collector.add_result_handler(handler)
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        # When
        with mock.patch('haas.result.datetime', new=MockDateTime(start_time)):
            collector.startTest(case)

        # Then
        self.assertTrue(handler.start_test.called)
        handler.start_test.reset_mock()

        # Given
        msg = '\N{GREEK SMALL LETTER PHI}'.encode('utf-8')
        with self.failure_exc_info(msg) as exc_info:
            expected_result = TestResult.from_test_case(
                case, TestCompletionStatus.error, expected_duration,
                exception=exc_info)
            # When
            with mock.patch(
                    'haas.result.datetime', new=MockDateTime(end_time)):
                collector.addError(case, exc_info)

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)
        self.assertFalse(collector.wasSuccessful())

    def test_result_collector_calls_handlers_on_error(self):
        # Given
        handler = mock.Mock(spec=IResultHandlerPlugin)
        collector = ResultCollector()
        collector.add_result_handler(handler)
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        # When
        with mock.patch('haas.result.datetime', new=MockDateTime(start_time)):
            collector.startTest(case)

        # Then
        self.assertTrue(handler.start_test.called)
        handler.start_test.reset_mock()

        # When
        with self.exc_info(RuntimeError) as exc_info:
            # Given
            expected_result = TestResult.from_test_case(
                case, TestCompletionStatus.error, expected_duration,
                exception=exc_info)

            # When
            with mock.patch(
                    'haas.result.datetime', new=MockDateTime(end_time)):
                collector.addError(case, exc_info)

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)
        self.assertFalse(collector.wasSuccessful())

    def test_result_collector_calls_handlers_on_failure(self):
        # Given
        handler = mock.Mock(spec=IResultHandlerPlugin)
        collector = ResultCollector()
        collector.add_result_handler(handler)
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        # When
        with mock.patch('haas.result.datetime', new=MockDateTime(start_time)):
            collector.startTest(case)

        # Then
        self.assertTrue(handler.start_test.called)
        handler.start_test.reset_mock()

        # Given
        with self.failure_exc_info() as exc_info:
            expected_result = TestResult.from_test_case(
                case, TestCompletionStatus.failure, expected_duration,
                exception=exc_info)

            # When
            with mock.patch(
                    'haas.result.datetime', new=MockDateTime(end_time)):
                collector.addFailure(case, exc_info)

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)
        self.assertFalse(collector.wasSuccessful())

    def test_result_collector_calls_handlers_on_success(self):
        # Given
        handler = mock.Mock(spec=IResultHandlerPlugin)
        collector = ResultCollector()
        collector.add_result_handler(handler)
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        # When
        with mock.patch('haas.result.datetime', new=MockDateTime(start_time)):
            collector.startTest(case)

        # Then
        self.assertTrue(handler.start_test.called)
        handler.start_test.reset_mock()

        # Given
        expected_result = TestResult.from_test_case(
            case, TestCompletionStatus.success, expected_duration)

        # When
        with mock.patch('haas.result.datetime', new=MockDateTime(end_time)):
            collector.addSuccess(case)

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)
        self.assertTrue(collector.wasSuccessful())

    def test_result_collector_calls_handlers_on_skip(self):
        # Given
        handler = mock.Mock(spec=IResultHandlerPlugin)
        collector = ResultCollector()
        collector.add_result_handler(handler)
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        # When
        with mock.patch('haas.result.datetime', new=MockDateTime(start_time)):
            collector.startTest(case)

        # Then
        self.assertTrue(handler.start_test.called)
        handler.start_test.reset_mock()

        # Given
        expected_result = TestResult.from_test_case(
            case, TestCompletionStatus.skipped, expected_duration,
            message='reason')

        # When
        with mock.patch('haas.result.datetime', new=MockDateTime(end_time)):
            collector.addSkip(case, 'reason')

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)
        self.assertTrue(collector.wasSuccessful())

    def test_result_collector_calls_handlers_on_expected_fail(self):
        # Given
        handler = mock.Mock(spec=IResultHandlerPlugin)
        collector = ResultCollector()
        collector.add_result_handler(handler)
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        # When
        with mock.patch('haas.result.datetime', new=MockDateTime(start_time)):
            collector.startTest(case)

        # Then
        self.assertTrue(handler.start_test.called)
        handler.start_test.reset_mock()

        # Given
        with self.exc_info(RuntimeError) as exc_info:
            expected_result = TestResult.from_test_case(
                case, TestCompletionStatus.expected_failure, expected_duration,
                exception=exc_info)

            # When
            with mock.patch(
                    'haas.result.datetime', new=MockDateTime(end_time)):
                collector.addExpectedFailure(case, exc_info)

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)
        self.assertTrue(collector.wasSuccessful())

    def test_result_collector_calls_handlers_on_unexpected_success(self):
        # Given
        handler = mock.Mock(spec=IResultHandlerPlugin)
        collector = ResultCollector()
        collector.add_result_handler(handler)
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        # When
        with mock.patch('haas.result.datetime', new=MockDateTime(start_time)):
            collector.startTest(case)

        # Then
        self.assertTrue(handler.start_test.called)
        handler.start_test.reset_mock()

        # Given
        expected_result = TestResult.from_test_case(
            case, TestCompletionStatus.unexpected_success, expected_duration)

        # When
        with mock.patch('haas.result.datetime', new=MockDateTime(end_time)):
            collector.addUnexpectedSuccess(case)

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)
        self.assertFalse(collector.wasSuccessful())

    def test_result_collector_should_stop(self):
        # Given
        collector = ResultCollector()

        # Then
        self.assertFalse(collector.shouldStop)

        # When
        collector.stop()

        # Then
        self.assertTrue(collector.shouldStop)

    def test_multiple_errors_from_one_test(self):
        # Given
        collector = ResultCollector()
        case = _test_case_data.TestWithTwoErrors('test_with_two_errors')

        start_time = datetime(2016, 4, 12, 8, 17, 32)
        test_end_time = datetime(2016, 4, 12, 8, 17, 38)
        tear_down_end_time = datetime(2016, 4, 12, 8, 17, 39)

        # When
        with mock.patch(
                'haas.result.datetime',
                new=MockDateTime(
                    [start_time, test_end_time, tear_down_end_time])):
            case.run(collector)

        # Then
        self.assertEqual(len(collector.errors), 2)
