# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

import os
import shutil
import sys
import tempfile
import unittest as python_unittest

from mock import Mock, patch

from haas.testing import unittest

from haas.tests import _test_cases, builder
from haas.loader import Loader
from haas.module_import_error import ModuleImportError
from haas.suite import find_test_cases, TestSuite
from haas.utils import cd
from ..discoverer import (
    Discoverer,
    filter_test_suite,
    find_module_by_name,
    find_top_level_directory,
    get_module_name,
)


class FilterTestCase(_test_cases.TestCase):

    pass


class TestDiscoveryMixin(object):

    def setUp(self):
        self.tmpdir = os.path.abspath(tempfile.mkdtemp())
        self.dirs = dirs = ['haas_test_package', 'tests']
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
        for key in list(sys.modules.keys()):
            if key in sys.modules and key.startswith(self.dirs[0]):
                del sys.modules[key]
        if self.tmpdir in sys.path:
            sys.path.remove(self.tmpdir)
        shutil.rmtree(self.tmpdir)

    def get_test_cases(self, suite):
        for test in find_test_cases(suite):
            yield test


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
        self.assertEqual(module_name, '.'.join(self.dirs))

    def test_module_not_in_project_deep(self):
        module_path = os.path.join(self.tmpdir, *self.dirs)
        with self.assertRaises(ValueError):
            get_module_name(os.path.dirname(__file__), module_path)

    def test_module_not_in_project_relpath(self):
        module_path = os.path.abspath(
            os.path.join(self.tmpdir, '..', *self.dirs))
        with self.assertRaises(ValueError):
            get_module_name(self.tmpdir, module_path)


class TestFindModuleByName(TestDiscoveryMixin, unittest.TestCase):

    def setUp(self):
        TestDiscoveryMixin.setUp(self)
        sys.path.insert(0, self.tmpdir)

    def tearDown(self):
        sys.path.remove(self.tmpdir)
        TestDiscoveryMixin.tearDown(self)

    def test_package_in_project(self):
        module, case_attributes = find_module_by_name('.'.join(self.dirs))
        dirname = os.path.join(self.tmpdir, *self.dirs)
        filename = os.path.join(dirname, '__init__')
        self.assertEqual(os.path.splitext(module.__file__)[0], filename)

    def test_missing_package_in_project(self):
        module_name = '.'.join(self.dirs + ['missing'])
        module, case_attributes = find_module_by_name(module_name)
        dirname = os.path.join(self.tmpdir, *self.dirs)
        filename = os.path.join(dirname, '__init__')
        self.assertEqual(os.path.splitext(module.__file__)[0], filename)
        self.assertEqual(case_attributes, ['missing'])

    def test_module_attribute_in_project(self):
        module_name = '.'.join(self.dirs + ['test_cases'])
        test_case_name = '.'.join([module_name, 'TestCase'])
        try:
            module, case_attributes = find_module_by_name(test_case_name)
            module_file = module.__file__
        finally:
            del sys.modules[module_name]
        dirname = os.path.join(self.tmpdir, *self.dirs)
        filename = os.path.join(dirname, 'test_cases')
        self.assertEqual(os.path.splitext(module_file)[0], filename)
        self.assertEqual(case_attributes, ['TestCase'])

    def test_missing_top_level_package_in_project(self):
        with self.assertRaises(ImportError):
            find_module_by_name('no_module')


