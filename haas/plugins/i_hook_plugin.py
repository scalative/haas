# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
import abc


class IHookPlugin(abc.ABC):

    @abc.abstractmethod
    def setup(self):  # pragma: no cover
        pass

    @abc.abstractmethod
    def teardown(self):  # pragma: no cover
        pass

    @abc.abstractclassmethod
    def add_parser_arguments(cls, parser, name, option_prefix, dest_prefix):
        pass

    @abc.abstractclassmethod
    def from_args(cls, args, dest_prefix):
        pass
