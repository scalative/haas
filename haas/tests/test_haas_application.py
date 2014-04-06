# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

import types

from mock import Mock, patch

import haas
from ..discoverer import Discoverer
from ..loader import Loader
from ..haas_application import HaasApplication
from ..testing import unittest


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

    def _run_with_arguments(self, runner_class, *args):
        runner = Mock()
        runner_class.return_value = runner

        result = Mock()
        result.wasSuccessful = Mock()
        run_method = Mock(return_value=result)
        runner.run = run_method

        app = HaasApplication(['argv0'] + list(args) + ['haas'])
        app.run()
        return run_method, result

    @patch('haas.testing.unittest.TextTestRunner')
    def test_main_default_arguments(self, runner_class):
        run, result = self._run_with_arguments(runner_class)
        runner_class.assert_called_once_with(
            verbosity=1, failfast=False, buffer=False,
            resultclass=MockLambda())
        suite = Discoverer(Loader()).discover('haas')
        run.assert_called_once_with(suite)

        result.wasSuccessful.assert_called_once_with()

    @patch('haas.testing.unittest.TextTestRunner')
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
    @patch('haas.testing.unittest.TextTestRunner')
    def test_main_quiet_and_verbose_not_allowed(self, runner_class, stdout,
                                                stderr):
        with self.assertRaises(SystemExit):
            self._run_with_arguments(runner_class, '-q', '-v')

    @patch('haas.testing.unittest.TextTestRunner')
    def test_main_verbose(self, runner_class):
        run, result = self._run_with_arguments(runner_class, '-v')

        runner_class.assert_called_once_with(
            verbosity=2, failfast=False, buffer=False,
            resultclass=MockLambda())
        suite = Discoverer(Loader()).discover('haas')
        run.assert_called_once_with(suite)

        result.wasSuccessful.assert_called_once_with()

    @patch('haas.testing.unittest.TextTestRunner')
    def test_main_failfast(self, runner_class):
        run, result = self._run_with_arguments(runner_class, '-f')

        runner_class.assert_called_once_with(
            verbosity=1, failfast=True, buffer=False,
            resultclass=MockLambda())
        suite = Discoverer(Loader()).discover('haas')
        run.assert_called_once_with(suite)

        result.wasSuccessful.assert_called_once_with()

    @patch('haas.testing.unittest.TextTestRunner')
    def test_main_buffer(self, runner_class):
        run, result = self._run_with_arguments(runner_class, '-b')

        runner_class.assert_called_once_with(
            verbosity=1, failfast=False, buffer=True,
            resultclass=MockLambda())
        suite = Discoverer(Loader()).discover('haas')
        run.assert_called_once_with(suite)

        result.wasSuccessful.assert_called_once_with()

    @patch('logging.getLogger')
    @patch('haas.testing.unittest.TextTestRunner')
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
    @patch('haas.testing.unittest.TextTestRunner')
    def test_invalid_environment_plugin(self, runner_class, stdout, stderr):
        with self.assertRaises(SystemExit):
            run, result = self._run_with_arguments(
                runner_class, '--environment-manager', 'haas.invalid')
