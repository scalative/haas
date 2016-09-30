# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from argparse import Namespace
from contextlib import contextmanager
from functools import wraps
import logging
import os
import shutil
import tempfile
import types

from mock import Mock, patch
from testfixtures import LogCapture

from stevedore.extension import ExtensionManager, Extension

import haas
from ..haas_application import HaasApplication
from ..loader import Loader
from ..plugin_manager import PluginManager
from ..plugins.discoverer import Discoverer
from ..suite import TestSuite
from ..testing import unittest
from ..utils import cd
from . import builder


class MockLambda(object):

    def __eq__(self, other):
        if isinstance(other, types.FunctionType):
            result_class = other(None, None, 1)
            if isinstance(result_class, unittest.TestResult):
                return True
        return False

    def __ne__(self, other):
        return not (other == self)


def with_patched_test_runner(fn):
    @wraps(fn)
    def wrapper(*args):
        with patch('haas.haas_application.ResultCollector') as result_cls:
            with patch('haas.plugins.runner.BaseTestRunner') as runner_class:
                environment_manager = ExtensionManager.make_test_instance(
                    [], namespace=PluginManager.ENVIRONMENT_HOOK,
                )
                result_handler = Extension(
                    'default', None, result_cls, None)
                env_managers = [
                    (PluginManager.ENVIRONMENT_HOOK, environment_manager),
                    (
                        PluginManager.RESULT_HANDLERS,
                        ExtensionManager.make_test_instance(
                            [result_handler],
                            namespace=PluginManager.RESULT_HANDLERS),
                    ),
                ]
                runner = Extension('default', None, runner_class, None)
                discoverer = Extension('default', None, Discoverer, None)
                driver_managers = [
                    (
                        PluginManager.TEST_DISCOVERY,
                        ExtensionManager.make_test_instance(
                            [discoverer],
                            namespace=PluginManager.TEST_DISCOVERY),
                    ),
                    (
                        PluginManager.TEST_RUNNER,
                        ExtensionManager.make_test_instance(
                            [runner], namespace=PluginManager.TEST_RUNNER),
                    ),
                ]
                plugin_manager = PluginManager.testing_plugin_manager(
                    hook_managers=env_managers,
                    driver_managers=driver_managers)
                args_ = args + (runner_class, result_cls, plugin_manager,)
                return fn(*args_)
    return wrapper


