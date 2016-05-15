from haas.testing import unittest
from ..suite import TestSuite


class TestSuiteSubclass(TestSuite):

    pass


class TestCaseSubclass(unittest.TestCase):

    def test_method(self):
        pass


class BadlySubclassedTestCase(unittest.TestCase):

    def __init__(self, wrongly_named):
        unittest.TestCase.__init__(self, wrongly_named)

    def test_method(self):
        pass


class TestSuiteNotSubclass(object):

    def __init__(self, tests=()):
        self.tests = tests

    def __iter__(self):
        return iter(self.tests)


class TestWithTwoErrors(unittest.TestCase):

    def test_with_two_errors(self):
        raise RuntimeError('An error in a test case')

    def tearDown(self):
        raise RuntimeError('An error in tearDown')
