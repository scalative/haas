# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from abc import ABCMeta, abstractmethod

from six import add_metaclass

from haas.utils import abstractclassmethod


@add_metaclass(ABCMeta)
class IResultHandlerPlugin(object):

    @abstractclassmethod
    def from_args(cls, args, name, dest_prefix, test_count):
        """Construct the result handler from parsed command line arguments.

        Parameters
        ----------
        args : argparse.Namespace
            The ``argparse.Namespace`` containing parsed arguments.
        name : str
            The name of the plugin.
        dest_prefix : str
            The prefix that ``dest`` strings for options added by this
            plugin should use.
        test_count : int
            The totel number of tests discovered.

        """

    @abstractclassmethod
    def add_parser_arguments(cls, parser, name, option_prefix, dest_prefix):
        """Add options for the plugin to the main argument parser.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            The parser to extend
        name : str
            The name of the plugin.
        option_prefix : str
            The prefix that option strings added by this plugin should use.
        dest_prefix : str
            The prefix that ``dest`` strings for options added by this
            plugin should use.

        """

    @abstractmethod
    def start_test(self, test):
        """Perform tasks at the start of a single test.

        """

    @abstractmethod
    def stop_test(self, test):
        """Perform tasks at the end of a single test.

        """

    @abstractmethod
    def start_test_run(self):
        """Perform tasks at the very start of the test run.

        """

    @abstractmethod
    def stop_test_run(self):
        """Perform tasks at the very end of the test run.

        """

    @abstractmethod
    def __call__(self, result):
        """Handle the completed test result ``result``.

        """
