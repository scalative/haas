# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

import unittest

from .suite import TestSuite


class Loader(object):
    """Load individual test cases from modules and wrap them in the
    :class:`~haas.suite.Suite` container.

    """

    def __init__(self, test_suite_class=None, test_case_class=None,
                 test_method_prefix='test',
                 **kwargs):
        super(Loader, self).__init__(**kwargs)
        self._test_method_prefix = test_method_prefix

        if test_suite_class is None:
            test_suite_class = TestSuite
        self._test_suite_class = test_suite_class

        if test_case_class is None:
            test_case_class = unittest.TestCase
        self._test_case_class = test_case_class

    def create_suite(self, tests=()):
        """Create a test suite using the confugured test suite class.

        Parameters
        ----------
        tests : sequence
            Sequence of TestCase instances.

        """
        return self._test_suite_class(tests)

    def is_test_case(self, klass):
        """Check if a class is a TestCase.

        """
        return issubclass(klass, self._test_case_class)

    def find_test_method_names(self, testcase):
        """Return a list of test method names in the provided ``TestCase``
        subclass.

        Parameters
        ----------
        testcase : type
            Subclass of :class:`unittest.TestCase`

        """
        prefix = self._test_method_prefix
        names = [name for name in dir(testcase)
                 if name.startswith(prefix) and
                 hasattr(getattr(testcase, name), '__call__')]
        return names

    def load_test(self, testcase, method_name):
        """Create and return an instance of :class:`unittest.TestCase` for the
        specified unbound test method.

        Parameters
        ----------
        unbound_test : unbound method
            An unbound method of a :class:`unittest.TestCase`

        """
        if not self.is_test_case(testcase):
            raise TypeError(
                'Test case must be a subclass of '
                '{0.__module__}.{0.__name__}'.format(self._test_case_class))
        return testcase(method_name)

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
        return self.create_suite(tests)

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
                and self.is_test_case(item)]

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
        return self.create_suite(suites)
