# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

import mock
from six.moves import cStringIO as StringIO

from ..result import TextTestResult
from ..testing import unittest


class TestTextTestResult(unittest.TestCase):

    def setUp(self):
        self.time = 'Sun Apr  6 21:46:20 2014'

    def _run_with_verbosity(self, verbosity):
        stream = StringIO()
        result = TextTestResult(
            total_tests=100,
            stream=stream,
            descriptions=False,
            verbosity=verbosity,
        )
        with mock.patch('time.ctime') as ctime:
            ctime.return_value = self.time
            result.startTest(self)
        return stream.getvalue()

    def test_start_test_verbosity_1(self):
        expected = ''
        output = self._run_with_verbosity(1)
        self.assertEqual(output, expected)

    def test_start_test_verbosity_2(self):
        expected = '[{0}] (  1/100) {1} ... '.format(self.time, str(self))
        output = self._run_with_verbosity(2)
        self.assertEqual(output, expected)