class TestHaasApplication(unittest.TestCase):

    def _run_with_arguments(self, runner_class, result_class, *args, **kwargs):
        plugin_manager = kwargs.get('plugin_manager')
        runner = Mock()
        runner_class.from_args.return_value = runner

        result = Mock()
        result.wasSuccessful = Mock()
        result_class.return_value = result
        run_method = Mock(return_value=result)
        runner.run = run_method

        app = HaasApplication(['argv0'] + list(args))
        app.run(plugin_manager=plugin_manager)
        return run_method, result

    @contextmanager
    def _basic_test_fixture(self):
        package_name = 'first'
        module = builder.Module(
            'test_something.py',
            (
                builder.Class(
                    'TestSomething',
                    (
                        builder.Method('test_method'),
                    ),
                ),
            ),
        )
        fixture = builder.Directory(
            'top',
            (
                builder.Package(package_name, (module,)),
            ),
        )

        tempdir = tempfile.mkdtemp(prefix='haas-tests-')
        try:
            fixture.create(tempdir)
            top_level = os.path.join(tempdir, fixture.name)
            with cd(top_level):
                yield package_name
        finally:
            shutil.rmtree(tempdir)

    @with_patched_test_runner
    def test_main_default_arguments(self, runner_class, result_class,
                                    plugin_manager):
        # When
        with self._basic_test_fixture() as package_name:
            run, result = self._run_with_arguments(
                runner_class, result_class, plugin_manager=plugin_manager)
            suite = Discoverer(Loader()).discover(package_name)

        # Then
        self.assertEqual(runner_class.from_args.call_count, 1)
        args = runner_class.from_args.call_args
        args, kwargs = args
        ns, dest = args
        self.assertIsInstance(ns, Namespace)
        self.assertEqual(dest, 'runner_')
        self.assertEqual(ns.verbosity, 1)
        self.assertFalse(ns.failfast)
        self.assertFalse(ns.buffer)

        run.assert_called_once_with(result, suite)
        result.wasSuccessful.assert_called_once_with()

    @with_patched_test_runner
    def test_main_quiet(self, runner_class, result_class, plugin_manager):
        # When
        with self._basic_test_fixture() as package_name:
            run, result = self._run_with_arguments(
                runner_class, result_class, '-q',
                plugin_manager=plugin_manager)
            suite = Discoverer(Loader()).discover(package_name)

        # Then
        args = runner_class.from_args.call_args
        args, kwargs = args
        ns, dest = args
        self.assertIsInstance(ns, Namespace)
        self.assertEqual(ns.verbosity, 0)
        self.assertFalse(ns.failfast)
        self.assertFalse(ns.buffer)

        run.assert_called_once_with(result, suite)
        result.wasSuccessful.assert_called_once_with()

    @patch('sys.stdout')
    @patch('sys.stderr')
    @patch('haas.plugins.runner.BaseTestRunner')
    def test_main_quiet_and_verbose_not_allowed(self,
                                                runner_class, stdout, stderr):
        with self.assertRaises(SystemExit):
            self._run_with_arguments(runner_class, Mock(), '-q', '-v')

    @with_patched_test_runner
    def test_main_verbose(self, runner_class, result_class, plugin_manager):
        # When
        with self._basic_test_fixture() as package_name:
            run, result = self._run_with_arguments(
                runner_class, result_class, '-v',
                plugin_manager=plugin_manager)
            suite = Discoverer(Loader()).discover(package_name)

        # Then
        args = runner_class.from_args.call_args
        args, kwargs = args
        ns, dest = args
        self.assertIsInstance(ns, Namespace)
        self.assertEqual(ns.verbosity, 2)
        self.assertFalse(ns.failfast)
        self.assertFalse(ns.buffer)

        run.assert_called_once_with(result, suite)
        result.wasSuccessful.assert_called_once_with()

    @with_patched_test_runner
    def test_main_failfast(self, runner_class, result_class, plugin_manager):
        # When
        with self._basic_test_fixture() as package_name:
            run, result = self._run_with_arguments(
                runner_class, result_class, '-f',
                plugin_manager=plugin_manager)
            suite = Discoverer(Loader()).discover(package_name)

        # Then
        args = runner_class.from_args.call_args
        args, kwargs = args
        ns, dest = args
        self.assertIsInstance(ns, Namespace)
        self.assertEqual(ns.verbosity, 1)
        self.assertTrue(ns.failfast)
        self.assertFalse(ns.buffer)

        run.assert_called_once_with(result, suite)
        result.wasSuccessful.assert_called_once_with()

    @with_patched_test_runner
    def test_main_buffer(self, runner_class, result_class, plugin_manager):
        # When
        with self._basic_test_fixture() as package_name:
            run, result = self._run_with_arguments(
                runner_class, result_class, '-b',
                plugin_manager=plugin_manager)
            suite = Discoverer(Loader()).discover(package_name)

        # Then
        args = runner_class.from_args.call_args
        args, kwargs = args
        ns, dest = args
        self.assertIsInstance(ns, Namespace)
        self.assertEqual(ns.verbosity, 1)
        self.assertFalse(ns.failfast)
        self.assertTrue(ns.buffer)

        run.assert_called_once_with(result, suite)
        result.wasSuccessful.assert_called_once_with()

    @patch('logging.getLogger')
    @with_patched_test_runner
    def test_with_logging(self, get_logger, runner_class, result_class,
                          plugin_manager):
        # Given
        with self._basic_test_fixture() as package_name:
            run, result = self._run_with_arguments(
                runner_class, result_class, '--log-level', 'debug',
                plugin_manager=plugin_manager)
            suite = Discoverer(Loader()).discover(package_name)

        # Then
        get_logger.assert_called_once_with(haas.__name__)
        args = runner_class.from_args.call_args
        args, kwargs = args
        ns, dest = args
        self.assertIsInstance(ns, Namespace)
        self.assertEqual(ns.verbosity, 1)
        self.assertFalse(ns.failfast)
        self.assertFalse(ns.buffer)

        run.assert_called_once_with(result, suite)
        result.wasSuccessful.assert_called_once_with()

    @patch('sys.stdout')
    @patch('sys.stderr')
    @patch('coverage.coverage')
    @patch('haas.plugins.runner.BaseTestRunner')
    def test_with_coverage_plugin(self, runner_class, coverage,
                                  stdout, stderr):
        # When
        run, result = self._run_with_arguments(
            runner_class, Mock(), '--with-coverage')

        # Then
        coverage.assert_called_once_with()

    def test_failfast(self):
        def test_should_cause_early_stop(self1):
            self1.fail()

        def test_cause_failure(self1):
            print('Did I fail?')
            self.fail('Failfast test did not abort test run')

        cls_dict = {
            'test_should_cause_early_stop': test_should_cause_early_stop,
            'test_cause_failure': test_cause_failure,
        }
        test_cls = type(str('TestFailfast'), (unittest.TestCase,), cls_dict)
        suite = TestSuite(
            [
                TestSuite(
                    [
                        test_cls('test_should_cause_early_stop'),
                        test_cls('test_cause_failure'),
                    ],
                ),
                TestSuite(
                    [
                        test_cls('test_cause_failure'),
                    ],
                ),
            ],
        )
        self.assertEqual(suite.countTestCases(), 3)

        result = unittest.TestResult()
        result.failfast = True
        suite.run(result)
        self.assertEqual(result.testsRun, 1)

    @with_patched_test_runner
    def test_multiple_start_directories(self, runner_class, result_class,
                                        plugin_manager):
        # Given
        module = builder.Module(
            'test_something.py',
            (
                builder.Class(
                    'TestSomething',
                    (
                        builder.Method('test_method'),
                    ),
                ),
            ),
        )
        fixture = builder.Directory(
            'top',
            (
                builder.Package('first', (module,)),
                builder.Package('second', (module,)),
            ),
        )

        tempdir = tempfile.mkdtemp(prefix='haas-tests-')
        try:
            fixture.create(tempdir)

            top_level = os.path.join(tempdir, fixture.name)

            # When
            with cd(top_level):
                run, result = self._run_with_arguments(
                    runner_class, result_class, '-t', top_level, 'first',
                    'second', plugin_manager=plugin_manager,
                )

                loader = Loader()
                suite1 = Discoverer(loader).discover('first', top_level)
                suite2 = Discoverer(loader).discover('second', top_level)
                suite = loader.create_suite((suite1, suite2))

            # Then
            run.assert_called_once_with(result, suite)

        finally:
            shutil.rmtree(tempdir)

    @with_patched_test_runner
    def test_multiple_start_directories_non_package(self, runner_class,
                                                    result_class,
                                                    plugin_manager):
        # Given
        module = builder.Module(
            'test_something.py',
            (
                builder.Class(
                    'TestSomething',
                    (
                        builder.Method('test_method'),
                    ),
                ),
            ),
        )
        fixture = builder.Directory(
            'top',
            (
                builder.Package('first', (module,)),
                builder.Directory('second', (module,)),
            ),
        )

        tempdir = tempfile.mkdtemp(prefix='haas-tests-')
        try:
            fixture.create(tempdir)

            top_level = os.path.join(tempdir, fixture.name)

            # When/Then
            with cd(top_level):
                with self.assertRaises(ImportError):
                    run, result = self._run_with_arguments(
                        runner_class, result_class, '-t', top_level, 'first',
                        'second', plugin_manager=plugin_manager)

        finally:
            shutil.rmtree(tempdir)

    @with_patched_test_runner
    def test_logging_propagate(self, runner_class, result_class,
                               plugin_manager):
        # Given
        logger = haas.logger
        message = 'test log message'

        # When
        with LogCapture() as root_logging:
            with LogCapture(haas.__name__) as haas_logging:
                logger.info(message)

        # Then
        root_logging.check()
        haas_logging.check(
            (haas.__name__, logging.getLevelName(logging.INFO), message))
