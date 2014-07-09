====================
 ``haas`` CHANGELOG
====================


Version 0.3.1
=============

Bugs Fixed
----------

* ``haas`` no longer crashes if there is a directory with a dot in the
  name containing python modules (#64)


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
