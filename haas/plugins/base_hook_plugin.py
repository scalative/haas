# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from haas.utils import uncamelcase
from .i_hook_plugin import IHookPlugin


class BaseHookPlugin(IHookPlugin):
    """The base implementation of hook plugins.

    """

    name = None
    enabled = False
    enabling_option = None

    def __init__(self, name=None):
        if name is None:
            name = uncamelcase(type(self).__name__, sep='-')
        self.name = name
        self.enabling_option = 'with_{0}'.format(name.replace('-', '_'))

    def add_parser_arguments(self, parser):
        parser.add_argument('--with-{0}'.format(self.name),
                            action='store_true',
                            help='Enable the {0} plugin'.format(self.name),
                            dest=self.enabling_option)

    def configure(self, args):
        if getattr(args, self.enabling_option, False):
            self.enabled = True
