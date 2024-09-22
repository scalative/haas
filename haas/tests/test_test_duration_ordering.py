# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
import unittest
from datetime import datetime, timedelta

from ..result import TestDuration


class TestTestDurationOrdering(unittest.TestCase):

    def test_unorderable_types(self):
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        duration = TestDuration(start_time, end_time)

        # Then
        self.assertNotEqual(duration, object())

        with self.assertRaises(TypeError):
            duration < object()

        with self.assertRaises(TypeError):
            duration > object()

    def test_hash_equal(self):
        # Given
        start_time1 = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time1 = start_time1 + duration
        duration1 = TestDuration(start_time1, end_time1)

        start_time2 = datetime(2015, 12, 23, 8, 14, 12)
        end_time2 = start_time2 + duration
        duration2 = TestDuration(start_time2, end_time2)

        # Then
        self.assertEqual(hash(duration1), hash(duration2))

    def test_hash_not_equal(self):
        # Given
        start_time1 = datetime(2015, 12, 23, 8, 14, 12)
        duration1 = timedelta(seconds=10)
        end_time1 = start_time1 + duration1
        duration1 = TestDuration(start_time1, end_time1)

        start_time2 = datetime(2015, 12, 23, 8, 14, 12)
        duration2 = timedelta(seconds=15)
        end_time2 = start_time2 + duration2
        duration2 = TestDuration(start_time2, end_time2)

        # Then
        self.assertNotEqual(hash(duration1), hash(duration2))

    def test_equality(self):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        duration1 = TestDuration(start_time, end_time)
        duration2 = TestDuration(start_time, end_time)
        self.assertIsNot(duration1, duration2)

        # When/Then
        self.assertEqual(duration1, duration2)
        self.assertLessEqual(duration1, duration2)
        self.assertGreaterEqual(duration1, duration2)
        with self.assertRaisesRegex(
                self.failureException, 'not less than'):
            self.assertLess(duration1, duration2)
        with self.assertRaisesRegex(
                self.failureException, 'not greater than'):
            self.assertGreater(duration1, duration2)

        self.assertNotEqual(duration1, object())

        # Given
        start_time1 = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time1 = start_time1 + duration
        duration1 = TestDuration(start_time1, end_time1)

        start_time2 = datetime(2015, 12, 23, 8, 14, 12)
        end_time2 = start_time2 + duration
        duration2 = TestDuration(start_time2, end_time2)

        # When/Then
        self.assertEqual(duration1, duration2)
        self.assertLessEqual(duration1, duration2)
        self.assertGreaterEqual(duration1, duration2)
        with self.assertRaisesRegex(
                self.failureException, 'not less than'):
            self.assertLess(duration1, duration2)
        with self.assertRaisesRegex(
                self.failureException, 'not greater than'):
            self.assertGreater(duration1, duration2)

    def test_lessthan(self):
        # Given
        start_time1 = datetime(2015, 12, 23, 8, 14, 12)
        duration1 = timedelta(seconds=10)
        end_time1 = start_time1 + duration1
        duration1 = TestDuration(start_time1, end_time1)

        start_time2 = datetime(2014, 12, 23, 8, 14, 12)
        duration2 = timedelta(seconds=15)
        end_time2 = start_time2 + duration2
        duration2 = TestDuration(start_time2, end_time2)

        # When/Then
        self.assertNotEqual(duration1, duration2)
        self.assertLess(duration1, duration2)
        self.assertLessEqual(duration1, duration2)
        with self.assertRaisesRegex(
                self.failureException, 'not greater than or equal to'):
            self.assertGreaterEqual(duration1, duration2)
        with self.assertRaisesRegex(
                self.failureException, 'not greater than'):
            self.assertGreater(duration1, duration2)

    def test_greaterthan(self):
        # Given
        start_time1 = datetime(2015, 12, 23, 8, 14, 12)
        duration1 = timedelta(seconds=15)
        end_time1 = start_time1 + duration1
        duration1 = TestDuration(start_time1, end_time1)

        start_time2 = datetime(2014, 12, 23, 8, 14, 12)
        duration2 = timedelta(seconds=5)
        end_time2 = start_time2 + duration2
        duration2 = TestDuration(start_time2, end_time2)

        # When/Then
        self.assertNotEqual(duration1, duration2)
        self.assertGreater(duration1, duration2)
        self.assertGreaterEqual(duration1, duration2)
        with self.assertRaisesRegex(
                self.failureException, 'not less than or equal to'):
            self.assertLessEqual(duration1, duration2)
        with self.assertRaisesRegex(
                self.failureException, 'not less than'):
            self.assertLess(duration1, duration2)
