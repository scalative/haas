# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

try:
    import coverage
    from ..coverage import Coverage
except ImportError:
    coverage = None
    Coverage = None

from mock import Mock, patch

from haas.testing import unittest


@unittest.skipIf(coverage is None, 'Coverage is not installed')
class TestCoverage(unittest.TestCase):

    @patch('coverage.coverage')
    def test_coverage(self, coverage_func):
        coverage_object = Mock()
        coverage_func.return_value = coverage_object
        coverage_object.start = Mock()
        coverage_object.stop = Mock()
        coverage_object.save = Mock()

        cov = Coverage('coverage', True, 'coverage')
        self.assertFalse(coverage_func.called)
        self.assertFalse(coverage_object.start.called)
        self.assertFalse(coverage_object.stop.called)
        self.assertFalse(coverage_object.save.called)
        cov.setup()
        coverage_func.assert_called_once_with()
        coverage_object.start.assert_called_once_with()
        self.assertFalse(coverage_object.stop.called)
        self.assertFalse(coverage_object.save.called)
        cov.teardown()
        coverage_object.stop.assert_called_once_with()
        coverage_object.save.assert_called_once_with()
