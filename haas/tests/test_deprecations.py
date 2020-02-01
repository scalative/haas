# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from testfixtures import ShouldWarn

from ..result import ResultCollecter
from ..testing import unittest


class TestResultCollecterDepricated(unittest.TestCase):

    def test_deprecation_warning(self):
        # Given
        expected_warning = DeprecationWarning(
            'ResultCollecter is deprecated in favour of ResultCollector and '
            'will be removed in the next release.',
        )

        # When/Then
        with ShouldWarn(expected_warning):
            ResultCollecter()
