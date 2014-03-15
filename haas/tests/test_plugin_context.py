# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from mock import Mock

from ..plugin_context import PluginContext
from ..testing import unittest


class TestPluginContext(unittest.TestCase):

    def test_empty_plugin_context(self):
        context = PluginContext()
        self.assertEqual(context.hooks, ())
        # This shount not raise
        with context:
            pass

    def test_plugin_context_no_plugins(self):
        context = PluginContext([])
        self.assertEqual(context.hooks, ())
        # This shount not raise
        with context:
            pass

    def test_plugin_context_none_plugin(self):
        context = PluginContext([None])
        self.assertEqual(context.hooks, ())
        # This shount not raise
        with context:
            pass

    def test_plugin_context_with_plugin(self):
        plugin = Mock()
        plugin.setup = Mock()
        plugin.teardown = Mock()
        context = PluginContext([plugin])
        self.assertEqual(context.hooks, (plugin,))
        # This should not raise
        with context:
            plugin.setup.assert_called_once_with()
            self.assertFalse(plugin.teardown.called)
        plugin.teardown.assert_called_once_with()
