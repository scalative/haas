# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import unicode_literals

from contextlib import contextmanager
import sys

from ..suite import TestSuite, _TestSuiteState
from ..testing import unittest


class MockModule(object):

    def __init__(self, setup_raise=False, teardown_raise=False):
        self.setup = False
        self.teardown = False
        self.setup_raise = setup_raise
        self.teardown_raise = teardown_raise


class MockModuleSetup(MockModule):

    def setUpModule(self):
        self.setup = True
        if self.setup_raise:
            raise Exception('Error in setUpModule')


class MockModuleTeardown(MockModule):

    def tearDownModule(self):
        self.teardown = True
        if self.teardown_raise:
            raise Exception('Error in tearDownModule')


class MockModuleSetupTeardown(MockModuleSetup, MockModuleTeardown):
    pass


class MockTestCase(object):

    setup = False
    teardown = False
    setup_raise = False
    teardown_raise = False

    @classmethod
    def reset(cls):
        cls.setup = False
        cls.teardown = False
        cls.setup_raise = False
        cls.teardown_raise = False

    def run(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)


class MockTestCaseSetup(MockTestCase):

    @classmethod
    def setUpClass(cls):
        cls.setup = True
        if cls.setup_raise:
            raise Exception('Error in setUpClass')


class MockTestCaseTeardown(MockTestCase):

    @classmethod
    def tearDownClass(cls):
        cls.teardown = True
        if cls.setup_raise:
            raise Exception('Error in tearDownClass')


class MockTestCaseSetupTeardown(MockTestCaseSetup, MockTestCaseTeardown):
    pass


class TestTestSuiteState(unittest.TestCase):

    def setUp(self):
        self.state = _TestSuiteState(unittest.TestResult())
        for klass in (MockTestCase, MockTestCaseSetup,
                      MockTestCaseTeardown, MockTestCaseSetupTeardown):
            klass.reset()
        self.assertStateReset()

    def tearDown(self):
        for klass in (MockTestCase, MockTestCaseSetup,
                      MockTestCaseTeardown, MockTestCaseSetupTeardown):
            klass.reset()
        self.assertStateReset()
        del self.state

    def assertStateReset(self):
        for klass in (MockTestCase, MockTestCaseSetup,
                      MockTestCaseTeardown, MockTestCaseSetupTeardown):
            self.assertFalse(klass.setup)
            self.assertFalse(klass.teardown)
            self.assertFalse(klass.setup_raise)
            self.assertFalse(klass.teardown_raise)

    def test_setup_none(self):
        self.assertTrue(self.state.setup(None))

    def test_teardown_no_prior_setup_does_not_raise(self):
        self.state.teardown()

    @contextmanager
    def _temporary_module(self, klass, module):
        module_name = 'haas_test_module_name'
        self.assertNotIn(module_name, sys.modules)
        sys.modules[module_name] = module
        old_module = klass.__module__
        klass.__module__ = module_name

        try:
            yield
        finally:
            klass.__module__ = old_module
            del sys.modules[module_name]

    def _run_test(self, klass, module, setup_raise, teardown_raise,
                  class_setup, class_teardown, module_setup, module_teardown):
        klass.setup_raise = setup_raise
        klass.teardown_raise = teardown_raise
        test = klass()
        module = module(
            setup_raise=setup_raise,
            teardown_raise=teardown_raise,
        )

        with self._temporary_module(klass, module):
            self.assertEqual(self.state.setup(test), not setup_raise)
            self.assertEqual(klass.setup, class_setup)
            self.assertEqual(module.setup, module_setup)
            self.assertFalse(klass.teardown)
            self.assertFalse(module.teardown)

            self.state.teardown()
            self.assertEqual(klass.setup, class_setup)
            self.assertEqual(module.setup, module_setup)
            self.assertEqual(klass.teardown, class_teardown)
            self.assertEqual(module.teardown, module_teardown)

    def test_call_setup_without_setup_or_teardown(self):
        self._run_test(
            klass=MockTestCase,
            module=MockModule,
            setup_raise=False,
            teardown_raise=False,
            class_setup=False,
            class_teardown=False,
            module_setup=False,
            module_teardown=False,
        )

    def test_setup_case_setup(self):
        self._run_test(
            klass=MockTestCaseSetup,
            module=MockModule,
            setup_raise=False,
            teardown_raise=False,
            class_setup=True,
            class_teardown=False,
            module_setup=False,
            module_teardown=False,
        )

    def test_setup_case_teardown(self):
        self._run_test(
            klass=MockTestCaseTeardown,
            module=MockModule,
            setup_raise=False,
            teardown_raise=False,
            class_setup=False,
            class_teardown=True,
            module_setup=False,
            module_teardown=False,
        )

    def test_setup_case_setup_and_teardown(self):
        self._run_test(
            klass=MockTestCaseSetupTeardown,
            module=MockModule,
            setup_raise=False,
            teardown_raise=False,
            class_setup=True,
            class_teardown=True,
            module_setup=False,
            module_teardown=False,
        )

    def test_setup_case_setup_raises_and_teardown(self):
        self._run_test(
            klass=MockTestCaseSetupTeardown,
            module=MockModule,
            setup_raise=True,
            teardown_raise=False,
            class_setup=True,
            class_teardown=False,
            module_setup=False,
            module_teardown=False,
        )

    def test_setup_case_setup_and_teardown_raises(self):
        self._run_test(
            klass=MockTestCaseSetupTeardown,
            module=MockModule,
            setup_raise=False,
            teardown_raise=True,
            class_setup=True,
            class_teardown=True,
            module_setup=False,
            module_teardown=False,
        )

    def test_setup_module_setup(self):
        self._run_test(
            klass=MockTestCase,
            module=MockModuleSetup,
            setup_raise=False,
            teardown_raise=False,
            class_setup=False,
            class_teardown=False,
            module_setup=True,
            module_teardown=False,
        )

    def test_setup_module_teardown(self):
        self._run_test(
            klass=MockTestCase,
            module=MockModuleTeardown,
            setup_raise=False,
            teardown_raise=False,
            class_setup=False,
            class_teardown=False,
            module_setup=False,
            module_teardown=True,
        )

    def test_setup_module_setup_and_teardown(self):
        self._run_test(
            klass=MockTestCase,
            module=MockModuleSetupTeardown,
            setup_raise=False,
            teardown_raise=False,
            class_setup=False,
            class_teardown=False,
            module_setup=True,
            module_teardown=True,
        )

    def test_setup_module_setup_raises_and_teardown(self):
        self._run_test(
            klass=MockTestCase,
            module=MockModuleSetupTeardown,
            setup_raise=True,
            teardown_raise=False,
            class_setup=False,
            class_teardown=False,
            module_setup=True,
            module_teardown=False,
        )

    def test_setup_module_setup_and_teardown_raises(self):
        self._run_test(
            klass=MockTestCase,
            module=MockModuleSetupTeardown,
            setup_raise=False,
            teardown_raise=True,
            class_setup=False,
            class_teardown=False,
            module_setup=True,
            module_teardown=True,
        )


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
