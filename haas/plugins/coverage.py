# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

import coverage

from .base_hook_plugin import BaseHookPlugin


class Coverage(BaseHookPlugin):

    def __init__(self, *args, **kwargs):
        super(Coverage, self).__init__(*args, **kwargs)
        self._coverage = None

    def setup(self):
        self._coverage = coverage.coverage()
        self._coverage.start()

    def teardown(self):
        self._coverage.stop()
        self._coverage.save()
