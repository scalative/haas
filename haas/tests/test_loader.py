# Copyright 2013-2014 Simon Jagoe
from __future__ import unicode_literals

import os
import shutil
import sys
import tempfile
import unittest as python_unittest

from mock import patch

from haas.testing import unittest, expected_failure

from . import _test_cases
from ..loader import Loader, find_top_level_directory, get_module_name


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
        self.assertIsInstance(test, python_unittest.TestCase)
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

    def test_finds_custom_test_names(self):
        loader = Loader(test_method_prefix='non')
        names = loader.find_test_method_names(_test_cases.TestCase)
        self.assertEqual(names, ['non_test_public_method'])


class TestLoadCase(LoaderTestMixin, unittest.TestCase):

    def test_creates_unittest_testsuite(self):
        suite = self.loader.load_case(_test_cases.TestCase)
        self.assertIsInstance(suite, python_unittest.TestSuite)

    def test_creates_custom_testsuite_subclass(self):
        loader = Loader(test_suite_class=TestSuiteSubclass)
        suite = loader.load_case(_test_cases.TestCase)
        self.assertIsInstance(suite, python_unittest.TestSuite)
        self.assertIsInstance(suite, TestSuiteSubclass)

    def test_creates_custom_testsuite_not_subclass(self):
        loader = Loader(test_suite_class=TestSuiteNotSubclass)
        suite = loader.load_case(_test_cases.TestCase)
        self.assertNotIsInstance(suite, python_unittest.TestSuite)
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
        self.assertSuiteClasses(suite, python_unittest.TestSuite)
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


class TestDiscoveryMixin(object):

    def setUp(self):
        self.tmpdir = os.path.abspath(tempfile.mkdtemp())
        self.dirs = dirs = ['tests', 'tests']
        path = self.tmpdir
        for dir_ in dirs:
            path = os.path.join(path, dir_)
            os.makedirs(path)
            with open(os.path.join(path, '__init__.py'), 'w'):
                pass
        destdir = os.path.join(self.tmpdir, *dirs)
        base = os.path.splitext(_test_cases.__file__)[0]
        srcfile = '{0}.py'.format(base)
        shutil.copyfile(
            srcfile, os.path.join(destdir, 'test_cases.py'))

    def tearDown(self):
        shutil.rmtree(self.tmpdir)


class TestFindTopLevelDirectory(TestDiscoveryMixin, unittest.TestCase):

    def test_from_top_level_directory(self):
        directory = find_top_level_directory(self.tmpdir)
        self.assertEqual(directory, self.tmpdir)

    def test_from_leaf_directory(self):
        directory = find_top_level_directory(
            os.path.join(self.tmpdir, *self.dirs))
        self.assertEqual(directory, self.tmpdir)

    def test_from_middle_directory(self):
        directory = find_top_level_directory(
            os.path.join(self.tmpdir, self.dirs[0]))
        self.assertEqual(directory, self.tmpdir)

    def test_from_nonpackage_directory(self):
        nonpackage = os.path.join(self.tmpdir, self.dirs[0], 'nonpackage')
        os.makedirs(nonpackage)
        directory = find_top_level_directory(nonpackage)
        self.assertEqual(directory, nonpackage)

    def test_relative_directory(self):
        relative = os.path.join(self.tmpdir, self.dirs[0], '..', *self.dirs)
        directory = find_top_level_directory(relative)
        self.assertEqual(directory, self.tmpdir)

    def test_no_top_level(self):
        os_path_dirname = os.path.dirname
        def dirname(path):
            if os.path.basename(os_path_dirname(path)) not in self.dirs:
                return path
            return os_path_dirname(path)
        with patch('os.path.dirname', dirname):
            with self.assertRaises(ValueError):
                find_top_level_directory(os.path.join(self.tmpdir, *self.dirs))



class TestGetModuleName(TestDiscoveryMixin, unittest.TestCase):

    def test_module_in_project(self):
        module_path = os.path.join(self.tmpdir, *self.dirs)
        module_name = get_module_name(self.tmpdir, module_path)
        self.assertEqual(module_name, 'tests.tests')

    def test_module_not_in_project_deep(self):
        module_path = os.path.join(self.tmpdir, *self.dirs)
        with self.assertRaises(ValueError):
            get_module_name(os.path.dirname(__file__), module_path)

    def test_module_not_in_project_relpath(self):
        module_path = os.path.abspath(
            os.path.join(self.tmpdir, '..', *self.dirs))
        with self.assertRaises(ValueError):
            get_module_name(self.tmpdir, module_path)


class TestDiscoveryByPath(TestDiscoveryMixin, unittest.TestCase):

    def get_test_cases(self, suite):
        for test in suite:
            if isinstance(test, python_unittest.TestCase):
                yield test
            else:
                for test_ in self.get_test_cases(test):
                    yield test_

    def setUp(self):
        TestDiscoveryMixin.setUp(self)
        self.loader = Loader()

    def tearDown(self):
        del self.loader
        TestDiscoveryMixin.tearDown(self)

    def assertSuite(self, suite):
        self.assertIsInstance(suite, python_unittest.TestSuite)
        tests = list(self.get_test_cases(suite))
        self.assertEqual(len(tests), 1)
        test, = tests
        self.assertIsInstance(test, python_unittest.TestCase)
        self.assertEqual(test._testMethodName, 'test_method')

    def test_from_top_level_directory(self):
        suite = self.loader.discover(self.tmpdir)
        self.assertSuite(suite)

    def test_from_leaf_directory(self):
        suite = self.loader.discover(os.path.join(self.tmpdir, *self.dirs))
        self.assertSuite(suite)

    def test_from_middle_directory(self):
        suite = self.loader.discover(os.path.join(self.tmpdir, self.dirs[0]))
        self.assertSuite(suite)

    def test_from_nonpackage_directory(self):
        nonpackage = os.path.join(self.tmpdir, self.dirs[0], 'nonpackage')
        os.makedirs(nonpackage)
        suite = self.loader.discover(nonpackage)
        self.assertEqual(len(list(suite)), 0)

    def test_relative_directory(self):
        relative = os.path.join(self.tmpdir, self.dirs[0], '..', *self.dirs)
        suite = self.loader.discover(relative)
        self.assertSuite(suite)

    def test_given_correct_top_level_directory(self):
        suite = self.loader.discover(
            self.tmpdir, top_level_directory=self.tmpdir)
        self.assertSuite(suite)

    def test_given_incorrect_top_level_directory(self):
        with self.assertRaises(ImportError):
            self.loader.discover(
                self.tmpdir,
                top_level_directory='/',
            )

    def test_top_level_directory_on_path(self):
        sys.path.insert(0, self.tmpdir)
        try:
            suite = self.loader.discover(self.tmpdir)
        finally:
            sys.path.remove(self.tmpdir)
        self.assertSuite(suite)


class TestDiscoveryByModule(TestDiscoveryMixin, unittest.TestCase):

    def test_not_implemented(self):
        self.assertIsNone(Loader().discover('haas.missingmodule'))
