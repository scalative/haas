# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import unicode_literals

import sys


def get_module_by_name(name):
    """Import a module and return the imported module object.

    """
    __import__(name)
    return sys.modules[name]


def find_module_by_name(full_name):
    module_name = full_name
    module_attributes = []
    while True:
        try:
            module = get_module_by_name(module_name)
        except ImportError:
            if '.' in module_name:
                module_name, attribute = module_name.rsplit('.', 1)
                module_attributes.append(attribute)
            else:
                raise
        else:
            break
    return module, list(reversed(module_attributes))
