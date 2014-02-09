# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import unicode_literals

from ..suite import TestSuite
from ..testing import unittest


TestCase = unittest.TestCase


class TestTestSuiteCount(unittest.TestCase):

    def test_count_empty(self):
        suite = TestSuite()
        self.assertEqual(suite.countTestCases(), 0)

    def test_one_level(self):
        suite = TestSuite(tests=[unittest.TestCase(), TestSuite()])
        self.assertEqual(suite.countTestCases(), 1)

    def test_suite_not_included_in_count(self):
        suite = TestSuite(
            tests=[
                TestSuite(tests=[TestSuite(), TestSuite(), TestSuite()]),
                TestSuite(),
                TestSuite(),
            ],
        )
        self.assertEqual(suite.countTestCases(), 0)

    def test_cases_included_in_count(self):
        suite = TestSuite(
            tests=[
                TestSuite(
                    tests=[
                        unittest.TestCase(),
                        TestSuite(),
                        TestSuite(),
                    ],
                ),
                unittest.TestCase(),
                TestSuite(),
            ],
        )
        self.assertEqual(suite.countTestCases(), 2)


class TestTestSuiteEquality(unittest.TestCase):

    def test_equal_to_itself_empty(self):
        suite = TestSuite()
        self.assertEqual(suite, suite)

    def test_not_equal_to_empty_list(self):
        suite = TestSuite()
        self.assertNotEqual(suite, [])

    def test_equal_to_itself_nested(self):
        suite = TestSuite(
            tests=[
                TestSuite(
                    tests=[
                        unittest.TestCase(),
                        TestSuite(),
                        TestSuite(),
                    ],
                ),
                unittest.TestCase(),
                TestSuite(),
            ],
        )
        self.assertEqual(suite, suite)

    def test_equal_to_other_nested(self):
        suite = TestSuite(
            tests=[
                TestSuite(
                    tests=[
                        unittest.TestCase(),
                        TestSuite(),
                        TestSuite(),
                    ],
                ),
                unittest.TestCase(),
                TestSuite(),
            ],
        )
        suite2 = TestSuite(
            tests=[
                TestSuite(
                    tests=[
                        unittest.TestCase(),
                        TestSuite(),
                        TestSuite(),
                    ],
                ),
                unittest.TestCase(),
                TestSuite(),
            ],
        )
        self.assertEqual(suite, suite2)
