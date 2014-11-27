===================================
haas: Extensible Python Test Runner
===================================

.. image:: https://pypip.in/wheel/haas/badge.png
   :target: https://pypi.python.org/pypi/haas/
   :alt: Wheel Status

.. image:: https://api.travis-ci.org/sjagoe/haas.png?branch=master
   :target: https://travis-ci.org/sjagoe/haas
   :alt: Build status

.. image:: https://coveralls.io/repos/sjagoe/haas/badge.png?branch=master
   :target: https://coveralls.io/r/sjagoe/haas?branch=master
   :alt: Coverage status


``haas`` is a Python test runner that is backward-compatible with Python's
built-in unittest Test Cases, but supports more advanced features, such
as project-specific plugins.


Features
========

* Runs ``unittest.TestCase`` based tests!

* Plugin system, based on stevedore_.

  * Still subject to change and revision to clean the plugin APIs.

  * Plugins for whole-test-run environment configuration (run before any
    client-code is imported).

  * Plugins for test result output formatting.

  * Plugins for test runner scheme (e.g. parallel runner)

* Generic test result collection, presentation & output handled by
  plugins.

* (Very) Basic parallel test run support.


.. _stevedore: https://pypi.python.org/pypi/stevedore

Missing (unittest) Features
===========================

* Does not support the ``unittest.load_tests`` protocol.

* Does not support subtests.


Future Features
===============

* Per-project config file

* Improve parallel test runner to allow conditional splitting of tests,
  or allow tests to be run in the main process.

* Improve plugin system

* More result output plugins/options (xunit, result summary)

* ... ?


Copyright
=========

``haas`` is copyright 2013-2014 Simon Jagoe

The name ``haas`` is taken from the animal on the cover of O'Reilly's
Python Cookbook, a *springhaas* or *Pedetes capensis*.
