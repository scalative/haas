.. haas documentation master file, created by
   sphinx-quickstart on Sun Mar 16 15:00:51 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

====================================
 Welcome to the haas documentation!
====================================

``haas`` is a Python test runner that is backward-compatible with
Python's built-in unittest Test Cases, but is designed to support more
advanced features, such as project-specific plugins.


Introduction
============

``haas`` is intended to iron out some of the wrinkles in Python's
``unittest` test runner.  ``haas`` features and improved test discover
and loading mechanism, allowing the same base command to be used to
discover tests in packages as well as run individual test cases.  In the
future, ``haas`` will feature a plugin system allowing the use of
environment configuration plugins (e.g. configure Windows SxS manifests
or COM before running tests) or even plugins that run code between tests
(e.g. report on threads that are not cleaned up by code under test).

Unlike ``unittest``, ``haas`` is also usually safe to use within a
project's source tree as it features more robust detection of the
top-level directory of a project.


Contents:

.. toctree::
   :maxdepth: 2

   getting_started
   reference/modules

====================
 Indices and tables
====================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
