====================
 ``haas`` CHANGELOG
====================

Changes since version 0.9.0
===========================

Packaging
---------

* Replace ``setup.py`` with ``pyproject.toml`` (#199).

Bugs Fixed
---------

* Fix deprecation warnings under Python 3.12 (#200).


Version 0.9.0
=============

Behaviour changes
-----------------

* Dropped support for long out-of-support Python versions prior to
  Python 3.7 (#188, #194, #193):
  * Python 2.6
  * Python 2.7
  * Python 3.3
  * Python 3.4
  * Python 3.5
  * Python 3.6

Enhancements
------------

* Allow log-level names to be case-insensitive (#166)
* Add command-line argument for Python warning levels (#174)
* Fixed compatibility with Python 3.12 (#194)
* Added testing of Python 3.6 and 3.7 (#175)
* Added testing of Python 3.8 and 3.9 and 3.10 (#192)
* Added testing of Python 3.11 and 3.12 (#193)

Bugs Fixed
----------

* Adding missing LICENSE and docs to source distribution (#185)
* Fix path handling and normalization on MacOS when discovering tests
  by directory (#194, #193)


Version 0.8.0
=============

Enhancements
------------

* The ParallelTestRunner now has an option to force a new process for
  each test case, enforcing isolation between tests (#138).
* A new output plugin summarizing the slowest tests and overall test
  speed (#90).

Bugs Fixed
----------

* Haas now correctly specifies its Python 2.6 dependencies (#137).
* Haas no longer passes the test name to TestCase using a keyword
  argument, allowing it to create test cases from subclasses that
  rename arguments (#135).
* Haas no longer emits errors loading plugins when running on Windows
  (#141).
* Haas no longer ignores tests derived from ``unittest.TestCase`` when
  ``unittest2`` is installed (#143).
* Haas no longer propagates its internal logging to the root logger,
  avoiding polluting logs when running tests that have a logger
  configured (#148).
* The sort order of plugins is now stable, producing consistent output
  (#149).
* Spelling of class ``ResultCollector`` is now correct (#153).
* Fix crash under Python 3 on Windows (#163).


Version 0.7.0
=============

Behaviour changes
-----------------

* Following the stdlib unittest runner behaviour, ``__init__.py`` is
  required in packages searched for tests (#98, #113).

Bugs Fixed
----------

* The parallel test runner now returns correct results in the presence
  of a module import error (#129).
* Fixed a UnicodeDecodeError when a traceback contains Unicode
  characters (e.g. Unicode filesystem paths) (#132).

Enhancements
------------

* Allow multiple result handler plugins to be enabled at the same
  time (#92).


Version 0.6.2
=============

Packaging
---------

* Package tests in the haas distribution so that they can actually be
  run (#125).


Version 0.6.1
=============

Packaging
---------

* Tests can be run on an installed haas tree (PR #112).

Bugs Fixed
----------

* Fix crash if a non-ImportError occurs at the top-level of a test
  module (#97).
* Tests are no longer ignored if there is an import error in the
  top-level package (#98).

Bugs closed
-----------

* Haas no longer crashes on temporary emac recovery filed (fixed in a
  prior release; closed #91).


Version 0.6.0
=============

Enhancements
------------

* Haas now supports replacing the test discovery mechanism with plugins
  (#106).


Version 0.5.1
=============

Bugs Fixed
----------

* With ``v0.5.0``, wheels were only valid on CPython 3.4, despite being
  labelled universal.  In ``v0.5.1``, wheels are built correctly for all
  supported versions.


Version 0.5.0
=============

Enhancements
------------

* Added a plugin manager based on ``stevedore``
  https://pypi.python.org/pypi/stevedore (#16).
* Decouple test result collection from test result presentation (PR
  #83).
* Added a basic parallel test runner plugin (#78, #88).


Version 0.4.1
=============

* Fixed packaging error causing v0.4.0 to contain an invalid (but
  unused) file.


Version 0.4.0
=============

Bugs Fixed
----------

* Never filter out ``ModuleImportErrors``, even if using substring
  filtering on test name (#70).
* Fix running tests when given a full file path on the command line
  (#72).


Version 0.3.1
=============

Bugs Fixed
----------

* ``haas`` no longer crashes if there is a directory with a dot in the
  name containing python modules (#64).


Version 0.3.0
=============

Bugs Fixed
----------

* ``haas`` no longer crashes in Python 2.x when there are non-package
  directories under discovery (#38).


Release 0.2.3
=============

Enhancements
------------

* It is now possible to discover the version of ``haas`` from the
  command line (#53)!
* ``haas`` now supports the ``--failfast`` option (#47).
* ``haas`` now supports multiple ``start`` directories (#49)


Release 0.2.2
=============

Enhancements
------------

* ``haas`` now supports Python 3.2


Release 0.2.1
=============

Enhancements
------------

* ``haas`` now supports Python 3.4


Release 0.2.0
=============

Enhancements
------------

* ``haas`` now supports discovering tests by a substring of the test
  name, such as ``haas module_name.ClassName`` or ``haas
  ClassName.test_method`` or simply ``haas test_method``.
* ``haas`` uses a simple extension to the ``unittest.TextTestRunner``
  that shows the progress of the test run and a timestamp of when each
  test was started.  This is useful for projects with a very large
  number of tests that take more than a few minutes to run.


Release 0.1.0
=============

The initial release of ``haas``.

Features
--------

* ``haas`` is fully compatible with tests written using
  ``unittest.TestCase``.
* ``haas`` has a test discovery and loading mechanism to allow more
  advanced test discovery.  Most notably in this release is the unified
  interface for running a single test and discovering multiple tests.
* ``haas`` is able to infer the top level directory from within a
  project, resulting in the tests running in the correct environment and
  correctly supporting test modules that make use of relative imports.
