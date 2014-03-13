# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import unicode_literals

from .environment import Environment


class HaasApplication(object):

    def __init__(self, discoverer, runner, environment=None, **kwargs):
        super(HaasApplication, self).__init__(**kwargs)
        self.discoverer = discoverer
        self.runner = runner
        if environment is None:
            environment = Environment()
        self.global_environment = environment

    def run(self, args):
        with self.global_environment:
            suite = self.discoverer.discover(
                start=args.start,
                top_level_directory=args.top_level_directory,
                pattern=args.pattern,
            )
            result = self.runner.run(suite)
            return not result.wasSuccessful()
