``haas`` CHANGELOG
==================


Changes since 0.1.0
-------------------


Enhancements
~~~~~~~~~~~~

* ``haas`` now supports discovering tests by a substring of the test
  name, such as ``haas module_name.ClassName`` or ``haas
  ClassName.test_method`` or simply ``haas test_method``.


Release 0.1.0
-------------

The initial release of ``haas``.

Features
~~~~~~~~

* ``haas`` is fully compatible with tests written using
  ``unittest.TestCase``.
* ``haas`` has a test discovery and loading mechanism to allow more
  advanced test discovery.  Most notably in this release is the unified
  interface for running a single test and discovering multiple tests.
* ``haas`` is able to infer the top level directory from within a
  project, resulting in the tests running in the correct environment and
  correctly supporting test modules that make use of relative imports.