# Copyright 2013-2014 Simon Jagoe
from ..testing import (
    _ExpectedFailure,
    _UnexpectedSuccess,
    expected_failure,
    unittest,
)


class TestExpectedFailureContextManager(unittest.TestCase):

    def test_context_exception(self):
        try:
            with expected_failure():
                raise Exception()
        except _ExpectedFailure:
            return
        self.fail('Did not receive expected failure')

    def test_context_failure(self):
        try:
            with expected_failure():
                self.fail()
        except _ExpectedFailure:
            return
        self.fail('Did not receive expected failure')

    def test_decorator_unexpected_success(self):
        try:
            with expected_failure():
                pass
        except _UnexpectedSuccess:
            return
        self.fail('Did not receive unexpected success')

    def test_decorator_success(self):
        with expected_failure(False):
            pass
