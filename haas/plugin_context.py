# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals


class PluginContext(object):
    """Handles correct setup and teardown of multiple plugins.

    """

    def __init__(self, hooks=None, **kwargs):
        super(PluginContext, self).__init__(**kwargs)
        if hooks is None:
            hooks = []
        self.hooks = tuple(hook for hook in hooks if hook is not None)

    def __enter__(self):
        self.setup()

    def __exit__(self, exc_type, exc_value, traceback):
        self.teardown()

    def setup(self):
        for hook in self.hooks:
            hook.setup()

    def teardown(self):
        for hook in reversed(self.hooks):
            hook.teardown()