class TestFilterTestSuite(unittest.TestCase):

    def setUp(self):
        self.case_1 = _test_cases.TestCase(methodName='test_method')
        self.case_2 = _test_cases.TestCase(methodName='_private_method')
        self.case_3 = FilterTestCase(methodName='_private_method')
        self.suite = TestSuite(
            [
                TestSuite(
                    [
                        self.case_1,
                        self.case_2,
                    ],
                ),
                TestSuite(
                    [
                        self.case_3,
                    ],
                ),
            ],
        )

    def tearDown(self):
        del self.suite
        del self.case_3
        del self.case_2
        del self.case_1

    def test_filter_by_method_name(self):
        filtered_suite = filter_test_suite(self.suite, 'test_method')
        self.assertEqual(len(filtered_suite), 1)
        test, = filtered_suite
        self.assertIs(test, self.case_1)

    def test_filter_by_class_name(self):
        filtered_suite = filter_test_suite(self.suite, 'FilterTestCase')
        self.assertEqual(len(filtered_suite), 1)
        test, = filtered_suite
        self.assertIs(test, self.case_3)

    def test_filter_by_module_name(self):
        filtered_suite = filter_test_suite(self.suite, '_test_cases')
        self.assertEqual(len(filtered_suite), 2)
        test1, test2 = filtered_suite
        self.assertIs(test1, self.case_1)
        self.assertIs(test2, self.case_2)

    def test_filter_by_package_name(self):
        filtered_suite = filter_test_suite(self.suite, 'test_discoverer')
        self.assertEqual(len(filtered_suite), 1)
        test, = filtered_suite
        self.assertIs(test, self.case_3)

    def test_filter_by_nonexistant_name(self):
        filtered_suite = filter_test_suite(self.suite, 'nothing_called_this')
        self.assertEqual(len(filtered_suite), 0)

    def test_filter_by_class_and_test_name(self):
        filtered_suite = filter_test_suite(
            self.suite, 'TestCase.test_method')
        self.assertEqual(len(filtered_suite), 1)
        test, = filtered_suite
        self.assertIs(test, self.case_1)

    def test_filter_by_module_and_class(self):
        filtered_suite = filter_test_suite(
            self.suite, '_test_cases.TestCase')
        self.assertEqual(len(filtered_suite), 2)
        test1, test2 = filtered_suite
        self.assertIs(test1, self.case_1)
        self.assertIs(test2, self.case_2)

    def test_filter_by_module_and_class_and_test(self):
        filtered_suite = filter_test_suite(
            self.suite, '_test_cases.TestCase.test_method')
        self.assertEqual(len(filtered_suite), 1)
        test1, = filtered_suite
        self.assertIs(test1, self.case_1)


class TestDiscoveryByPath(TestDiscoveryMixin, unittest.TestCase):

    def setUp(self):
        TestDiscoveryMixin.setUp(self)
        self.discoverer = Discoverer(Loader())

    def tearDown(self):
        del self.discoverer
        TestDiscoveryMixin.tearDown(self)

    def assertSuite(self, suite):
        self.assertIsInstance(suite, TestSuite)
        tests = list(self.get_test_cases(suite))
        self.assertEqual(len(tests), 2)
        for test in tests:
            self.assertIsInstance(test, python_unittest.TestCase)
            self.assertEqual(test._testMethodName, 'test_method')

    def test_from_top_level_directory(self):
        suite = self.discoverer.discover(self.tmpdir)
        self.assertSuite(suite)

    def test_from_leaf_directory(self):
        suite = self.discoverer.discover(os.path.join(self.tmpdir, *self.dirs))
        self.assertSuite(suite)

    def test_from_middle_directory(self):
        suite = self.discoverer.discover(
            os.path.join(self.tmpdir, self.dirs[0]))
        self.assertSuite(suite)

    def test_start_from_nonpackage_directory(self):
        nonpackage = os.path.join(self.tmpdir, self.dirs[0], 'nonpackage')
        os.makedirs(nonpackage)
        suite = self.discoverer.discover(nonpackage)
        self.assertEqual(len(list(suite)), 0)

    def test_from_nested_nonpackage_directory(self):
        """
        Regression test for #38
        """
        # Given
        nonpackage = os.path.join(self.tmpdir, 'nonpackage')
        package = os.path.join(nonpackage, 'nonpackage', 'tests')
        os.makedirs(package)
        with open(os.path.join(package, '__init__.py'), 'w'):
            pass
        with open(os.path.join(package, 'test.py'), 'w'):
            pass

        # When
        suite = self.discoverer.discover(nonpackage, nonpackage)

        # Then
        self.assertEqual(suite.countTestCases(), 0)

    def test_relative_directory(self):
        relative = os.path.join(self.tmpdir, self.dirs[0], '..', *self.dirs)
        suite = self.discoverer.discover(relative)
        self.assertSuite(suite)

    def test_given_correct_top_level_directory(self):
        suite = self.discoverer.discover(
            self.tmpdir, top_level_directory=self.tmpdir)
        self.assertSuite(suite)

    def test_given_incorrect_top_level_directory(self):
        with self.assertRaises(ImportError):
            self.discoverer.discover(
                self.tmpdir,
                top_level_directory=os.path.dirname(self.tmpdir),
            )

    def test_top_level_directory_on_path(self):
        sys.path.insert(0, self.tmpdir)
        try:
            suite = self.discoverer.discover(self.tmpdir)
        finally:
            sys.path.remove(self.tmpdir)
        self.assertSuite(suite)


