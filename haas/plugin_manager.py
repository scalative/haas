# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import unicode_literals

from .utils import find_module_by_name


class PluginManager(object):

    def load_plugin_class(self, class_spec):
        if class_spec is None:
            return None
        try:
            module, module_attributes = find_module_by_name(class_spec)
        except ImportError:
            return None
        if len(module_attributes) != 1:
            return None
        klass = getattr(module, module_attributes[0], None)
        if klass is None:
            return None
        return klass

    def load_plugin(self, class_spec):
        klass = self.load_plugin_class(class_spec)
        if klass is None:
            return None
        return klass()
