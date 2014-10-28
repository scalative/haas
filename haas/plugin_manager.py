# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

import sys
import logging

if sys.version_info < (2, 7):
    from ordereddict import OrderedDict
else:
    from collections import OrderedDict

from stevedore.driver import DriverManager
from stevedore.extension import ExtensionManager

logger = logging.getLogger(__name__)


class PluginManager(object):

    ENVIRONMENT_HOOK = 'haas.hooks.environment'

    TEST_RUNNER = 'haas.runner'

    _help = {
        TEST_RUNNER: 'Test runner implementation to use.'
    }

    _namespace_to_option_parts = {
        TEST_RUNNER: ['runner'],
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
    def testing_plugin_manager(cls, hook_managers, driver_managers):
        plugin_manager = cls.__new__(cls)
        plugin_manager.hook_managers = OrderedDict(hook_managers)
        plugin_manager.driver_managers = OrderedDict(driver_managers)
        return plugin_manager

    def _filter_enabled_plugins(self, extension):
        if extension.obj.enabled:
            return extension.obj
        return None

    def _add_hook_extension_arguments(self, extension, parser):
        extension.obj.add_parser_arguments(parser)

    def _configure_hook_extension(self, extension, args):
        extension.obj.configure(args)

    def _add_driver_extension_arguments(self, extension, parser, option_prefix,
                                        dest_prefix):
        extension.plugin.add_parser_arguments(
            parser, option_prefix, dest_prefix)

    def _namespace_to_option(self, namespace):
        parts = self._namespace_to_option_parts[namespace]
        option = '--{0}'.format('-'.join(parts))
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
            option_prefix = '{0}-'.format(option)
            dest_prefix = '{0}_'.format(dest)
            manager.map(self._add_driver_extension_arguments,
                        parser, option_prefix, dest_prefix)

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
        dest_prefix = '{0}_'.format(dest)
        driver_name = getattr(args, dest, 'default')
        driver_manager = DriverManager(
            namespace, driver_name,
        )
        return driver_manager.driver.from_args(args, dest_prefix)
