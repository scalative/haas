# Copyright 2013-2014 Simon Jagoe
from ..testing import unittest, expected_failure


class TestExpectedFailureContextManager(unittest.TestCase):

    def test_decorator_exception(self):
        with expected_failure():
            raise Exception()

    def test_decorator_failure(self):
        with expected_failure():
            self.fail()

    def test_decorator_unexpected_success(self):
        with expected_failure():
            pass

    def test_decorator_success(self):
        with expected_failure(False):
            pass
