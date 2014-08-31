# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

import logging

from .plugins.i_plugin import IPlugin
from .exceptions import PluginError
from .utils import get_module_by_name, uncamelcase

logger = logging.getLogger(__name__)


class PluginManager(object):

    def load_plugin_class(self, class_spec):
        if class_spec is None or '.' not in class_spec:
            msg = 'Malformed plugin factory specification {0!r}'.format(
                class_spec)
            logger.error(msg)
            raise PluginError(msg)
        module_name, factory_name = class_spec.rsplit('.', 1)
        try:
            module = get_module_by_name(module_name)
        except ImportError:
            msg = 'Unable to import {0!r}'.format(class_spec)
            logger.exception(msg)
            raise PluginError(msg)
        try:
            klass = getattr(module, factory_name)
        except AttributeError:
            msg = 'Module %r has no attribute {0!r}'.format(
                module.__name__, factory_name)
            logger.error(msg)
            raise PluginError(msg)
        if not callable(klass):
            msg = 'Plugin factory {0!r} is not callable'.format(klass)
            logger.error(msg)
            raise PluginError(msg)
        return klass

    def load_plugin(self, plugin_factory):
        if not isinstance(plugin_factory, type) or \
                not issubclass(plugin_factory, IPlugin):
            raise PluginError('Plugin does not support IPlugin interface')
        plugin = plugin_factory()
        return plugin

    def add_parser_arguments_for_plugin(self, parser, klass):
        dest_part = uncamelcase(klass.__name__)
        name = dest_part.replace('_', '-')
        dest = 'with_{}'.format(dest_part)
        parser.add_argument(
            '--with-{}'.format(name),
            action='store_true',
            default=False,
            dest=dest,
            help='Enable {} plugin (default: disabled)'.format(klass.__name__),
        )
        parser.add_argument(
            '--no-{}'.format(name),
            action='store_false',
            dest=dest,
            help='Disable {} plugin (default: disabled)'.format(
                klass.__name__),
        )
        klass.add_parser_arguments(parser)
