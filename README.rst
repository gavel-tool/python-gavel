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
.. |docs| image:: https://readthedocs.org/projects/gavel/badge/?style=flat
    :target: https://readthedocs.org/projects/gavel
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/MGlauer/python-gavel.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/MGlauer/python-gavel

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/MGlauer/python-gavel?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/MGlauer/python-gavel

.. |requires| image:: https://requires.io/github/MGlauer/python-gavel/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/MGlauer/python-gavel/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/MGlauer/python-gavel/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/MGlauer/python-gavel

.. |version| image:: https://img.shields.io/pypi/v/gavel.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/gavel

.. |commits-since| image:: https://img.shields.io/github/commits-since/MGlauer/python-gavel/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/MGlauer/python-gavel/compare/v0.0.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/gavel.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/gavel

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/gavel.svg
    :alt: Supported versions
    :target: https://pypi.org/project/gavel

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/gavel.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/gavel


.. end-badges

A toolset for prover independent premise selection. Template generated with cookiecutter-pylibrary.

Installation
============

::

    pip install gavel

Documentation
=============


https://gavel.readthedocs.io/


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
