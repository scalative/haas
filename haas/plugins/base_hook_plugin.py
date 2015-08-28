# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from .i_hook_plugin import IHookPlugin


class BaseHookPlugin(IHookPlugin):
    """The base implementation of hook plugins.

    """

    def __init__(self, name, enabled, enabling_option):
        self.name = name
        self.enabled = enabled
        self.enabling_option = 'with_{0}'.format(name.replace('-', '_'))

    @classmethod
    def _get_enabling_option_string(cls, name, dest_prefix):
        enabling_option = '--with-{0}'.format(name)
        enabling_dest = 'with_{0}'.format(dest_prefix)
        return enabling_option, enabling_dest

    @classmethod
    def add_parser_arguments(cls, parser, name, option_prefix, dest_prefix):
        enabling_option, enabling_dest = cls._get_enabling_option_string(
            name, dest_prefix)
        parser.add_argument(enabling_option,
                            action='store_true',
                            help='Enable the {0} plugin'.format(name),
                            dest=enabling_dest)

    @classmethod
    def from_args(cls, args, name, dest_prefix):
        enabling_option, enabling_dest = cls._get_enabling_option_string(
            name, dest_prefix)
        enabled = getattr(args, enabling_dest, False)
        return cls(name=name, enabled=enabled, enabling_option=enabling_dest)
