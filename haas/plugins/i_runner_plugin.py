# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

import abc

from six import add_metaclass

from haas.utils import abstractclassmethod


@add_metaclass(abc.ABCMeta)
class IRunnerPlugin(object):

    @abstractclassmethod
    def from_args(cls, args, arg_prefix):
        """Construct the runner from parsed command line arguments.

        Parameters
        ----------
        args : argparse.Namespace
            The ``argparse.Namespace`` containing parsed arguments.
        arg_prefix : str
            The prefix used for arguments beloning solely to this plugin.

        """

    @abstractclassmethod
    def add_parser_arguments(self, parser, option_prefix, dest_prefix):
        pass
