# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from collections import OrderedDict
import logging

from stevedore.extension import ExtensionManager

logger = logging.getLogger(__name__)


class PluginManager(object):

    ENVIRONMENT_HOOK = 'haas.hooks.environment'

    def __init__(self):
        self.plugin_managers = OrderedDict()
        self.plugin_managers[self.ENVIRONMENT_HOOK] = ExtensionManager(
            namespace=self.ENVIRONMENT_HOOK,
            invoke_on_load=True,
        )

    def _filter_enabled_plugins(self, extension):
        if extension.obj.is_enabled():
            return extension.obj
        return None

    def _add_extension_arguments(self, extension, parser):
        extension.obj.add_arguments(parser)

    def add_plugin_arguments(self, parser):
        for manager in self.plugin_managers.values():
            if len(list(manager)) == 0:
                continue
            manager.map(self._add_extension_arguments, parser)

    def get_enabled_plugins(self, hook):
        manager = self.plugin_managers[hook]
        if len(manager.extensions) == 0:
            return []
        return [plugin for plugin in manager.map(self._filter_enabled_plugins)
                if plugin is not None]