class TestDiscoveryByModule(TestDiscoveryMixin, unittest.TestCase):

    def setUp(self):
        TestDiscoveryMixin.setUp(self)
        self.discoverer = Discoverer(Loader())

    def tearDown(self):
        del self.discoverer
        TestDiscoveryMixin.tearDown(self)

    def test_discover_package(self):
        suite = self.discoverer.discover(
            '.'.join(self.dirs),
            top_level_directory=self.tmpdir,
        )
        tests = list(self.get_test_cases(suite))
        self.assertEqual(len(tests), 2)
        for test in tests:
            self.assertIsInstance(test, python_unittest.TestCase)
            self.assertEqual(test._testMethodName, 'test_method')

    def test_discover_package_no_top_level(self):
        suite = self.discoverer.discover('haas.tests')
        tests = list(self.get_test_cases(suite))
        self.assertGreater(len(tests), 1)

    def test_discover_module(self):
        module = '{0}.test_cases'.format('.'.join(self.dirs))
        suite = self.discoverer.discover(
            module, top_level_directory=self.tmpdir)
        tests = list(self.get_test_cases(suite))
        self.assertEqual(len(tests), 2)
        for test in tests:
            self.assertIsInstance(test, python_unittest.TestCase)
            self.assertEqual(test._testMethodName, 'test_method')

    def test_discover_case(self):
        module = '{0}.test_cases.TestCase'.format('.'.join(self.dirs))
        suite = self.discoverer.discover(
            module, top_level_directory=self.tmpdir)
        tests = list(self.get_test_cases(suite))
        self.assertEqual(len(tests), 1)
        test, = tests
        self.assertIsInstance(test, python_unittest.TestCase)
        self.assertEqual(test._testMethodName, 'test_method')

    def test_discover_missing_case(self):
        module = '{0}.test_cases.MissingTestCase'.format('.'.join(self.dirs))
        suite = self.discoverer.discover(
            module, top_level_directory=self.tmpdir)
        tests = list(self.get_test_cases(suite))
        self.assertEqual(len(tests), 0)

    def test_discover_not_case(self):
        module = '{0}.test_cases.NotTestCase'.format('.'.join(self.dirs))
        suite = self.discoverer.discover(
            module, top_level_directory=self.tmpdir)
        tests = list(self.get_test_cases(suite))
        self.assertEqual(len(tests), 0)

    def test_discover_method(self):
        module = '{0}.test_cases.TestCase.test_method'.format(
            '.'.join(self.dirs))
        suite = self.discoverer.discover(
            module, top_level_directory=self.tmpdir)
        tests = list(self.get_test_cases(suite))
        self.assertEqual(len(tests), 1)
        test, = tests
        self.assertIsInstance(test, python_unittest.TestCase)
        self.assertEqual(test._testMethodName, 'test_method')

    def test_discover_too_many_components(self):
        module = '{0}.test_cases.TestCase.test_method.nothing'.format(
            '.'.join(self.dirs))
        with self.assertRaises(ValueError):
            self.discoverer.discover(module, top_level_directory=self.tmpdir)


