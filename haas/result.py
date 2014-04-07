# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

import time

from .testing import unittest


class TextTestResult(unittest.TextTestResult):
    """A simple extension to ``unittest.TextTestResult`` that displays
    progression of testing when run in verbose mode.

    """

    def __init__(self, total_tests, stream, descriptions, verbosity):
        """Create a TextTestResult. The parameters ``stream``, ``descriptions``
        and ``verbosity`` are as in ``unittest.TextTestResult``.

        Parameters
        ----------
        total_tests : int
            The total number of tests in the suite to be run, as
            returned by ``Suite.countTestCases()``

        """
        self._total_tests = total_tests
        super(TextTestResult, self).__init__(stream, descriptions, verbosity)

    def startTest(self, test):
        if self.showAll:
            padding = len(str(self._total_tests))
            prefix = '[{timestamp}] ({run: >{padding}d}/{total:d}) '.format(
                timestamp=time.ctime(),
                run=self.testsRun + 1,
                padding=padding,
                total=self._total_tests,
            )
            self.stream.write(prefix)
        super(TextTestResult, self).startTest(test)

    startTest.__doc__ = unittest.TextTestResult.startTest.__doc__
