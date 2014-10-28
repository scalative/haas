# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from collections import OrderedDict
import logging

from stevedore.driver import DriverManager
from stevedore.extension import ExtensionManager

logger = logging.getLogger(__name__)


class PluginManager(object):

    ENVIRONMENT_HOOK = 'haas.hooks.environment'

    TEST_RUNNER = 'haas.runner'

    _help = {
        TEST_RUNNER: 'Test runner implementation to use.'
    }

    def __init__(self):
        self.hook_managers = OrderedDict()
        self.hook_managers[self.ENVIRONMENT_HOOK] = ExtensionManager(
            namespace=self.ENVIRONMENT_HOOK,
            invoke_on_load=True,
        )

        self.driver_managers = OrderedDict()
        self.driver_managers[self.TEST_RUNNER] = ExtensionManager(
            namespace=self.TEST_RUNNER,
        )

    @classmethod
    def testing_plugin_manager(cls, hook_managers):
        plugin_manager = cls.__new__(cls)
        plugin_manager.hook_managers = hook_managers
        return plugin_manager

    def _filter_enabled_plugins(self, extension):
        if extension.obj.enabled:
            return extension.obj
        return None

    def _add_hook_extension_arguments(self, extension, parser):
        extension.obj.add_parser_arguments(parser)

    def _configure_hook_extension(self, extension, args):
        extension.obj.configure(args)

    def _namespace_to_option(self, namespace):
        parts = namespace.split('.')
        option = '--{}'.format('-'.join(parts))
        dest = '_'.join(parts)
        return option, dest

    def add_plugin_arguments(self, parser):
        for manager in self.hook_managers.values():
            if len(list(manager)) == 0:
                continue
            manager.map(self._add_hook_extension_arguments, parser)
        for namespace, manager in self.driver_managers.items():
            choices = list(sorted(manager.names()))
            if len(choices) == 0:
                continue
            option, dest = self._namespace_to_option(namespace)
            parser.add_argument(
                option, help=self._help[namespace], dest=dest,
                choices=choices, default='default')

    def configure_plugins(self, args):
        for manager in self.hook_managers.values():
            if len(list(manager)) == 0:
                continue
            manager.map(self._configure_hook_extension, args)

    def get_enabled_hook_plugins(self, hook):
        manager = self.hook_managers[hook]
        if len(list(manager)) == 0:
            return []
        return [plugin for plugin in manager.map(self._filter_enabled_plugins)
                if plugin is not None]

    def get_driver(self, namespace, args):
        option, dest = self._namespace_to_option(namespace)
        driver_name = getattr(args, dest, 'default')
        driver_manager = DriverManager(
            namespace, driver_name,
        )
        return driver_manager.driver