class TestDiscoverFilteredTests(TestDiscoveryMixin, unittest.TestCase):

    def setUp(self):
        TestDiscoveryMixin.setUp(self)
        self.discoverer = Discoverer(Loader())

    def tearDown(self):
        del self.discoverer
        TestDiscoveryMixin.tearDown(self)

    def test_discover_subpackage(self):
        suite = self.discoverer.discover(
            'tests',
            top_level_directory=self.tmpdir,
        )
        tests = list(self.get_test_cases(suite))
        self.assertEqual(len(tests), 2)
        for test in tests:
            self.assertIsInstance(test, python_unittest.TestCase)
            self.assertEqual(test._testMethodName, 'test_method')

    def test_discover_test_method(self):
        suite = self.discoverer.discover(
            'test_method',
            top_level_directory=self.tmpdir,
        )
        tests = list(self.get_test_cases(suite))
        self.assertEqual(len(tests), 2)
        for test in tests:
            self.assertIsInstance(test, python_unittest.TestCase)
            self.assertEqual(test._testMethodName, 'test_method')

    def test_discover_class(self):
        suite = self.discoverer.discover(
            'TestCase',
            top_level_directory=self.tmpdir,
        )
        tests = list(self.get_test_cases(suite))
        self.assertEqual(len(tests), 1)
        test, = tests
        self.assertIsInstance(test, python_unittest.TestCase)
        self.assertEqual(test._testMethodName, 'test_method')

    def test_discover_no_top_level(self):
        getcwd = Mock()
        getcwd.return_value = self.tmpdir
        with patch.object(os, 'getcwd', getcwd):
            suite = self.discoverer.discover(
                'TestCase',
            )
            getcwd.assert_called_once_with()
            tests = list(self.get_test_cases(suite))
            self.assertEqual(len(tests), 1)
            test, = tests
            self.assertIsInstance(test, python_unittest.TestCase)
            self.assertEqual(test._testMethodName, 'test_method')

    def test_discover_class_and_method(self):
        suite = self.discoverer.discover(
            'TestCase.test_method',
            top_level_directory=self.tmpdir,
        )
        tests = list(self.get_test_cases(suite))
        self.assertEqual(len(tests), 1)
        test, = tests
        self.assertIsInstance(test, python_unittest.TestCase)
        self.assertEqual(test._testMethodName, 'test_method')

    def test_discover_module_and_class_and_method(self):
        suite = self.discoverer.discover(
            'test_cases.TestCase.test_method',
            top_level_directory=self.tmpdir,
        )
        tests = list(self.get_test_cases(suite))
        self.assertEqual(len(tests), 1)
        test, = tests
        self.assertIsInstance(test, python_unittest.TestCase)
        self.assertEqual(test._testMethodName, 'test_method')

    def test_discover_module_and_class(self):
        suite = self.discoverer.discover(
            'test_cases.TestCase',
            top_level_directory=self.tmpdir,
        )
        tests = list(self.get_test_cases(suite))
        self.assertEqual(len(tests), 1)
        test, = tests
        self.assertIsInstance(test, python_unittest.TestCase)
        self.assertEqual(test._testMethodName, 'test_method')


class TestDiscovererImportError(unittest.TestCase):

    def setUp(self):
        self.modules = sys.modules.copy()
        self.tempdir = tempfile.mkdtemp(prefix='haas-tests-')
        klass = builder.Class(
            'TestSomething',
            (
                builder.Method('test_method'),
            ),
        )

        module1 = builder.Module('test_something.py', (klass,))
        module2 = builder.Module('test_something_else.py', (klass,))
        subpackage = builder.Package(
            'subpackage',
            (
                builder.Package('package1', (module1,)),
                builder.Package('package2', (module2,)),
            ),
        )
        package = builder.Package('package', (subpackage,))
        fixture = builder.Package('fixture', (package,))
        fixture.create(self.tempdir)

        module_path = os.path.join(
            self.tempdir, fixture.name, package.name, subpackage.name,
            module1.name)
        with open(module_path, 'w') as fh:
            fh.write('import haas.i_dont_exist\n')

    def tearDown(self):
        if self.tempdir in sys.path:
            sys.path.remove(self.tempdir)
        modules_to_remove = [key for key in sys.modules
                             if key not in self.modules]
        for key in modules_to_remove:
            del sys.modules[key]
        del self.modules
        shutil.rmtree(self.tempdir)

    def test_discover_creates_importerror_testcase(self):
        with cd(self.tempdir):
            suite = Discoverer(Loader()).discover(
                self.tempdir, self.tempdir)
        self.assertEqual(suite.countTestCases(), 3)
        case_names = [
            type(case).__name__ for case in find_test_cases(suite)]
        self.assertEqual(
            case_names, ['ModuleImportError', 'TestSomething',
                         'TestSomething'])

    def test_importerror_testcase(self):
        with cd(self.tempdir):
            suite = Discoverer(Loader()).discover(
                self.tempdir, self.tempdir)
        self.assertEqual(suite.countTestCases(), 3)
        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(len(result.errors), 1)


class TestDiscovererNonPackageImport(unittest.TestCase):

    def setUp(self):
        self.modules = sys.modules.copy()
        self.tempdir = tempfile.mkdtemp(prefix='haas-tests-')
        klass = builder.Class(
            'TestSomething',
            (
                builder.Method('test_method'),
            ),
        )

        module1 = builder.Module('test_something.py', (klass,))
        module2 = builder.Module('test_something_else.py', (klass,))
        subpackage = builder.Directory(
            'subpackage',
            (
                builder.Package('package1', (module1,)),
                builder.Package('package2', (module2,)),
            ),
        )
        package = builder.Directory('package', (subpackage,))
        fixture = builder.Directory('fixture', (package,))
        fixture.create(self.tempdir)

    def tearDown(self):
        if self.tempdir in sys.path:
            sys.path.remove(self.tempdir)
        modules_to_remove = [key for key in sys.modules
                             if key not in self.modules]
        for key in modules_to_remove:
            del sys.modules[key]
        del self.modules
        shutil.rmtree(self.tempdir)

    def test_discover_skips_non_packages(self):
        with cd(self.tempdir):
            suite = Discoverer(Loader()).discover(self.tempdir, self.tempdir)
        self.assertEqual(suite.countTestCases(), 0)


