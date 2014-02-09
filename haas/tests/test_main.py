# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import unicode_literals

from mock import Mock, patch

from ..discoverer import Discoverer
from ..loader import Loader
from ..main import main
from ..testing import unittest


class TestMain(unittest.TestCase):

    def _run_with_arguments(self, runner_class, *args):
        runner = Mock()
        runner_class.return_value = runner

        result = Mock()
        result.wasSuccessful = Mock()
        run_method = Mock(return_value=result)
        runner.run = run_method

        main(['argv0'] + list(args) + ['haas'])
        return run_method, result

    @patch('haas.testing.unittest.TextTestRunner')
    def test_main_default_arguments(self, runner_class):
        run, result = self._run_with_arguments(runner_class)
        runner_class.assert_called_once_with(
            verbosity=1, failfast=False, buffer=False)
        suite = Discoverer(Loader()).discover('haas')
        run.assert_called_once_with(suite)

        result.wasSuccessful.assert_called_once_with()

    @patch('haas.testing.unittest.TextTestRunner')
    def test_main_quiet(self, runner_class):
        run, result = self._run_with_arguments(runner_class, '-q')

        runner_class.assert_called_once_with(
            verbosity=0, failfast=False, buffer=False)
        suite = Discoverer(Loader()).discover('haas')
        run.assert_called_once_with(suite)

        result.wasSuccessful.assert_called_once_with()

    @patch('haas.testing.unittest.TextTestRunner')
    def test_main_quiet_and_verbose(self, runner_class):
        run, result = self._run_with_arguments(runner_class, '-q', '-v')

        runner_class.assert_called_once_with(
            verbosity=1, failfast=False, buffer=False)
        suite = Discoverer(Loader()).discover('haas')
        run.assert_called_once_with(suite)

        result.wasSuccessful.assert_called_once_with()

    @patch('haas.testing.unittest.TextTestRunner')
    def test_main_verbose(self, runner_class):
        run, result = self._run_with_arguments(runner_class, '-v')

        runner_class.assert_called_once_with(
            verbosity=2, failfast=False, buffer=False)
        suite = Discoverer(Loader()).discover('haas')
        run.assert_called_once_with(suite)

        result.wasSuccessful.assert_called_once_with()

    @patch('haas.testing.unittest.TextTestRunner')
    def test_main_failfast(self, runner_class):
        run, result = self._run_with_arguments(runner_class, '-f')

        runner_class.assert_called_once_with(
            verbosity=1, failfast=True, buffer=False)
        suite = Discoverer(Loader()).discover('haas')
        run.assert_called_once_with(suite)

        result.wasSuccessful.assert_called_once_with()

    @patch('haas.testing.unittest.TextTestRunner')
    def test_main_buffer(self, runner_class):
        run, result = self._run_with_arguments(runner_class, '-b')

        runner_class.assert_called_once_with(
            verbosity=1, failfast=False, buffer=True)
        suite = Discoverer(Loader()).discover('haas')
        run.assert_called_once_with(suite)

        result.wasSuccessful.assert_called_once_with()
