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
def expected_failure(condition=True):
    """Conditional expected failure context manager.

    Paramaters
    ----------
    conditional : boolean
        If True, the context will be expected failure, otherwise it is
        expected to succeed.

    """
    if condition:
        try:
            yield
        except Exception:
            raise _ExpectedFailure(sys.exc_info())
        raise _UnexpectedSuccess()
    else:
        yield
