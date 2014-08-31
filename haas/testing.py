# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
__all__ = [
    'unittest',
]

import sys


if sys.version_info[:2] == (2, 6):  # pragma: no cover
    import unittest2 as unittest
else:
    import unittest
