# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
import logging

__version__ = '0.10.0.dev1'


class NullHandler(logging.Handler):  # pragma: no cover
    def emit(self, record):
        pass


logger = logging.getLogger(__name__)
logger.propagate = False
logger.addHandler(NullHandler())
