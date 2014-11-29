# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

import logging
import sys
from .error_holder import ErrorHolder

logger = logging.getLogger(__name__)


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


class _TestSuiteState(object):

    def __init__(self, result):
        self._result = result
        self._previous_class = None
        self._module_setup_failed = False
        self._class_setup_failed = False

    def _run_setup(self, item, setup_name, error_name):
        setup = getattr(item, setup_name, lambda: None)
        try:
            setup()
        except Exception:
            error = '{0} ({1})'.format(setup_name, error_name)
            self._result.addError(ErrorHolder(error), sys.exc_info())
            return False
        return True

    def _setup_module(self, module_name):
        if self._previous_class is not None:
            previous_module = self._previous_class.__module__
            if previous_module == module_name:
                return
            self._teardown_module(previous_module)

        module = sys.modules.get(module_name)
        if module is None:
            return

        logger.debug('Set up module: %r', module_name)
        self._module_setup_failed = not self._run_setup(
            module, 'setUpModule', module_name)

    def _setup_class(self, current_class):
        previous_class = self._previous_class
        if previous_class == current_class:
            logger.debug('Class has not changed; not setting up class %r',
                         current_class)
            return
        if self._module_setup_failed:
            logger.debug('Module setup failed; not setting up class %r',
                         previous_class)
            return
        if getattr(current_class, '__unittest_skip__', False):
            logger.debug('Class skipped; not setting up class %r',
                         current_class)
            return

        logger.debug('Set up class: %r', current_class)
        self._class_setup_failed = not self._run_setup(
            current_class, 'setUpClass', current_class.__name__)

    def setup(self, test):
        if isinstance(test, TestSuite):
            return True
        logger.debug('Setup module and class for %r', test)
        current_class = test.__class__
        module = current_class.__module__
        self._teardown_previous_class(current_class)
        self._setup_module(module)
        self._setup_class(current_class)

        self._previous_class = current_class

        return not (self._class_setup_failed or self._module_setup_failed)

    def _teardown_previous_class(self, current_class):
        previous_class = self._previous_class
        if previous_class is None:
            logger.debug('No previous class to tear down')
            return
        if current_class == self._previous_class:
            logger.debug('Class has not changed; not tearing down class %r',
                         previous_class)
            return
        if self._class_setup_failed:
            logger.debug(
                'Previous class setup failed; not tearing down class %r',
                previous_class)
            self._class_setup_failed = False
            return
        if self._module_setup_failed:
            logger.debug('Module setup failed; not tearing down class %r',
                         previous_class)
            return
        if getattr(previous_class, '__unittest_skip__', False):
            logger.debug('Previous class skipped; not tearing down class %r',
                         previous_class)
            return

        logger.debug('Tear down previous class: %r', previous_class)
        self._run_setup(
            previous_class, 'tearDownClass', previous_class.__name__)

    def _teardown_module(self, module_name):
        if self._module_setup_failed:
            logger.debug('Module setup failed; not tearing down module %r',
                         module_name)
            self._module_setup_failed = False
            return

        module = sys.modules.get(module_name)
        if module is None:
            return

        self._run_setup(module, 'tearDownModule', module_name)

    def teardown(self):
        if self._previous_class is None:
            return
        self._teardown_previous_class(None)
        previous_module = self._previous_class.__module__
        self._teardown_module(previous_module)


class TestSuite(object):
    """A ``TestSuite`` is a container of test cases and allows executing
    many test cases while managing the state of the overall suite.

    """

    def __init__(self, tests=()):
        self._tests = tuple(tests)

    def __iter__(self):
        return iter(self._tests)

    def __eq__(self, other):
        if not isinstance(other, TestSuite):
            return NotImplemented
        return list(self) == list(other)

    def __ne__(self, other):
        return not (self == other)

    def __call__(self, *args, **kwds):
        """Run all tests in the suite.

        Parameters
        ----------
        result : unittest.result.TestResult

        """
        return self.run(*args, **kwds)

    def run(self, result, _state=None):
        """Run all tests in the suite.

        Parameters
        ----------
        result : unittest.result.TestResult

        """
        if _state is None:
            state = _TestSuiteState(result)
        else:
            state = _state
        kwargs = {}
        for test in self:
            if result.shouldStop:
                break
            if state.setup(test):
                if isinstance(test, TestSuite):
                    kwargs = {'_state': state}
                logger.debug('Running test %r', test)
                test(result, **kwargs)
        if _state is None:
            state.teardown()
        return result

    def countTestCases(self):
        """Return the total number of tests contained in this suite.

        """
        return sum(test.countTestCases() for test in self)

    def __repr__(self):
        return '<{0} number_of_tests={1!r}>'.format(
            type(self).__name__, self.countTestCases())
