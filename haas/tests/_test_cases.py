# Copyright 2013-2014 Simon Jagoe
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


class TestSuite(NotTestCase, unittest.TestSuite):

    pass
