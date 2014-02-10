# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
__all__ = [
    'expected_failure',
    'unittest',
]

from contextlib import contextmanager
import sys


if sys.version_info[:2] == (2, 6):  # pragma: no cover
    import unittest2 as unittest
    from unittest2.case import _ExpectedFailure, _UnexpectedSuccess
else:  # pragma: no cover
    import unittest
    from unittest.case import _ExpectedFailure, _UnexpectedSuccess


@contextmanager
def expected_failure(condition=True):
    """Conditional expected failure context manager.

    Paramaters
    ----------
    condition : boolean
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
