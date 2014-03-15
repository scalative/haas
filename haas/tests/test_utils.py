# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from mock import patch

import haas
from ..testing import unittest
from ..utils import configure_logging


class TestConfigureLogging(unittest.TestCase):

    @patch('logging.getLogger')
    def test_configure_logging(self, get_logger):
        configure_logging('debug')
        get_logger.assert_called_once_with(haas.__name__)
