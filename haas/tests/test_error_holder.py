# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from haas.testing import unittest

from ..error_holder import ErrorHolder


class TestErrorHolder(unittest.TestCase):

    def test_error_holder(self):
        holder = ErrorHolder('description')
        self.assertEqual(holder.id(), 'description')
        self.assertEqual(holder.shortDescription(), None)
        self.assertEqual(str(holder), holder.id())
        self.assertEqual(holder(None), None)
        self.assertEqual(holder.countTestCases(), 0)
