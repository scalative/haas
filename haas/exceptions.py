# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals


class HaasException(Exception):
    pass


class DotInModuleNameError(HaasException):
    pass


class PluginError(HaasException):
    pass
