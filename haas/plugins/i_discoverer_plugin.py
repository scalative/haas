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
class IDiscovererPlugin(object):

    @abstractclassmethod
    def from_args(cls, args, arg_prefix, loader):
        """Construct the discoverer from parsed command line arguments.

        Parameters
        ----------
        args : argparse.Namespace
            The ``argparse.Namespace`` containing parsed arguments.
        arg_prefix : str
            The prefix used for arguments beloning solely to this plugin.
        loader : haas.loader.Loader
            The test loader used to construct TestCase and TestSuite instances.

        """

    @abstractclassmethod
    def add_parser_arguments(cls, parser, option_prefix, dest_prefix):
        """Add options for the plugin to the main argument parser.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            The parser to extend
        option_prefix : str
            The prefix that option strings added by this plugin should use.
        dest_prefix : str
            The prefix that ``dest`` strings for options added by this
            plugin should use.

        """

    @abstractmethod
    def discover(self, start, top_level_directory=None, pattern=None):
        """Do test case discovery.

        This is the top-level entry-point for test discovery.

        If the ``start`` argument is a drectory, then ``haas`` will
        discover all tests in the package contained in that directory.

        If the ``start`` argument is not a directory, it is assumed to
        be a package or module name and tests in the package or module
        are loaded.

        FIXME: This needs a better description.

        Parameters
        ----------
        start : str
            The directory, package, module, class or test to load.
        top_level_directory : str
            The path to the top-level directoy of the project.  This is
            the parent directory of the project'stop-level Python
            package.
        pattern : str
            The glob pattern to match the filenames of modules to search
            for tests.

        """
