# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from datetime import datetime, timedelta
import sys

from io import StringIO

from haas.tests.compat import mock
from ..plugins.i_result_handler_plugin import IResultHandlerPlugin
from ..result import (
    ResultCollector, TestResult, TestCompletionStatus, TestDuration
)
from ..testing import unittest
from . import _test_cases
from .fixtures import ExcInfoFixture, MockDateTime


class TestBuffering(ExcInfoFixture, unittest.TestCase):

    @mock.patch('sys.stderr', new_callable=StringIO)
    def test_buffering_stderr(self, stderr):
        # Given
        handler = mock.Mock(spec=IResultHandlerPlugin)
        collector = ResultCollector(buffer=True)
        collector.add_result_handler(handler)
        test_stderr = 'My Test Output'
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
        sys.stderr.write(test_stderr)

        # Then
        self.assertEqual(stderr.getvalue(), '')

        # Given
        with self.exc_info(RuntimeError) as exc_info:
            expected_result = TestResult.from_test_case(
                case, TestCompletionStatus.error, expected_duration,
                exception=exc_info, stderr=test_stderr)
            # When
            with mock.patch(
                    'haas.result.datetime', new=MockDateTime(end_time)):
                collector.addError(case, exc_info)
        collector.stopTest(case)

        # Then
        self.assertIn(test_stderr, expected_result.exception)
        handler.assert_called_once_with(expected_result)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_buffering_stdout(self, stdout):
        # Given
        handler = mock.Mock(spec=IResultHandlerPlugin)
        collector = ResultCollector(buffer=True)
        collector.add_result_handler(handler)
        test_stdout = 'My Test Output'
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
        sys.stdout.write(test_stdout)

        # Then
        self.assertEqual(stdout.getvalue(), '')

        # Given
        with self.exc_info(RuntimeError) as exc_info:
            expected_result = TestResult.from_test_case(
                case, TestCompletionStatus.error, expected_duration,
                exception=exc_info, stdout=test_stdout)

            # When
            with mock.patch(
                    'haas.result.datetime', new=MockDateTime(end_time)):
                collector.addError(case, exc_info)
        collector.stopTest(case)

        # Then
        self.assertIn(test_stdout, expected_result.exception)
        handler.assert_called_once_with(expected_result)