class TestDiscovererDotInModuleName(unittest.TestCase):

    def setUp(self):
        self.modules = sys.modules.copy()
        self.tempdir = tempfile.mkdtemp(prefix='haas-tests-')
        klass = builder.Class(
            'TestSomething',
            (
                builder.Method('test_method'),
            ),
        )
        expected_klass = builder.Class(
            'TestExpected',
            (
                builder.Method('test_expected'),
            ),
        )

        module1 = builder.Module('test_some.thing.py', (klass,))
        module2 = builder.Module('test_something_else.py', (klass,))
        module3 = builder.Module('test_another_one.py', (expected_klass,))
        subpackage = builder.Package(
            'subpackage',
            (
                builder.Package('package1', (module1,)),
                builder.Package('packa.ge2', (module2,)),
                builder.Package('package3', (module3,)),
            ),
        )
        package = builder.Package('package', (subpackage,))
        fixture = builder.Package('fixture', (package,))
        fixture.create(self.tempdir)

    def tearDown(self):
        if self.tempdir in sys.path:
            sys.path.remove(self.tempdir)
        modules_to_remove = [key for key in sys.modules
                             if key not in self.modules]
        for key in modules_to_remove:
            del sys.modules[key]
        del self.modules
        shutil.rmtree(self.tempdir)

    def test_discover_tests(self):
        # When
        with cd(self.tempdir):
            suite = Discoverer(Loader()).discover(self.tempdir, self.tempdir)

        # Then
        self.assertEqual(suite.countTestCases(), 1)
        case, = find_test_cases(suite)
        self.assertEqual(type(case).__name__, 'TestExpected')
        self.assertEqual(case._testMethodName, 'test_expected')


class TestDiscovererNeverFilterModuleImportError(unittest.TestCase):

    def setUp(self):
        self.modules = sys.modules.copy()
        self.tempdir = tempfile.mkdtemp(prefix='haas-tests-')
        text = builder.RawText('ImportError', 'import haas.i_dont_exist')
        klass = builder.Class(
            'TestSomething',
            (
                builder.Method('test_method'),
            ),
        )

        module = builder.Module('test_importerror.py', (text, klass,))
        package = builder.Package('package', (module,))
        fixture = builder.Package('fixture', (package,))
        fixture.create(self.tempdir)

    def tearDown(self):
        if self.tempdir in sys.path:
            sys.path.remove(self.tempdir)
        modules_to_remove = [key for key in sys.modules
                             if key not in self.modules]
        for key in modules_to_remove:
            del sys.modules[key]
        del self.modules
        shutil.rmtree(self.tempdir)

    def test_discover_tests(self):
        # When
        with cd(self.tempdir):
            suite = Discoverer(Loader()).discover('TestSomething', None)

        # Then
        self.assertEqual(suite.countTestCases(), 1)
        case, = find_test_cases(suite)
        self.assertIsInstance(case, ModuleImportError)
        self.assertEqual(case._testMethodName, 'test_error')


class TestDiscovererSelectiveFilterPackageImportError(unittest.TestCase):

    def setUp(self):
        self.modules = sys.modules.copy()
        self.tempdir = tempfile.mkdtemp(prefix='haas-tests-')
        text = builder.RawText('ImportError', 'from . import i_dont_exist')
        klass = builder.Class(
            'TestSomething',
            (
                builder.Method('test_method'),
            ),
        )
        module = builder.Module('test_importerror.py', (klass,))
        fixture = builder.Directory(
            'testing_package',
            (
                builder.Module('__init__.py', (text,)),
                module,
            ),
        )

        fixture.create(self.tempdir)

    def tearDown(self):
        if self.tempdir in sys.path:
            sys.path.remove(self.tempdir)
        modules_to_remove = [key for key in sys.modules
                             if key not in self.modules]
        for key in modules_to_remove:
            del sys.modules[key]
        del self.modules
        shutil.rmtree(self.tempdir)

    def test_discover_tests(self):
        # When
        with cd(self.tempdir):
            suite = Discoverer(Loader()).discover('TestSomething', None)

        # Then
        self.assertEqual(suite.countTestCases(), 1)
        case, = find_test_cases(suite)
        self.assertIsInstance(case, ModuleImportError)
        self.assertEqual(case._testMethodName, 'test_error')


