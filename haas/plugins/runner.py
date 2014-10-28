# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from .i_runner_plugin import IRunnerPlugin
from ..testing import unittest


class TextTestRunner(IRunnerPlugin, unittest.TextTestRunner):

    @classmethod
    def from_args(cls, args, arg_prefix):
        return cls(
            verbosity=args.verbosity,
            failfast=args.failfast,
            buffer=args.buffer,
        )

    @classmethod
    def add_parser_arguments(self, parser, option_prefix, dest_prefix):
        pass
