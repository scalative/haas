===================================
haas: Extensible Python Test Runner
===================================

.. image:: https://api.travis-ci.org/sjagoe/haas.png?branch=master
   :target: https://travis-ci.org/sjagoe/haas
   :alt: Build status


.. image:: https://coveralls.io/repos/sjagoe/haas/badge.png?branch=master
   :target: https://coveralls.io/r/sjagoe/haas?branch=master
   :alt: Coverage status


``haas`` is a Python test runner that is backward-compatible with Python's
built-in unittest Test Cases, but supports more advanced features, such
as project-specific plugins.


Feature Ideas
=============

* Default ``Loader``, ``TestSuite``, ``TestRunner``, ``TestResult``

  * Possible to override defaults using plugins

  * Defaults classes take options via command line or config file

* System-level plugins

  * Allow plugins to be easily contributed

  * Plugins loaded at startup before running any user code

  * Plugins optionally enabled and disabled through command line flags

    * Plugin options loaded before plugin functionality

  * Possible plugin functionality

    * Pre-testing environment configuration

    * Custom loader, runner, results collection, reporting, ???

* Project-level plugins

  * Allow projects to contribute project-specific plugins

  * Specified by command-line

  * Specified by config file

* Plugin config read from config file in project directory

  * Config file specified on command line


Copyright
=========

``haas`` is copyright 2013-2014 Simon Jagoe

The name ``haas`` is taken from the animal on the cover of O'Reilly's
Python Cookbook, a *springhaas* or *Pedetes capensis*.
