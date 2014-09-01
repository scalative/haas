# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from ..plugin_manager import PluginManager
from ..testing import unittest


class InvalidPlugin(object):
    pass


class PluginManagerFixture(object):

    def setUp(self):
        self.plugin_manager = PluginManager()

    def tearDown(self):
        del self.plugin_manager
