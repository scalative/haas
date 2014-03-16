Getting Started
===============


Installing ``haas``
-------------------

``haas`` is currently only available from `the GitHub repository`_.  To
install haas, clone the repository and install using ``pip``::

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
