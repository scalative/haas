# Copyright 2013-2014 Simon Jagoe
from __future__ import unicode_literals

import os
import sys

from fnmatch import fnmatch
import unittest


def get_relpath(top_level_directory, fullpath):
    normalized = os.path.normpath(fullpath)
    relpath = os.path.relpath(normalized, top_level_directory)
    if os.path.isabs(relpath) or relpath.startswith('..'):
        raise ValueError('Path not within project: {0}'.format(fullpath))
    return relpath


def find_top_level_directory(start_directory):
    top_level = start_directory
    while os.path.isfile(os.path.join(top_level, '__init__.py')):
        top_level = os.path.dirname(top_level)
        if top_level == os.path.dirname(top_level):
            raise ValueError("Can't find top level directory")
    return os.path.abspath(top_level)


def match_path(filename, filepath, pattern):
    return fnmatch(filename, pattern)


def get_module_name(top_level_directory, filepath):
    modulepath = os.path.splitext(os.path.normpath(filepath))[0]
    relpath = get_relpath(top_level_directory, modulepath)
    return relpath.replace(os.path.sep, '.')


def get_module_by_name(name):
    __import__(name)
    return sys.modules[name]


def assert_start_importable(top_level_directory, start_directory):
    relpath = get_relpath(top_level_directory, start_directory)
    path = top_level_directory
    for component in relpath.split(os.path.sep):
        if component == '.':
            continue
        path = os.path.join(path, component)
        if path != top_level_directory and \
                not os.path.isfile(os.path.join(path, '__init__.py')):
            raise ImportError('Start directory is not importable')


class Loader(object):

    def __init__(self, test_suite_class=None, test_method_prefix='test',
                 **kwargs):
        super(Loader, self).__init__(**kwargs)
        self.test_method_prefix = test_method_prefix
        if test_suite_class is None:
            test_suite_class = unittest.TestSuite
        self.test_suite_class = test_suite_class

    def find_test_method_names(self, testcase):
        """Return a list of test method names in the provided ``TestCase``
        subclass.

        Parameters
        ----------
        testcase : type
            Subclass of :class:`unittest.TestCase`

        """
        names = [name for name in dir(testcase)
                 if name.startswith(self.test_method_prefix)
                 and hasattr(getattr(testcase, name), '__call__')]
        return names

    def load_test(self, testcase, method_name):
        """Create and return an instance of :class:`unittest.TestCase` for the
        specified unbound test method.

        Parameters
        ----------
        unbound_test : unbound method
            An unbound method of a :class:`unittest.TestCase`

        """
        if not issubclass(testcase, unittest.TestCase):
            raise TypeError(
                'Test case must be a subclass of unittest.TestCase')
        return testcase(methodName=method_name)

    def load_case(self, testcase):
        """Load a TestSuite containing all TestCase instances for all tests in
        a TestCase subclass.

        Parameters
        ----------
        testcase : type
            A subclass of :class:`unittest.TestCase`

        """
        tests = [self.load_test(testcase, name)
                 for name in self.find_test_method_names(testcase)]
        return self.test_suite_class(tests)

    def get_test_cases_from_module(self, module):
        """Return a list of TestCase subclasses contained in the provided
        module object.

        Parameters
        ----------
        module : module
            A module object containing ``TestCases``

        """
        module_items = (getattr(module, name) for name in dir(module))
        return [item for item in module_items
                if isinstance(item, type)
                and issubclass(item, unittest.TestCase)]

    def load_module(self, module):
        """Create and return a test suite containing all cases loaded from the
        provided module.

        Parameters
        ----------
        module : module
            A module object containing ``TestCases``

        """
        cases = self.get_test_cases_from_module(module)
        suites = [self.load_case(case) for case in cases]
        return self.test_suite_class(suites)

    def discover(self, start_directory, top_level_directory=None,
                 pattern='test*.py'):
        if os.path.isdir(start_directory):
            return self.discover_by_directory(
                start_directory, top_level_directory=top_level_directory,
                 pattern=pattern)

    def discover_by_directory(self, start_directory, top_level_directory=None,
                              pattern='test*.py'):
        start_directory = os.path.abspath(start_directory)
        if top_level_directory is None:
            top_level_directory = find_top_level_directory(
                start_directory)

        assert_start_importable(top_level_directory, start_directory)

        if top_level_directory not in sys.path:
            sys.path.insert(0, top_level_directory)
        tests = self._discover_tests(
            start_directory, top_level_directory, pattern)
        return self.test_suite_class(list(tests))

    def _discover_tests(self, start_directory, top_level_directory, pattern):
        for curdir, dirnames, filenames in os.walk(start_directory):
            for filename in filenames:
                filepath = os.path.join(curdir, filename)
                if not match_path(filename, filepath, pattern):
                    continue
                module_name = get_module_name(top_level_directory, filepath)
                yield self.load_module(get_module_by_name(module_name))
