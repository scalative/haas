# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals


from ..result import ResultCollector
from ..testing import unittest
from . import _test_cases
from .fixtures import ExcInfoFixture


class TestFailfast(ExcInfoFixture, unittest.TestCase):

    def test_failfast_enabled_on_error(self):
        # Given
        collector = ResultCollector(failfast=True)
        self.assertFalse(collector.shouldStop)
        case = _test_cases.TestCase('test_method')

        collector.startTest(case)

        # When
        with self.exc_info(RuntimeError) as exc_info:
            collector.addError(case, exc_info)

        # Then
        self.assertTrue(collector.shouldStop)

    def test_failfast_enabled_on_failure(self):
        # Given
        collector = ResultCollector(failfast=True)
        self.assertFalse(collector.shouldStop)
        case = _test_cases.TestCase('test_method')

        collector.startTest(case)

        # When
        with self.failure_exc_info() as exc_info:
            collector.addFailure(case, exc_info)

        # Then
        self.assertTrue(collector.shouldStop)

    def test_failfast_enabled_on_unexpected_success(self):
        # Given
        collector = ResultCollector(failfast=False)
        self.assertFalse(collector.shouldStop)
        case = _test_cases.TestCase('test_method')

        collector.startTest(case)

        # When
        collector.addUnexpectedSuccess(case)

        # Then
        self.assertFalse(collector.shouldStop)

    def test_failfast_disabled_on_error(self):
        # Given
        collector = ResultCollector(failfast=False)
        self.assertFalse(collector.shouldStop)
        case = _test_cases.TestCase('test_method')

        collector.startTest(case)

        # When
        with self.exc_info(RuntimeError) as exc_info:
            collector.addError(case, exc_info)

        # Then
        self.assertFalse(collector.shouldStop)

    def test_failfast_disabled_on_failure(self):
        # Given
        collector = ResultCollector(failfast=False)
        self.assertFalse(collector.shouldStop)
        case = _test_cases.TestCase('test_method')

        collector.startTest(case)

        # When
        with self.failure_exc_info() as exc_info:
            collector.addFailure(case, exc_info)

        # Then
        self.assertFalse(collector.shouldStop)

    def test_failfast_disabled_on_unexpected_success(self):
        # Given
        collector = ResultCollector(failfast=False)
        self.assertFalse(collector.shouldStop)
        case = _test_cases.TestCase('test_method')

        collector.startTest(case)

        # When
        collector.addUnexpectedSuccess(case)

        # Then
        self.assertFalse(collector.shouldStop)
