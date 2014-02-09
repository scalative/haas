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

    @patch('haas.testing.unittest.TextTestRunner')
    def test_main_runs_tests(self, runner_class):
        runner = Mock()
        runner_class.return_value = runner

        result = Mock()
        result.wasSuccessful = Mock()
        run = Mock(return_value=result)
        runner.run = run

        main(['argv0', 'haas'])
        runner_class.assert_called_once_with()
        suite = Discoverer(Loader()).discover('haas')
        run.assert_called_once_with(suite)

        result.wasSuccessful.assert_called_once_with()
