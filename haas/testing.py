# Copyright 2013-2014 Simon Jagoe
from contextlib import contextmanager
import sys


if sys.version_info[:2] == (2, 6):  # pragma: no cover
    import unittest2 as unittest
    from unittest2.case import _ExpectedFailure, _UnexpectedSuccess
else:
    import unittest
    from unittest.case import _ExpectedFailure, _UnexpectedSuccess


@contextmanager
def expected_failure():
    try:
        yield
    except Exception:
        raise _ExpectedFailure(sys.exc_info())
    raise _UnexpectedSuccess()
