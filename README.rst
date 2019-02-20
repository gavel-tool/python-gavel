========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/python-chisel/badge/?style=flat
    :target: https://readthedocs.org/projects/python-chisel
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/MGlauer/python-chisel.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/MGlauer/python-chisel

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/MGlauer/python-chisel?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/MGlauer/python-chisel

.. |requires| image:: https://requires.io/github/MGlauer/python-chisel/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/MGlauer/python-chisel/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/MGlauer/python-chisel/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/MGlauer/python-chisel

.. |version| image:: https://img.shields.io/pypi/v/chisel.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/chisel

.. |commits-since| image:: https://img.shields.io/github/commits-since/MGlauer/python-chisel/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/MGlauer/python-chisel/compare/v0.0.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/chisel.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/chisel

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/chisel.svg
    :alt: Supported versions
    :target: https://pypi.org/project/chisel

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/chisel.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/chisel


.. end-badges

A toolset for prover independent premise selection. Template generated with cookiecutter-pylibrary.

* Free software: BSD 2-Clause License

Installation
============

::

    pip install chisel

Documentation
=============


https://python-chisel.readthedocs.io/


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