class TestDiscovererFindTestsByFilePath(unittest.TestCase):

    def setUp(self):
        self.modules = sys.modules.copy()
        self.tempdir = tempfile.mkdtemp(prefix='haas-tests-')
        klass = builder.Class(
            'TestSomething',
            (
                builder.Method('test_method'),
            ),
        )

        module = builder.Module('test_something.py', (klass,))
        package = builder.Package('package', (module,))
        fixture = builder.Package('fixture', (package,))
        fixture.create(self.tempdir)

    def tearDown(self):
        if self.tempdir in sys.path:
            sys.path.remove(self.tempdir)
        modules_to_remove = [key for key in sys.modules
                             if key not in self.modules]
        for key in modules_to_remove:
            del sys.modules[key]
        del self.modules
        shutil.rmtree(self.tempdir)

    def test_discover_tests_no_prefix_dot_slash(self):
        # Given
        start = 'fixture/package/test_something.py'

        # When
        with cd(self.tempdir):
            suite = Discoverer(Loader()).discover(start, None)

        # Then
        self.assertEqual(suite.countTestCases(), 1)
        case, = find_test_cases(suite)
        self.assertEqual(type(case).__name__, 'TestSomething')
        self.assertEqual(case._testMethodName, 'test_method')

    def test_discover_tests_with_dot_slash(self):
        # Given
        start = './fixture/package/test_something.py'

        # When
        with cd(self.tempdir):
            suite = Discoverer(Loader()).discover(start, None)

        # Then
        self.assertEqual(suite.countTestCases(), 1)
        case, = find_test_cases(suite)
        self.assertEqual(type(case).__name__, 'TestSomething')
        self.assertEqual(case._testMethodName, 'test_method')


class TestDiscovererEmacsRecoveryFiles(unittest.TestCase):

    def setUp(self):
        self.modules = sys.modules.copy()
        self.tempdir = tempfile.mkdtemp(prefix='haas-tests-')
        klass = builder.Class(
            'TestSomething',
            (
                builder.Method('test_method'),
            ),
        )
        module = builder.Module('.#test_module.py', (klass,))
        module = builder.Module('test_module.py', (klass,))
        fixture = builder.Package(
            'testing_package',
            (
                module,
            ),
        )

        fixture.create(self.tempdir)

    def tearDown(self):
        if self.tempdir in sys.path:
            sys.path.remove(self.tempdir)
        modules_to_remove = [key for key in sys.modules
                             if key not in self.modules]
        for key in modules_to_remove:
            del sys.modules[key]
        del self.modules
        shutil.rmtree(self.tempdir)

    def test_discover_error_emacs_recovery_file(self):
        # When
        with cd(self.tempdir):
            suite = Discoverer(Loader()).discover('TestSomething', None)

        # Then
        self.assertEqual(suite.countTestCases(), 1)
        case, = find_test_cases(suite)
        self.assertIsInstance(case, unittest.TestCase)
        self.assertEqual(case._testMethodName, 'test_method')


class TestDiscovererExceptionOnModuleImport(unittest.TestCase):

    def setUp(self):
        self.modules = sys.modules.copy()
        self.tempdir = tempfile.mkdtemp(prefix='haas-tests-')
        text = builder.RawText('RuntimeError', 'raise RuntimeError("failed")')
        klass = builder.Class(
            'TestSomething',
            (
                builder.Method('test_method'),
            ),
        )
        module = builder.Module('test_importerror.py', (text, klass,))
        fixture = builder.Package(
            'testing_package',
            (
                module,
            ),
        )

        fixture.create(self.tempdir)

    def tearDown(self):
        if self.tempdir in sys.path:
            sys.path.remove(self.tempdir)
        modules_to_remove = [key for key in sys.modules
                             if key not in self.modules]
        for key in modules_to_remove:
            del sys.modules[key]
        del self.modules
        shutil.rmtree(self.tempdir)

    def test_discover_tests_runtime_error_on_import(self):
        # When
        with cd(self.tempdir):
            suite = Discoverer(Loader()).discover('TestSomething', None)

        # Then
        self.assertEqual(suite.countTestCases(), 1)
        case, = find_test_cases(suite)
        self.assertIsInstance(case, ModuleImportError)
        self.assertEqual(case._testMethodName, 'test_error')
