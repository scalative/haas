# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from argparse import ArgumentParser
from collections import OrderedDict

from stevedore.extension import ExtensionManager, Extension

from haas.plugins.base_hook_plugin import BaseHookPlugin
from ..plugin_manager import PluginManager
from ..testing import unittest


class InvalidPlugin(object):
    pass


class TestingPlugin(BaseHookPlugin):

    def __init__(self, *args, **kwargs):
        super(TestingPlugin, self).__init__(*args, **kwargs)
        self.setup_called = 0
        self.teardown_called = 0
        self.add_parser_arguments_called = 0
        self.configure_called = 0

    def setup(self):
        self.setup_called += 1

    def teardown(self):
        self.teardown_called += 1

    def add_parser_arguments(self, parser):
        self.add_parser_arguments_called += 1
        return super(TestingPlugin, self).add_parser_arguments(parser)

    def configure(self, args):
        self.configure_called += 1
        return super(TestingPlugin, self).configure(args)


class TestBaseHookPlugin(unittest.TestCase):

    def test_name_default(self):
        # When
        plugin = TestingPlugin(name='my-name')

        # Then
        self.assertEqual(plugin.name, 'my-name')

        # When
        plugin = TestingPlugin()

        # Then
        self.assertEqual(plugin.name, 'testing-plugin')


class TestPluginManagerWithPlugins(unittest.TestCase):

    def setUp(self):
        self.plugin_obj = TestingPlugin()
        self.extension = Extension(
            'extension', None, TestingPlugin, self.plugin_obj)
        extensions = [
            self.extension,
        ]
        environment_manager = ExtensionManager.make_test_instance(
            extensions, namespace=PluginManager.ENVIRONMENT_HOOK,
        )
        hook_managers = [(PluginManager.ENVIRONMENT_HOOK, environment_manager)]
        self.plugin_manager = PluginManager.testing_plugin_manager(
            hook_managers=hook_managers, driver_managers=())

    def test_environment_hook_options(self):
        # Given
        plugin_manager = self.plugin_manager
        parser = ArgumentParser(add_help=False)

        # When
        plugin_manager.add_plugin_arguments(parser)

        # Then
        self.assertEqual(self.plugin_obj.add_parser_arguments_called, 1)
        actions = parser._actions
        self.assertEqual(len(actions), 1)
        action, = actions
        self.assertEqual(action.option_strings, ['--with-testing-plugin'])

        # When
        enabled_plugins = plugin_manager.get_enabled_hook_plugins(
            plugin_manager.ENVIRONMENT_HOOK)

        # Then
        self.assertFalse(self.plugin_obj.enabled)
        self.assertEqual(enabled_plugins, [])

        # When
        args = parser.parse_args(['--with-testing-plugin'])
        plugin_manager.configure_plugins(args)

        # Then
        self.assertEqual(self.plugin_obj.configure_called, 1)

        # When
        enabled_plugins = plugin_manager.get_enabled_hook_plugins(
            plugin_manager.ENVIRONMENT_HOOK)

        # Then
        self.assertTrue(self.plugin_obj.enabled)
        self.assertEqual(enabled_plugins, [self.plugin_obj])


class TestPluginManagerWithoutPlugins(unittest.TestCase):

    def setUp(self):
        environment_manager = ExtensionManager.make_test_instance(
            [], namespace=PluginManager.ENVIRONMENT_HOOK,
        )
        hook_managers = [(PluginManager.ENVIRONMENT_HOOK, environment_manager)]
        self.plugin_manager = PluginManager.testing_plugin_manager(
            hook_managers=hook_managers, driver_managers=())

    def test_environment_hook_options_no_plugins(self):
        # Given
        plugin_manager = self.plugin_manager
        parser = ArgumentParser(add_help=False)

        # When
        plugin_manager.add_plugin_arguments(parser)

        # Then
        actions = parser._actions
        self.assertEqual(len(actions), 0)

        # When
        enabled_plugins = plugin_manager.get_enabled_hook_plugins(
            plugin_manager.ENVIRONMENT_HOOK)

        # Then
        self.assertEqual(enabled_plugins, [])

        # When
        args = parser.parse_args([])
        plugin_manager.configure_plugins(args)

        # When
        enabled_plugins = plugin_manager.get_enabled_hook_plugins(
            plugin_manager.ENVIRONMENT_HOOK)

        # Then
        self.assertEqual(enabled_plugins, [])
