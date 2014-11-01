# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from argparse import Namespace
import os
import shutil
import tempfile
import types

from mock import Mock, patch

from stevedore.extension import ExtensionManager, Extension

import haas
from ..discoverer import Discoverer
from ..haas_application import HaasApplication
from ..loader import Loader
from ..plugin_manager import PluginManager
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


class TestHaasApplication(unittest.TestCase):

    def _run_with_arguments(self, runner_class, *args, **kwargs):
        plugin_manager = kwargs.get('plugin_manager')
        runner = Mock()
        runner_class.from_args.return_value = runner

        result = Mock()
        result.wasSuccessful = Mock()
        run_method = Mock(return_value=result)
        runner.run = run_method

        app = HaasApplication(['argv0'] + list(args))
        app.run(plugin_manager=plugin_manager)
        return run_method, result

    @patch('haas.plugins.runner.TextTestRunner')
    def test_main_default_arguments(self, runner_class):
        # Given
        environment_manager = ExtensionManager.make_test_instance(
            [], namespace=PluginManager.ENVIRONMENT_HOOK,
        )
        env_managers = [(PluginManager.ENVIRONMENT_HOOK, environment_manager)]
        extension = Extension('default', None, runner_class, None)
        driver_managers = [
            (PluginManager.TEST_RUNNER, ExtensionManager.make_test_instance(
                [extension], namespace=PluginManager.TEST_RUNNER)),
        ]
        plugin_manager = PluginManager.testing_plugin_manager(
            hook_managers=env_managers,
            driver_managers=driver_managers)

        # When
        run, result = self._run_with_arguments(
            runner_class, plugin_manager=plugin_manager)

        # Then
        self.assertEqual(runner_class.from_args.call_count, 1)
        args = runner_class.from_args.call_args
        self.assertIsInstance(args[0][0], Namespace)
        self.assertEqual(args[0][1], 'runner_')

        suite = Discoverer(Loader()).discover('haas')
        run.assert_called_once_with(suite)

        result.wasSuccessful.assert_called_once_with()

    @patch('haas.plugins.runner.TextTestRunner')
    def test_main_quiet(self, runner_class):
        run, result = self._run_with_arguments(runner_class, '-q')

        runner_class.assert_called_once_with(
            verbosity=0, failfast=False, buffer=False,
            resultclass=MockLambda())
        suite = Discoverer(Loader()).discover('haas')
        run.assert_called_once_with(suite)

        result.wasSuccessful.assert_called_once_with()

    @patch('sys.stdout')
    @patch('sys.stderr')
    @patch('haas.plugins.runner.TextTestRunner')
    def test_main_quiet_and_verbose_not_allowed(self, runner_class, stdout,
                                                stderr):
        with self.assertRaises(SystemExit):
            self._run_with_arguments(runner_class, '-q', '-v')

    @patch('haas.plugins.runner.TextTestRunner')
    def test_main_verbose(self, runner_class):
        run, result = self._run_with_arguments(runner_class, '-v')

        runner_class.assert_called_once_with(
            verbosity=2, failfast=False, buffer=False,
            resultclass=MockLambda())
        suite = Discoverer(Loader()).discover('haas')
        run.assert_called_once_with(suite)

        result.wasSuccessful.assert_called_once_with()

    @patch('haas.plugins.runner.TextTestRunner')
    def test_main_failfast(self, runner_class):
        run, result = self._run_with_arguments(runner_class, '-f')

        runner_class.assert_called_once_with(
            verbosity=1, failfast=True, buffer=False,
            resultclass=MockLambda())
        suite = Discoverer(Loader()).discover('haas')
        run.assert_called_once_with(suite)

        result.wasSuccessful.assert_called_once_with()

    @patch('haas.plugins.runner.TextTestRunner')
    def test_main_buffer(self, runner_class):
        run, result = self._run_with_arguments(runner_class, '-b')

        runner_class.assert_called_once_with(
            verbosity=1, failfast=False, buffer=True,
            resultclass=MockLambda())
        suite = Discoverer(Loader()).discover('haas')
        run.assert_called_once_with(suite)

        result.wasSuccessful.assert_called_once_with()

    @patch('logging.getLogger')
    @patch('haas.plugins.runner.TextTestRunner')
    def test_with_logging(self, runner_class, get_logger):
        run, result = self._run_with_arguments(
            runner_class, '--log-level', 'debug')
        get_logger.assert_called_once_with(haas.__name__)

        runner_class.assert_called_once_with(
            verbosity=1, failfast=False, buffer=False,
            resultclass=MockLambda())
        suite = Discoverer(Loader()).discover('haas')
        run.assert_called_once_with(suite)

        result.wasSuccessful.assert_called_once_with()

    @patch('sys.stdout')
    @patch('sys.stderr')
    @patch('coverage.coverage')
    @patch('haas.plugins.runner.TextTestRunner')
    def test_with_coverage_plugin(self, runner_class, coverage, stdout,
                                  stderr):
        # When
        run, result = self._run_with_arguments(
            runner_class, '--with-coverage')

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

    @patch('haas.plugins.runner.TextTestRunner')
    def test_multiple_start_directories(self, runner_class):
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
                    runner_class, '-t', top_level, 'first', 'second')

            loader = Loader()
            suite1 = Discoverer(loader).discover('first', top_level)
            suite2 = Discoverer(loader).discover('second', top_level)
            suite = loader.create_suite((suite1, suite2))

            # Then
            run.assert_called_once_with(suite)

        finally:
            shutil.rmtree(tempdir)

    @patch('haas.plugins.runner.TextTestRunner')
    def test_multiple_start_directories_non_package(self, runner_class):
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
                        runner_class, '-t', top_level, 'first', 'second')

        finally:
            shutil.rmtree(tempdir)
