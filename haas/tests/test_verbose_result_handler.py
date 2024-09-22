# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from datetime import datetime, timedelta
from time import ctime
from io import StringIO
from unittest import mock
import unittest

from ..plugins.result_handler import VerboseTestResultHandler
from ..result import (
    TestResult, TestCompletionStatus, TestDuration)
from . import _test_cases
from .fixtures import ExcInfoFixture


class TestVerboseResultHandler(ExcInfoFixture, unittest.TestCase):

    @mock.patch('sys.stderr', new_callable=StringIO)
    def test_output_start_test_run(self, stderr):
        # Given
        handler = VerboseTestResultHandler(test_count=1)

        # When
        handler.start_test_run()

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @mock.patch('sys.stderr', new_callable=StringIO)
    def test_no_output_stop_test_run(self, stderr):
        # Given
        handler = VerboseTestResultHandler(test_count=1)
        handler.start_test_run()

        # When
        handler.stop_test_run()

        # Then
        output = stderr.getvalue()
        self.assertTrue(output.startswith('\n' + handler.separator2))
        self.assertTrue(output.endswith('OK\n'))
        self.assertRegex(
            output.replace('\n', ''), r'--+.*?Ran 0 tests.*?OK')

    @mock.patch('time.ctime')
    @mock.patch('sys.stderr', new_callable=StringIO)
    def test_output_start_test(self, stderr, mock_ctime):
        # Given
        case = _test_cases.TestCase('test_method')
        handler = VerboseTestResultHandler(test_count=1)
        mock_ctime.return_value = expected_time = ctime()
        expected_description = handler.get_test_description(case)

        # When
        handler.start_test(case)

        # Then
        output = stderr.getvalue()
        self.assertEqual(
            output, '[{0}] (1/1) {1} ... '.format(
                expected_time, expected_description))

    @mock.patch('sys.stderr', new_callable=StringIO)
    def test_no_output_stop_test(self, stderr):
        # Given
        handler = VerboseTestResultHandler(test_count=1)
        case = _test_cases.TestCase('test_method')

        # When
        handler.stop_test(case)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @mock.patch('sys.stderr', new_callable=StringIO)
    def test_output_on_error(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = VerboseTestResultHandler(test_count=1)
        with self.exc_info(RuntimeError) as exc_info:
            result = TestResult.from_test_case(
                case, TestCompletionStatus.error, expected_duration,
                exception=exc_info)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, 'ERROR\n')

    @mock.patch('sys.stderr', new_callable=StringIO)
    def test_output_on_failure(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = VerboseTestResultHandler(test_count=1)
        with self.failure_exc_info() as exc_info:
            result = TestResult.from_test_case(
                case, TestCompletionStatus.failure, expected_duration,
                exception=exc_info)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, 'FAIL\n')

    @mock.patch('sys.stderr', new_callable=StringIO)
    def test_output_on_success(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = VerboseTestResultHandler(test_count=1)
        result = TestResult.from_test_case(
            case, TestCompletionStatus.success, expected_duration)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, 'ok\n')

    @mock.patch('sys.stderr', new_callable=StringIO)
    def test_output_on_skip(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = VerboseTestResultHandler(test_count=1)
        result = TestResult.from_test_case(
            case, TestCompletionStatus.skipped, expected_duration,
            message='reason')

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, 'skipped \'reason\'\n')

    @mock.patch('sys.stderr', new_callable=StringIO)
    def test_output_on_expected_fail(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = VerboseTestResultHandler(test_count=1)
        with self.exc_info(RuntimeError) as exc_info:
            result = TestResult.from_test_case(
                case, TestCompletionStatus.expected_failure, expected_duration,
                exception=exc_info)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, 'expected failure\n')

    @mock.patch('sys.stderr', new_callable=StringIO)
    def test_output_on_unexpected_success(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = VerboseTestResultHandler(test_count=1)
        result = TestResult.from_test_case(
            case, TestCompletionStatus.unexpected_success, expected_duration)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, 'unexpected success\n')

    @mock.patch('sys.stderr', new_callable=StringIO)
    def test_output_with_error_on_stop_test_run(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = VerboseTestResultHandler(test_count=1)
        handler.start_test_run()
        with self.exc_info(RuntimeError) as exc_info:
            result = TestResult.from_test_case(
                case, TestCompletionStatus.error, expected_duration,
                exception=exc_info)

        # When
        handler(result)
        handler.stop_test_run()

        # Then
        output = stderr.getvalue().replace('\n', '')
        description = handler.get_test_description(
            case).replace('(', r'\(').replace(')', r'\)')
        self.assertRegex(
            output, '{0}.*?Traceback.*?RuntimeError'.format(
                description))

    @mock.patch('sys.stderr', new_callable=StringIO)
    def test_output_with_failure_on_stop_test_run(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = VerboseTestResultHandler(test_count=1)
        handler.start_test_run()
        with self.failure_exc_info() as exc_info:
            result = TestResult.from_test_case(
                case, TestCompletionStatus.failure, expected_duration,
                exception=exc_info)

        # When
        handler(result)
        handler.stop_test_run()

        # Then
        output = stderr.getvalue().replace('\n', '')
        description = handler.get_test_description(
            case).replace('(', r'\(').replace(')', r'\)').replace('\n', '')
        self.assertRegex(
            output, '{0}.*?Traceback.*?AssertionError'.format(
                description))
        # The contents of unittest.TestCase should not be in the traceback
        self.assertNotIn('raise', output)
