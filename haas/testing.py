# Copyright 2013-2014 Simon Jagoe
import sys


if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest
