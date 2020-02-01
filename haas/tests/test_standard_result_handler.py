# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from datetime import datetime, timedelta

from mock import patch
from six.moves import StringIO

from ..plugins.result_handler import StandardTestResultHandler
from ..result import (
    TestResult, TestCompletionStatus, TestDuration)
from ..testing import unittest
from . import _test_cases
from .fixtures import ExcInfoFixture


class TestStandardResultHandler(ExcInfoFixture, unittest.TestCase):

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_start_test_run(self, stderr):
        # Given
        handler = StandardTestResultHandler(test_count=1)

        # When
        handler.start_test_run()

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_output_stop_test_run(self, stderr):
        # Given
        handler = StandardTestResultHandler(test_count=1)
        handler.start_test_run()

        # When
        handler.stop_test_run()

        # Then
        output = stderr.getvalue()
        self.assertTrue(output.startswith('\n' + handler.separator2))
        self.assertTrue(output.endswith('OK\n'))
        self.assertRegexpMatches(
            output.replace('\n', ''), r'--+.*?Ran 0 tests.*?OK')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_start_test(self, stderr):
        # Given
        handler = StandardTestResultHandler(test_count=1)
        case = _test_cases.TestCase('test_method')

        # When
        handler.start_test(case)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_stop_test(self, stderr):
        # Given
        handler = StandardTestResultHandler(test_count=1)
        case = _test_cases.TestCase('test_method')

        # When
        handler.stop_test(case)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_on_error(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = StandardTestResultHandler(test_count=1)
        with self.exc_info(RuntimeError) as exc_info:
            result = TestResult.from_test_case(
                case, TestCompletionStatus.error, expected_duration,
                exception=exc_info)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, 'E')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_on_failure(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = StandardTestResultHandler(test_count=1)
        with self.failure_exc_info() as exc_info:
            result = TestResult.from_test_case(
                case, TestCompletionStatus.failure, expected_duration,
                exception=exc_info)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, 'F')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_on_success(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = StandardTestResultHandler(test_count=1)
        result = TestResult.from_test_case(
            case, TestCompletionStatus.success, expected_duration)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '.')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_on_skip(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = StandardTestResultHandler(test_count=1)
        result = TestResult.from_test_case(
            case, TestCompletionStatus.skipped, expected_duration,
            message='reason')

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, 's')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_on_expected_fail(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = StandardTestResultHandler(test_count=1)
        with self.exc_info(RuntimeError) as exc_info:
            result = TestResult.from_test_case(
                case, TestCompletionStatus.expected_failure, expected_duration,
                exception=exc_info)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, 'x')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_on_unexpected_success(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = StandardTestResultHandler(test_count=1)
        result = TestResult.from_test_case(
            case, TestCompletionStatus.unexpected_success, expected_duration)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, 'u')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_with_error_on_stop_test_run(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = StandardTestResultHandler(test_count=1)
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
        self.assertRegexpMatches(
            output, '{0}.*?Traceback.*?RuntimeError'.format(
                description))

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_with_failure_on_stop_test_run(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = StandardTestResultHandler(test_count=1)
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
        self.assertRegexpMatches(
            output, '{0}.*?Traceback.*?AssertionError'.format(
                description))
        # The contents of unittest.TestCase should not be in the traceback
        self.assertNotIn('raise', output)
