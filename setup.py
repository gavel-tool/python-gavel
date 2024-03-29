#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import os
import re
import subprocess
import sys
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import relpath
from os.path import splitext

from setuptools import Extension
from setuptools import find_packages
from setuptools import setup
from setuptools.command.build_ext import build_ext


def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ) as fh:
        return fh.read()


# Enable code coverage for C code: we can't use CFLAGS=-coverage in tox.ini, since that may mess with compiling
# dependencies (e.g. numpy). Therefore we set SETUPPY_CFLAGS=-coverage in tox.ini and copy it to CFLAGS here (after
# deps have been safely installed).
if "TOXENV" in os.environ and "SETUPPY_CFLAGS" in os.environ:
    os.environ["CFLAGS"] = os.environ["SETUPPY_CFLAGS"]


class optional_build_ext(build_ext):
    """Allow the building of C extensions to fail."""

    def run(self):
        try:
            build_ext.run(self)
        except Exception as e:
            self._unavailable(e)
            self.extensions = []  # avoid copying missing files (it would fail).

    def _unavailable(self, e):
        print("*" * 80)
        print(
            """WARNING:

    An optional code optimization (C extension) could not be compiled.

    Optimizations for this package will not be available!
        """
        )

        print("CAUSE:")
        print("")
        print("    " + repr(e))
        print("*" * 80)


setup(
    name="gavel",
    version="0.1.5",
    license="AGPL",
    description="A toolset for prover independent premise selection. Template generated with cookiecutter-pylibrary.",
    long_description="%s\n%s"
    % (
        re.compile("^.. start-badges.*^.. end-badges", re.M | re.S).sub(
            "", read("README.rst")
        ),
        re.sub(":[a-z]+:`~?(.*?)`", r"``\1``", read("CHANGELOG.rst")),
    ),
    author="Martin Glauer",
    author_email="martin.glauer@ovgu.de",
    url="https://github.com/MGlauer/python-gavel",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        # uncomment if you test on these interpreters:
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: Stackless',
        "Topic :: Utilities",
    ],
    project_urls={
        "Documentation": "https://python-gavel.readthedocs.io/",
        "Changelog": "https://python-gavel.readthedocs.io/en/latest/changelog.html",
        "Issue Tracker": "https://github.com/MGlauer/python-gavel/issues",
    },
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=[
        # eg: 'aspectlib==1.1.1', 'six>=1.7',
        "click",
        "lark-parser",
        "pre-commit",
        "graphviz",
        "pytest",
        "requests",
        "lxml",
        "beautifulsoup4",
    ],
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
        "dev": ["black", "isort", "pre-commit", "sphinx-click"]
    },
    entry_points={},
    cmdclass={"build_ext": optional_build_ext},
    ext_modules=[
        Extension(
            splitext(relpath(path, "src").replace(os.sep, "."))[0],
            sources=[path],
            include_dirs=[dirname(path)],
        )
        for root, _, _ in os.walk("src")
        for path in glob(join(root, "*.c"))
    ],
)
