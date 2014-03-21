# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from ..plugin_manager import PluginError, PluginManager
from ..testing import unittest


class InvalidPlugin(object):
    pass


class PluginManagerFixture(object):

    def setUp(self):
        self.plugin_manager = PluginManager()

    def tearDown(self):
        del self.plugin_manager


class TestLoadPluginClass(PluginManagerFixture, unittest.TestCase):

    def test_none_raises(self):
        with self.assertRaises(PluginError):
            self.plugin_manager.load_plugin_class(None)

    def test_no_dot_raises(self):
        with self.assertRaises(PluginError):
            self.plugin_manager.load_plugin_class(
                'module_with_no_class_attribute')

    def test_missing_module_raises(self):
        with self.assertRaises(PluginError):
            self.plugin_manager.load_plugin_class('haas.non_existent.factory')

    def test_no_in_module_attribute_raises(self):
        with self.assertRaises(PluginError):
            self.plugin_manager.load_plugin_class('haas.plugin_context')

    def test_missing_factory_raises(self):
        with self.assertRaises(PluginError):
            self.plugin_manager.load_plugin_class(
                'haas.plugins.coverage.non_existent')

    def test_valid_plugin(self):
        klass = self.plugin_manager.load_plugin_class(
            'haas.plugins.coverage.Coverage')
        from ..plugins.coverage import Coverage
        self.assertIs(klass, Coverage)


class TestLoadPlugin(PluginManagerFixture, unittest.TestCase):

    def test_none_returns_none(self):
        self.assertIsNone(self.plugin_manager.load_plugin(None))

    def test_valid_plugin(self):
        plugin = self.plugin_manager.load_plugin(
            'haas.plugins.coverage.Coverage')
        from ..plugins.coverage import Coverage
        self.assertIsInstance(plugin, Coverage)

    def test_invalid_plugin(self):
        with self.assertRaises(PluginError):
            self.plugin_manager.load_plugin(
                'haas.tests.test_plugin_manager.InvalidPlugin')
