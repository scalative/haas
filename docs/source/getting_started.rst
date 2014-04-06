Getting Started
===============


Installing ``haas``
-------------------

``haas`` can be easily installed using ``pip``::

    $ pip install haas

For development versions, the source is available from `the GitHub
repository`_.  To install haas from GitHub, clone the repository and
install using ``pip``::

    $ git clone https://github.com/sjagoe/haas.git
    $ cd haas
    $ python setup.py sdist
    $ pip install dist/haas*.egg


.. _`the GitHub repository`: https://github.com/sjagoe/haas


Using ``haas``
--------------

To use the basic test discovery feature of ``haas``, simply invoke it at
the top-level of a project; this should be enough to detect and run all
unit tests::

    $ haas
    .......................................................................................................
    ----------------------------------------------------------------------
    Ran 103 tests in 0.116s

    OK

``haas`` supports some of the same options as Python's ``unittest``
runner, with one major difference: the starting directory (or package
name) for test discovery is simply specified on the command line::

    $ haas haas/tests
    .......................................................................................................
    ----------------------------------------------------------------------
    Ran 103 tests in 0.116s

    OK
    $ haas haas.tests
    .......................................................................................................
    ----------------------------------------------------------------------
    Ran 103 tests in 0.116s

    OK


For the currently available options, use the ``--help`` option::

    $ haas --help
    usage: haas [-h] [-v | -q] [-f] [-b] [-p PATTERN]
                [-t TOP_LEVEL_DIRECTORY]
                [--log-level {critical,fatal,error,warning,info,debug}]
                [start]

    positional arguments:
      start                 Directory or dotted package/module name to start
                            searching for tests

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         Verbose output
      -q, --quiet           Quiet output
      -f, --failfast        Stop on first fail or error
      -b, --buffer          Buffer stdout and stderr during tests
      -p PATTERN, --pattern PATTERN
                            Pattern to match tests ('test*.py' default)
      -t TOP_LEVEL_DIRECTORY, --top-level-directory TOP_LEVEL_DIRECTORY
                            Top level directory of project (defaults to start
                            directory)
      --log-level {critical,fatal,error,warning,info,debug}
                            Log level for haas logging


Discovering tests by a test name only
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``haas`` is able to discover a subset of the tests when just a test name
(or any sub-section of a dotted module name) is given on the command
line.

For example, to run all test methods called ``test_method``, the
following would work::

    $ haas -v test_method
    test_method (haas.tests._test_cases.TestCase) ... ok
    test_method (haas.tests.test_loader.TestCaseSubclass) ... ok
    test_method (haas.tests.test_discoverer.FilterTestCase) ... ok

    ----------------------------------------------------------------------
    Ran 3 tests in 0.000s

    OK

Note that three tests in three different modules have been run. The
string ``test_method`` is matched at any point in the name
``<package>.<module>.<class>.<method>`` and across all loadable tests in
the project.  To restrict this to a single test, we can use the class
name as an additional matching parameter::

    $ haas -v FilterTestCase.test_method
    test_method (haas.tests.test_discoverer.FilterTestCase) ... ok

    ----------------------------------------------------------------------
    Ran 1 test in 0.000s

    OK
