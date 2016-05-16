# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

import unittest as python_unittest

import six

from haas.testing import unittest

from . import _test_cases
from . import _test_case_data
from ..loader import Loader
from ..suite import TestSuite


class LoaderTestMixin(object):

    def setUp(self):
        self.loader = Loader()

    def tearDown(self):
        del self.loader


class TestLoadTest(LoaderTestMixin, unittest.TestCase):

    def test_creates_instance_for_valid_test(self):
        test = self.loader.load_test(_test_cases.TestCase, 'test_method')
        self.assertIsInstance(test, python_unittest.TestCase)
        self.assertIsInstance(test, _test_cases.TestCase)

    def test_raises_for_invalid_test(self):
        with self.assertRaises(TypeError):
            self.loader.load_test(_test_cases.NotTestCase, 'test_method')

    def test_raises_for_test_suite(self):
        with self.assertRaises(TypeError):
            self.loader.load_test(_test_cases.TestSuite, 'test_method')

    def test_create_custom_class(self):
        loader = Loader(test_case_class=_test_case_data.TestCaseSubclass)
        test = loader.load_test(_test_case_data.TestCaseSubclass, 'test_method')
        self.assertIsInstance(test, _test_case_data.TestCaseSubclass)

    def test_create_custom_class_raises(self):
        loader = Loader(test_case_class=_test_case_data.TestCaseSubclass)
        with self.assertRaises(TypeError):
            loader.load_test(unittest.TestCase, 'test_method')

    def test_load_test_overridden_init(self):
        test = self.loader.load_test(
            _test_case_data.BadlySubclassedTestCase, 'test_method')
        self.assertIsInstance(test, python_unittest.TestCase)
        self.assertIsInstance(test, unittest.TestCase)


class TestFindTestMethodNames(LoaderTestMixin, unittest.TestCase):

    def test_finds_valid_test_names(self):
        names = self.loader.find_test_method_names(_test_cases.TestCase)
        self.assertEqual(names, ['test_method'])

    def test_finds_custom_test_names(self):
        loader = Loader(test_method_prefix='non')
        names = loader.find_test_method_names(_test_cases.TestCase)
        self.assertEqual(names, ['non_test_public_method'])


class TestLoadCase(LoaderTestMixin, unittest.TestCase):

    def test_creates_testsuite(self):
        suite = self.loader.load_case(_test_cases.TestCase)
        self.assertIsInstance(suite, TestSuite)

    def test_creates_custom_testsuite_subclass(self):
        loader = Loader(
            test_suite_class=_test_case_data.TestSuiteSubclass)
        suite = loader.load_case(_test_cases.TestCase)
        self.assertIsInstance(suite, TestSuite)
        self.assertIsInstance(suite, _test_case_data.TestSuiteSubclass)

    def test_creates_custom_testsuite_not_subclass(self):
        loader = Loader(test_suite_class=_test_case_data.TestSuiteNotSubclass)
        suite = loader.load_case(_test_cases.TestCase)
        self.assertNotIsInstance(suite, TestSuite)
        self.assertIsInstance(suite, _test_case_data.TestSuiteNotSubclass)

    def test_raises_for_invalid_test(self):
        with self.assertRaises(TypeError):
            self.loader.load_case(_test_cases.NotTestCase, 'test_method')

    def test_raises_for_test_suite(self):
        with self.assertRaises(TypeError):
            self.loader.load_case(_test_cases.TestSuite, 'test_method')


class TestLoadModule(LoaderTestMixin, unittest.TestCase):

    def assertSuiteClasses(self, suite, klass):
        self.assertIsInstance(suite, klass)
        sub_suites = list(suite)
        self.assertEqual(len(sub_suites), 2)
        for sub_suite in sub_suites:
            self.assertIsInstance(sub_suite, klass)

    def test_find_all_cases_in_module(self):
        cases = self.loader.get_test_cases_from_module(_test_cases)
        six.assertCountEqual(
            self,
            cases, [_test_cases.TestCase, _test_cases.PythonTestCase])

    def test_load_all_cases_in_module(self):
        suite = self.loader.load_module(_test_cases)
        self.assertSuiteClasses(suite, TestSuite)
        sub_suites = list(suite)
        self.assertEqual(len(sub_suites), 2)
        cases = []
        for sub_suite in sub_suites:
            self.assertEqual(len(list(sub_suite)), 1)
            for case in sub_suite:
                self.assertIsInstance(case, python_unittest.TestCase)
                cases.append(case)
        self.assertEqual(len(cases), 2)

    def test_creates_custom_testsuite_subclass(self):
        loader = Loader(test_suite_class=_test_case_data.TestSuiteSubclass)
        suite = loader.load_module(_test_cases)
        self.assertSuiteClasses(suite, _test_case_data.TestSuiteSubclass)

    def test_creates_custom_testsuite_not_subclass(self):
        loader = Loader(test_suite_class=_test_case_data.TestSuiteNotSubclass)
        suite = loader.load_module(_test_cases)
        self.assertSuiteClasses(suite, _test_case_data.TestSuiteNotSubclass)
