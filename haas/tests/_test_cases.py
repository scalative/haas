# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

import unittest as python_unittest

from haas.testing import unittest


class NotTestCase(object):

    def test_method(self):
        pass

    def _private_method(self):
        pass

    def non_test_public_method(self):
        pass


class TestCase(NotTestCase, unittest.TestCase):

    pass


class PythonTestCase(NotTestCase, python_unittest.TestCase):

    pass


class TestSuite(NotTestCase, unittest.TestSuite):

    pass


def subprocess_initializer():
    pass
