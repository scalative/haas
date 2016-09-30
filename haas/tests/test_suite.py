# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from contextlib import contextmanager
from itertools import count
import sys

from ._test_cases import TestCase
from ..result import ResultCollector
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
    setup_count = 0
    teardown_count = 0

    def __init__(self):
        self.was_run = False

    @classmethod
    def reset(cls):
        cls.setup = False
        cls.teardown = False
        cls.setup_raise = False
        cls.teardown_raise = False
        cls.setup_count = 0
        cls.teardown_count = 0
        if hasattr(cls, '__unittest_skip__'):
            del cls.__unittest_skip__

    def run(self, result, _state=None):
        self.was_run = True
        return result

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)


class MockTestCaseSetup(MockTestCase):

    @classmethod
    def setUpClass(cls):
        cls.setup = True
        cls.setup_count += 1
        if cls.setup_raise:
            raise Exception('Error in setUpClass')


class MockTestCaseTeardown(MockTestCase):

    @classmethod
    def tearDownClass(cls):
        cls.teardown = True
        cls.teardown_count += 1
        if cls.setup_raise:
            raise Exception('Error in tearDownClass')


class MockTestCaseSetupTeardown(MockTestCaseSetup, MockTestCaseTeardown):
    pass


class ResetClassStateMixin(object):

    def setUp(self):
        for klass in (MockTestCase, MockTestCaseSetup,
                      MockTestCaseTeardown, MockTestCaseSetupTeardown):
            klass.reset()
        self.assertStateReset()

    def tearDown(self):
        for klass in (MockTestCase, MockTestCaseSetup,
                      MockTestCaseTeardown, MockTestCaseSetupTeardown):
            klass.reset()
        self.assertStateReset()

    def assertStateReset(self):
        for klass in (MockTestCase, MockTestCaseSetup,
                      MockTestCaseTeardown, MockTestCaseSetupTeardown):
            self.assertFalse(klass.setup)
            self.assertFalse(klass.teardown)
            self.assertFalse(klass.setup_raise)
            self.assertFalse(klass.teardown_raise)
            self.assertFalse(hasattr(klass, '__unittest_skip__'))


class TestTestSuiteState(ResetClassStateMixin, unittest.TestCase):

    def setUp(self):
        self.state = _TestSuiteState(ResultCollector())
        self._name_count = count(0)
        ResetClassStateMixin.setUp(self)

    def tearDown(self):
        ResetClassStateMixin.tearDown(self)
        del self.state

    def test_setup_none(self):
        self.assertTrue(self.state.setup(None))

    def test_teardown_no_prior_setup_does_not_raise(self):
        self.state.teardown()

    @contextmanager
    def _temporary_module(self, klass, module):
        module_name = 'haas_test_module_{0}'.format(next(self._name_count))
        self.assertNotIn(module_name, sys.modules)
        sys.modules[module_name] = module
        old_module = klass.__module__
        klass.__module__ = module_name

        try:
            yield
        finally:
            klass.__module__ = old_module
            del sys.modules[module_name]

    def _prepare_test(self, klass, module_factory, setup_raise,
                      teardown_raise):
        klass.setup_raise = setup_raise
        klass.teardown_raise = teardown_raise
        test = klass()
        if module_factory is not None:
            module = module_factory(
                setup_raise=setup_raise,
                teardown_raise=teardown_raise,
            )
        else:
            module = None
        return test, module

    @contextmanager
    def _run_test_context(self, klass, module_factory, setup_raise,
                          teardown_raise, class_setup, class_teardown,
                          module_setup, module_teardown):
        test, module = self._prepare_test(
            klass, module_factory, setup_raise, teardown_raise)

        with self._temporary_module(klass, module):
            self.assertEqual(self.state.setup(test), not setup_raise)
            self.assertEqual(klass.setup, class_setup)
            self.assertFalse(klass.teardown)
            if module is not None:
                self.assertEqual(module.setup, module_setup)
                self.assertFalse(module.teardown)

            yield test

            self.state.teardown()
            self.assertEqual(klass.setup, class_setup)
            self.assertEqual(klass.teardown, class_teardown)
            if module is not None:
                self.assertEqual(module.setup, module_setup)
                self.assertEqual(module.teardown, module_teardown)

    def _run_test(self, klass, module_factory, setup_raise, teardown_raise,
                  class_setup, class_teardown, module_setup, module_teardown):
        with self._run_test_context(
                klass, module_factory, setup_raise, teardown_raise,
                class_setup, class_teardown, module_setup, module_teardown):
            pass

    def test_call_setup_without_setup_or_teardown(self):
        self._run_test(
            klass=MockTestCase,
            module_factory=MockModule,
            setup_raise=False,
            teardown_raise=False,
            class_setup=False,
            class_teardown=False,
            module_setup=False,
            module_teardown=False,
        )

    def test_setup_skip(self):
        MockTestCaseSetupTeardown.__unittest_skip__ = True
        self._run_test(
            klass=MockTestCaseSetupTeardown,
            module_factory=MockModule,
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
            module_factory=MockModule,
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
            module_factory=MockModule,
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
            module_factory=MockModule,
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
            module_factory=MockModule,
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
            module_factory=MockModule,
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
            module_factory=MockModuleSetup,
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
            module_factory=MockModuleTeardown,
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
            module_factory=MockModuleSetupTeardown,
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
            module_factory=MockModuleSetupTeardown,
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
            module_factory=MockModuleSetupTeardown,
            setup_raise=False,
            teardown_raise=True,
            class_setup=False,
            class_teardown=False,
            module_setup=True,
            module_teardown=True,
        )

    def test_setup_module_none(self):
        self._run_test(
            klass=MockTestCase,
            module_factory=None,
            setup_raise=False,
            teardown_raise=False,
            class_setup=False,
            class_teardown=False,
            module_setup=False,
            module_teardown=False,
        )

    def test_multiple_setup_teardown_different_class_module(self):
        with self._run_test_context(
                klass=MockTestCaseSetupTeardown,
                module_factory=MockModuleSetupTeardown,
                setup_raise=False,
                teardown_raise=False,
                class_setup=True,
                class_teardown=True,
                module_setup=True,
                module_teardown=True):

            klass = MockTestCaseSetup
            module_factory = MockModuleSetup
            setup_raise = False
            teardown_raise = False
            test, module = self._prepare_test(
                klass=klass,
                module_factory=module_factory,
                setup_raise=setup_raise,
                teardown_raise=teardown_raise,
            )
            with self._temporary_module(klass, module):
                self.assertEqual(self.state.setup(test), not setup_raise)
                self.assertTrue(klass.setup)
                self.assertFalse(klass.teardown)
                self.assertTrue(module.setup)
                self.assertFalse(module.teardown)

        # Top-level tear down has occurred
        self.assertTrue(klass.setup)
        self.assertFalse(klass.teardown)
        self.assertTrue(module.setup)
        self.assertFalse(module.teardown)

    def test_multiple_setup_teardown_same_class_module(self):
        with self._run_test_context(
                klass=MockTestCaseSetupTeardown,
                module_factory=MockModuleSetupTeardown,
                setup_raise=False,
                teardown_raise=False,
                class_setup=True,
                class_teardown=True,
                module_setup=True,
                module_teardown=True) as first_test:

            klass = MockTestCaseSetupTeardown
            setup_raise = False
            teardown_raise = False
            test, _ = self._prepare_test(
                klass=klass,
                module_factory=None,
                setup_raise=setup_raise,
                teardown_raise=teardown_raise,
            )
            module_name = first_test.__class__.__module__
            module = sys.modules[module_name]

            self.assertEqual(self.state.setup(test), not setup_raise)
            self.assertTrue(klass.setup)
            self.assertFalse(klass.teardown)
            self.assertTrue(module.setup)
            self.assertFalse(module.teardown)

        # Top-level tear down has occurred
        self.assertTrue(klass.setup)
        self.assertTrue(klass.teardown)
        self.assertTrue(module.setup)
        self.assertTrue(module.teardown)


