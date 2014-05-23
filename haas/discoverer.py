# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from fnmatch import fnmatch
import logging
import os
import sys

from .utils import get_module_by_name

logger = logging.getLogger(__name__)


def get_relpath(top_level_directory, fullpath):
    normalized = os.path.normpath(fullpath)
    relpath = os.path.relpath(normalized, top_level_directory)
    if os.path.isabs(relpath) or relpath.startswith('..'):
        raise ValueError('Path not within project: {0}'.format(fullpath))
    return relpath


def match_path(filename, filepath, pattern):
    return fnmatch(filename, pattern)


def get_module_name(top_level_directory, filepath):
    modulepath = os.path.splitext(os.path.normpath(filepath))[0]
    relpath = get_relpath(top_level_directory, modulepath)
    return relpath.replace(os.path.sep, '.')


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


def find_module_by_name(full_name):
    module_name = full_name
    module_attributes = []
    while True:
        try:
            module = get_module_by_name(module_name)
        except ImportError:
            if '.' in module_name:
                module_name, attribute = module_name.rsplit('.', 1)
                module_attributes.append(attribute)
            else:
                raise
        else:
            break
    return module, list(reversed(module_attributes))


def find_top_level_directory(start_directory):
    """Finds the top-level directory of a project given a start directory
    inside the project.

    Parameters
    ----------
    start_directory : str
        The directory in which test discovery will start.

    """
    top_level = start_directory
    while os.path.isfile(os.path.join(top_level, '__init__.py')):
        top_level = os.path.dirname(top_level)
        if top_level == os.path.dirname(top_level):
            raise ValueError("Can't find top level directory")
    return os.path.abspath(top_level)


def find_test_cases(suite):
    """Generate a list of all test cases contained in a test suite.

    Parameters
    ----------
    suite : haas.suite.TestSuite
        The test suite from which to generate the test case list.

    """
    try:
        iter(suite)
    except TypeError:
        yield suite
    else:
        for test in suite:
            for test_ in find_test_cases(test):
                yield test_


def filter_test_suite(suite, filter_name):
    """Filter test cases in a test suite by a substring in the full dotted
    test name.

    Parameters
    ----------
    suite : haas.suite.TestSuite
        The test suite containing tests to be filtered.
    filter_name : str
        The substring of the full dotted name on which to filter.  This
        should not contain a leading or trailing dot.

    """
    filtered_cases = []
    for test in find_test_cases(suite):
        type_ = type(test)
        name = '{0}.{1}.{2}'.format(
            type_.__module__, type_.__name__, test._testMethodName)
        filter_internal = '.{0}.'.format(filter_name)
        if filter_internal in name or name.endswith(filter_internal[:-1]):
            filtered_cases.append(test)
    return filtered_cases


