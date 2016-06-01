# -*- coding: utf-8 -*-
# Copyright (c) 2013-2016 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

import logging

from .base_hook_plugin import BaseHookPlugin
from haas import NullHandler


class SuppressLogging(BaseHookPlugin):

    def __init__(self, *args, **kwargs):
        super(SuppressLogging, self).__init__(*args, **kwargs)
        self._loggers = {}

    @classmethod
    def _get_enabling_option_string(cls, name, dest_prefix):
        enabling_option = '--suppress-logging'
        enabling_dest = 'with_{0}'.format(dest_prefix)
        return enabling_option, enabling_dest

    def _suppress_logger(self, logger):
        self._loggers[logger] = handlers = logger.handlers[:]
        for handler in handlers:
            logger.removeHandler(handler)
        logger.addHandler(NullHandler())

    def _restore_logger(self, logger, old_handlers):
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        for handler in old_handlers:
            logger.addHandler(handler)

    def setup(self):
        root_logger = logging.getLogger()
        self._suppress_logger(root_logger)
        for logger in logging.Logger.manager.loggerDict.values():
            if isinstance(logger, logging.PlaceHolder):
                continue
            if len(logger.handlers) > 0 and logger not in self._loggers:
                self._suppress_logger(logger)

    def teardown(self):
        for logger, old_handlers in self._loggers.items():
            self._restore_logger(logger, old_handlers)
        self._loggers.clear()
