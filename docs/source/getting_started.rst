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
