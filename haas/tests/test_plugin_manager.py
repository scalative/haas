# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from argparse import ArgumentParser

from stevedore.extension import ExtensionManager, Extension

from haas.plugins.base_hook_plugin import BaseHookPlugin
from haas.plugins.runner import BaseTestRunner
from ..haas_application import create_argument_parser
from ..plugin_manager import PluginManager
from ..testing import unittest


class InvalidPlugin(object):
    pass


class BaseTestingPlugin(BaseHookPlugin):

    def __init__(self, *args, **kwargs):
        super(BaseTestingPlugin, self).__init__(*args, **kwargs)
        self.setup_called = 0
        self.teardown_called = 0
        self.add_parser_arguments_called = 0
        self.configure_called = 0

    def setup(self):
        self.setup_called += 1

    def teardown(self):
        self.teardown_called += 1


class TestPluginManager(unittest.TestCase):

    def test_environment_hook_options(self):
        class TestingPlugin(BaseTestingPlugin):
            add_parser_arguments_called = 0
            from_args_called = 0

            @classmethod
            def add_parser_arguments(cls, parser, name, option_prefix,
                                     dest_prefix):
                cls.add_parser_arguments_called += 1
                return super(TestingPlugin, cls).add_parser_arguments(
                    parser, name, option_prefix, dest_prefix)

            @classmethod
            def from_args(cls, args, name, dest_prefix):
                cls.from_args_called += 1
                return super(TestingPlugin, cls).from_args(
                    args, name, dest_prefix)

        # Given
        extension = Extension(
            'testing-plugin', None, TestingPlugin, None)
        environment_manager = ExtensionManager.make_test_instance(
            [extension], namespace=PluginManager.ENVIRONMENT_HOOK,
        )
        hook_managers = [(PluginManager.ENVIRONMENT_HOOK, environment_manager)]
        plugin_manager = PluginManager.testing_plugin_manager(
            hook_managers=hook_managers, driver_managers=())
        parser = ArgumentParser(add_help=False)

        # When
        plugin_manager.add_plugin_arguments(parser)

        # Then
        self.assertEqual(TestingPlugin.add_parser_arguments_called, 1)
        actions = parser._actions
        self.assertEqual(len(actions), 1)
        action, = actions
        self.assertEqual(action.option_strings, ['--with-testing-plugin'])

        # When
        args = parser.parse_args([])
        enabled_plugins = plugin_manager.get_enabled_hook_plugins(
            plugin_manager.ENVIRONMENT_HOOK, args)

        # Then
        self.assertEqual(enabled_plugins, [])
        self.assertEqual(TestingPlugin.from_args_called, 1)

        # When
        args = parser.parse_args(['--with-testing-plugin'])
        enabled_plugins = plugin_manager.get_enabled_hook_plugins(
            plugin_manager.ENVIRONMENT_HOOK, args)

        # Then
        self.assertEqual(len(enabled_plugins), 1)

        plugin_obj, = enabled_plugins
        self.assertEqual(TestingPlugin.from_args_called, 2)
        self.assertTrue(plugin_obj.enabled)

    def test_driver_hooks_found(self):
        # Given
        extension = Extension(
            'haas.runner', None, BaseTestRunner, None)
        driver_managers = [
            (PluginManager.TEST_RUNNER, ExtensionManager.make_test_instance(
                [extension], namespace=PluginManager.TEST_RUNNER)),
        ]
        plugin_manager = PluginManager.testing_plugin_manager(
            hook_managers=(), driver_managers=driver_managers)
        parser = ArgumentParser(add_help=False)

        # When
        plugin_manager.add_plugin_arguments(parser)

        # Then
        actions = parser._actions
        self.assertEqual(len(actions), 1)
        action, = actions
        self.assertEqual(action.option_strings, ['--runner'])

    def test_get_default_driver(self):
        # Given
        class OtherRunner(BaseTestRunner):
            pass

        default = Extension(
            'default', None, BaseTestRunner, None)
        other = Extension(
            'other', None, OtherRunner, None)
        driver_managers = [
            (PluginManager.TEST_RUNNER, ExtensionManager.make_test_instance(
                [default, other], namespace=PluginManager.TEST_RUNNER)),
        ]
        plugin_manager = PluginManager.testing_plugin_manager(
            hook_managers=(), driver_managers=driver_managers)
        parser = create_argument_parser()
        plugin_manager.add_plugin_arguments(parser)

        # When
        args = parser.parse_args([])
        plugin_manager.get_driver(plugin_manager.TEST_RUNNER, args)
        runner = plugin_manager.get_driver(plugin_manager.TEST_RUNNER, args)

        # Then
        self.assertNotIsInstance(runner, OtherRunner)

    def test_get_other_driver(self):
        # Given
        class OtherRunner(BaseTestRunner):
            pass

        default = Extension(
            'default', None, BaseTestRunner, None)
        other = Extension(
            'other', None, OtherRunner, None)
        driver_managers = [
            (PluginManager.TEST_RUNNER, ExtensionManager.make_test_instance(
                [default, other], namespace=PluginManager.TEST_RUNNER)),
        ]
        plugin_manager = PluginManager.testing_plugin_manager(
            hook_managers=(), driver_managers=driver_managers)
        parser = create_argument_parser()
        plugin_manager.add_plugin_arguments(parser)

        # When
        args = parser.parse_args(['--runner', 'other'])
        runner = plugin_manager.get_driver(plugin_manager.TEST_RUNNER, args)

        # Then
        self.assertIsInstance(runner, OtherRunner)

    def test_no_driver_hook_found(self):
        # Given
        driver_managers = [
            (PluginManager.TEST_RUNNER, ExtensionManager.make_test_instance(
                [], namespace=PluginManager.TEST_RUNNER)),
        ]
        plugin_manager = PluginManager.testing_plugin_manager(
            hook_managers=(), driver_managers=driver_managers)
        parser = ArgumentParser(add_help=False)

        # When
        plugin_manager.add_plugin_arguments(parser)

        # Then
        actions = parser._actions
        self.assertEqual(len(actions), 0)

    def test_environment_hook_options_no_plugins(self):
        # Given
        environment_manager = ExtensionManager.make_test_instance(
            [], namespace=PluginManager.ENVIRONMENT_HOOK,
        )
        hook_managers = [(PluginManager.ENVIRONMENT_HOOK, environment_manager)]
        plugin_manager = PluginManager.testing_plugin_manager(
            hook_managers=hook_managers, driver_managers=())
        parser = ArgumentParser(add_help=False)

        # When
        plugin_manager.add_plugin_arguments(parser)

        # Then
        actions = parser._actions
        self.assertEqual(len(actions), 0)

        # When
        args = parser.parse_args([])
        enabled_plugins = plugin_manager.get_enabled_hook_plugins(
            plugin_manager.ENVIRONMENT_HOOK, args)

        # Then
        self.assertEqual(enabled_plugins, [])

    def test_hook_plugin_none(self):
        class TestingPlugin(BaseTestingPlugin):

            @classmethod
            def from_args(cls, args, name, dest_prefix):
                return None

        # Given
        extension = Extension(
            'testing-plugin', None, TestingPlugin, None)
        environment_manager = ExtensionManager.make_test_instance(
            [extension], namespace=PluginManager.ENVIRONMENT_HOOK,
        )
        hook_managers = [(PluginManager.ENVIRONMENT_HOOK, environment_manager)]
        plugin_manager = PluginManager.testing_plugin_manager(
            hook_managers=hook_managers, driver_managers=())
        parser = ArgumentParser(add_help=False)
        args = parser.parse_args([])

        # When
        plugin = plugin_manager._create_hook_plugin(extension, args)

        # Then
        self.assertIsNone(plugin)