class Discoverer(object):
    """The ``Discoverer`` is responsible for finding tests that can be
    loaded by a :class:`~haas.loader.Loader`.

    """

    def __init__(self, loader, **kwargs):
        super(Discoverer, self).__init__(**kwargs)
        self._loader = loader

    def discover(self, start, top_level_directory=None, pattern='test*.py'):
        """Do test case discovery.

        This is the top-level entry-point for test discovery.

        If the ``start`` argument is a drectory, then ``haas`` will
        discover all tests in the package contained in that directory.

        If the ``start`` argument is not a directory, it is assumed to
        be a package or module name and tests in the package or module
        are loaded.

        FIXME: This needs a better description.

        Parameters
        ----------
        start : str
            The directory, package, module, class or test to load.
        top_level_directory : str
            The path to the top-level directoy of the project.  This is
            the parent directory of the project'stop-level Python
            package.
        pattern : str
            The glob pattern to match the filenames of modules to search
            for tests.

        """
        logger.debug('Starting test discovery')
        if os.path.isdir(start):
            start_directory = start
            return self.discover_by_directory(
                start_directory, top_level_directory=top_level_directory,
                pattern=pattern)
        else:
            package_or_module = start
            return self.discover_by_module(
                package_or_module, top_level_directory=top_level_directory,
                pattern=pattern)

    def discover_by_module(self, module_name, top_level_directory=None,
                           pattern='test*.py'):
        """Find all tests in a package or module, or load a single test case if
        a class or test inside a module was specified.

        Parameters
        ----------
        module_name : str
            The dotted package name, module name or TestCase class and
            test method.
        top_level_directory : str
            The path to the top-level directoy of the project.  This is
            the parent directory of the project'stop-level Python
            package.
        pattern : str
            The glob pattern to match the filenames of modules to search
            for tests.

        """
        # If the top level directory is given, the module may only be
        # importable with that in the path.
        if top_level_directory is not None and \
                top_level_directory not in sys.path:
            sys.path.insert(0, top_level_directory)

        logger.debug('Discovering tests by module: module_name=%r, '
                     'top_level_directory=%r, pattern=%r', module_name,
                     top_level_directory, pattern)

        try:
            module, case_attributes = find_module_by_name(module_name)
        except ImportError:
            return self.discover_filtered_tests(
                module_name, top_level_directory=top_level_directory,
                pattern=pattern)
        dirname, basename = os.path.split(module.__file__)
        basename = os.path.splitext(basename)[0]
        if len(case_attributes) == 0 and basename == '__init__':
            # Discover in a package
            return self.discover_by_directory(
                dirname, top_level_directory, pattern=pattern)
        elif len(case_attributes) == 0:
            # Discover all in a module
            return self._loader.load_module(module)

        return self.discover_single_case(module, case_attributes)

    def discover_single_case(self, module, case_attributes):
        """Find and load a single TestCase or TestCase method from a module.

        Parameters
        ----------
        module : module
            The imported Python module containing the TestCase to be
            loaded.
        case_attributes : list of str
            A list of length 1 or 2.  The first component must be the
            name of a TestCase subclass.  The second component must be
            the name of a method in the TestCase.

        """
        # Find single case
        case = module
        loader = self._loader
        for index, component in enumerate(case_attributes):
            case = getattr(case, component, None)
            if case is None:
                return loader.create_suite()
            elif loader.is_test_case(case):
                rest = case_attributes[index + 1:]
                if len(rest) > 1:
                    raise ValueError('Too many components in module path')
                elif len(rest) == 1:
                    return loader.create_suite(
                        [loader.load_test(case, *rest)])
                return loader.load_case(case)

        # No cases matched, return empty suite
        return loader.create_suite()

    def discover_by_directory(self, start_directory, top_level_directory=None,
                              pattern='test*.py'):
        """Run test discovery in a directory.

        Parameters
        ----------
        start_directory : str
            The package directory in which to start test discovery.
        top_level_directory : str
            The path to the top-level directoy of the project.  This is
            the parent directory of the project'stop-level Python
            package.
        pattern : str
            The glob pattern to match the filenames of modules to search
            for tests.

        """
        start_directory = os.path.abspath(start_directory)
        if top_level_directory is None:
            top_level_directory = find_top_level_directory(
                start_directory)
        logger.debug('Discovering tests in directory: start_directory=%r, '
                     'top_level_directory=%r, pattern=%r', start_directory,
                     top_level_directory, pattern)

        assert_start_importable(top_level_directory, start_directory)

        if top_level_directory not in sys.path:
            sys.path.insert(0, top_level_directory)
        tests = self._discover_tests(
            start_directory, top_level_directory, pattern)
        return self._loader.create_suite(list(tests))

    def _discover_tests(self, start_directory, top_level_directory, pattern):
        load_module = self._loader.load_module
        for curdir, dirnames, filenames in os.walk(start_directory):
            logger.debug('Discovering tests in %r', curdir)
            for filename in filenames:
                filepath = os.path.join(curdir, filename)
                if not match_path(filename, filepath, pattern):
                    logger.debug('Skipping %r', filepath)
                    continue
                module_name = get_module_name(top_level_directory, filepath)
                logger.debug('Loading tests from %r', module_name)
                yield load_module(get_module_by_name(module_name))

    def discover_filtered_tests(self, filter_name, top_level_directory=None,
                                pattern='test*.py'):
        """Find all tests whose package, module, class or method names match
        the ``filter_name`` string.

        Parameters
        ----------
        filter_name : str
            A subsection of the full dotted test name.  This can be
            simply a test method name (e.g. ``test_some_method``), the
            TestCase class name (e.g. ``TestMyClass``), a module name
            (e.g. ``test_module``), a subpackage (e.g. ``tests``).  It
            may also be a dotted combination of the above
            (e.g. ``TestMyClass.test_some_method``).
        top_level_directory : str
            The path to the top-level directoy of the project.  This is
            the parent directory of the project'stop-level Python
            package.
        pattern : str
            The glob pattern to match the filenames of modules to search
            for tests.

        """
        if top_level_directory is None:
            top_level_directory = find_top_level_directory(
                os.getcwd())

        logger.debug('Discovering filtered tests: filter_name=%r, '
                     'top_level_directory=%r, pattern=%r', top_level_directory,
                     top_level_directory, pattern)

        suite = self.discover_by_directory(
            top_level_directory, top_level_directory=top_level_directory,
            pattern=pattern)

        return self._loader.create_suite(
            filter_test_suite(suite, filter_name=filter_name))