class TestTestSuiteCount(unittest.TestCase):

    def test_count_empty(self):
        suite = TestSuite()
        self.assertEqual(suite.countTestCases(), 0)

    def test_one_level(self):
        suite = TestSuite(tests=[TestCase('test_method'), TestSuite()])
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
                        TestCase('test_method'),
                        TestSuite(),
                        TestSuite(),
                    ],
                ),
                TestCase('test_method'),
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
                        TestCase('test_method'),
                        TestSuite(),
                        TestSuite(),
                    ],
                ),
                TestCase('test_method'),
                TestSuite(),
            ],
        )
        self.assertEqual(suite, suite)

    def test_equal_to_other_nested(self):
        suite = TestSuite(
            tests=[
                TestSuite(
                    tests=[
                        TestCase('test_method'),
                        TestSuite(),
                        TestSuite(),
                    ],
                ),
                TestCase('test_method'),
                TestSuite(),
            ],
        )
        suite2 = TestSuite(
            tests=[
                TestSuite(
                    tests=[
                        TestCase('test_method'),
                        TestSuite(),
                        TestSuite(),
                    ],
                ),
                TestCase('test_method'),
                TestSuite(),
            ],
        )
        self.assertEqual(suite, suite2)


class TestRunningTestSuite(ResetClassStateMixin, unittest.TestCase):

    def setUp(self):
        ResetClassStateMixin.setUp(self)
        self.case_1 = MockTestCaseSetupTeardown()
        self.case_2 = MockTestCase()
        self.suite = TestSuite(
            tests=[
                TestSuite(
                    tests=[
                        self.case_1,
                        TestSuite(),
                        TestSuite(),
                    ],
                ),
                self.case_2,
                TestSuite(),
            ],
        )

    def tearDown(self):
        del self.suite
        del self.case_1
        del self.case_2
        ResetClassStateMixin.tearDown(self)

    def test_run_suite_run(self):
        result = ResultCollector()
        returned_result = self.suite.run(result)
        self.assertIs(result, returned_result)
        self.assertTrue(self.case_1.was_run)
        self.assertTrue(self.case_2.was_run)

    def test_run_suite_call(self):
        result = ResultCollector()
        returned_result = self.suite(result)
        self.assertIs(result, returned_result)
        self.assertTrue(self.case_1.was_run)
        self.assertTrue(self.case_2.was_run)

    def test_run_suite_setup_error(self):
        self.case_1.__class__.setup_raise = True
        result = ResultCollector()
        returned_result = self.suite.run(result)
        self.assertIs(result, returned_result)
        self.assertFalse(self.case_1.was_run)
        self.assertTrue(self.case_2.was_run)

    def test_same_class_multiple_suites(self):
        case_1 = MockTestCaseSetupTeardown()
        case_2 = MockTestCaseSetupTeardown()
        suite = TestSuite(
            tests=[
                TestSuite(
                    tests=[
                        case_1,
                    ],
                ),
                TestSuite(
                    tests=[
                        case_2,
                    ],
                ),
            ],
        )
        result = ResultCollector()
        suite.run(result)
        self.assertEqual(MockTestCaseSetupTeardown.setup_count, 1)
        self.assertEqual(MockTestCaseSetupTeardown.teardown_count, 1)
