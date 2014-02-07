# Copyright 2013-2014 Simon Jagoe
import unittest

from . import _test_cases
from ..loader import Loader


class LoaderTestMixin(object):

    def setUp(self):
        self.loader = Loader()

    def tearDown(self):
        del self.loader


class TestSuiteSubclass(unittest.TestSuite):

    pass


class TestSuiteNotSubclass(object):

    def __init__(self, tests=()):
        self.tests = tests

    def __iter__(self):
        return iter(self.tests)


class TestLoadTest(LoaderTestMixin, unittest.TestCase):

    def test_creates_instance_for_valid_test(self):
        test = self.loader.load_test(_test_cases.TestCase, 'test_method')
        self.assertIsInstance(test, unittest.TestCase)
        self.assertIsInstance(test, _test_cases.TestCase)

    def test_raises_for_invalid_test(self):
        with self.assertRaises(TypeError):
            self.loader.load_test(_test_cases.NotTestCase, 'test_method')

    def test_raises_for_test_suite(self):
        with self.assertRaises(TypeError):
            self.loader.load_test(_test_cases.TestSuite, 'test_method')


class TestFindTestMethodNames(LoaderTestMixin, unittest.TestCase):

    def test_finds_valid_test_names(self):
        names = self.loader.find_test_method_names(_test_cases.TestCase)
        self.assertEqual(names, ['test_method'])


class TestLoadCase(LoaderTestMixin, unittest.TestCase):

    def test_creates_unittest_testsuite(self):
        suite = self.loader.load_case(_test_cases.TestCase)
        self.assertIsInstance(suite, unittest.TestSuite)

    def test_creates_custom_testsuite_subclass(self):
        loader = Loader(test_suite_class=TestSuiteSubclass)
        suite = loader.load_case(_test_cases.TestCase)
        self.assertIsInstance(suite, unittest.TestSuite)
        self.assertIsInstance(suite, TestSuiteSubclass)

    def test_creates_custom_testsuite_not_subclass(self):
        loader = Loader(test_suite_class=TestSuiteNotSubclass)
        suite = loader.load_case(_test_cases.TestCase)
        self.assertNotIsInstance(suite, unittest.TestSuite)
        self.assertIsInstance(suite, TestSuiteNotSubclass)

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
        self.assertEqual(len(sub_suites), 1)
        self.assertIsInstance(sub_suites[0], klass)

    def test_find_all_cases_in_module(self):
        cases = self.loader.get_test_cases_from_module(_test_cases)
        self.assertEqual(cases, [_test_cases.TestCase])

    def test_load_all_cases_in_module(self):
        suite = self.loader.load_module(_test_cases)
        self.assertSuiteClasses(suite, unittest.TestSuite)
        sub_suites = list(suite)
        self.assertEqual(len(sub_suites), 1)
        cases = list(sub_suites[0])
        self.assertEqual(len(cases), 1)
        case = cases[0]
        self.assertIsInstance(case, _test_cases.TestCase)

    def test_creates_custom_testsuite_subclass(self):
        loader = Loader(test_suite_class=TestSuiteSubclass)
        suite = loader.load_module(_test_cases)
        self.assertSuiteClasses(suite, TestSuiteSubclass)

    def test_creates_custom_testsuite_not_subclass(self):
        loader = Loader(test_suite_class=TestSuiteNotSubclass)
        suite = loader.load_module(_test_cases)
        self.assertSuiteClasses(suite, TestSuiteNotSubclass)
