##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import print_function
version = '4.7.1'

import os
import sys

from distutils.errors import CCompilerError
from distutils.errors import DistutilsExecError
from distutils.errors import DistutilsPlatformError

from setuptools import Extension
from setuptools import find_packages
from setuptools import setup
from setuptools.command.build_ext import build_ext


def _read(fname):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, fname)) as f:
        return f.read()


README = _read("README.rst") + '\n\n' + _read('CHANGES.rst')


class optional_build_ext(build_ext):
    """This class subclasses build_ext and allows
       the building of C extensions to fail.
    """
    def run(self):
        try:
            build_ext.run(self)
        except DistutilsPlatformError as e:
            self._unavailable(e)

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except (CCompilerError, DistutilsExecError, OSError) as e:
            self._unavailable(e)

    def _unavailable(self, e):
        print('*' * 80)
        print("""WARNING:
        An optional code optimization (C extension) could not be compiled.
        Optimizations for this package will not be available!""")
        print()
        print(e)
        print('*' * 80)
        if 'bdist_wheel' in sys.argv and not os.environ.get("PURE_PYTHON"):
            # pip uses bdist_wheel by default, and hides the error output.
            # Let this error percolate up so the user can see it.
            # pip will then go ahead and run 'setup.py install' directly.
            raise

# Include directories for C extensions
# Sniff the location of the headers in 'persistent' or fall back
# to local headers in the include sub-directory


class ModuleHeaderDir(object):

    def __init__(self, require_spec, where='..'):
        # By default, assume top-level pkg has the same name as the dist.
        # Also assume that headers are located in the package dir, and
        # are meant to be included as follows:
        #    #include "module/header_name.h"
        self._require_spec = require_spec
        self._where = where

    def __str__(self):
        from pkg_resources import require
        from pkg_resources import resource_filename
        require(self._require_spec)
        path = resource_filename(self._require_spec, self._where)
        return os.path.abspath(path)


include = [ModuleHeaderDir('persistent')]

# Set up dependencies for the BTrees package
base_btrees_depends = [
    "BTrees/BTreeItemsTemplate.c",
    "BTrees/BTreeModuleTemplate.c",
    "BTrees/BTreeTemplate.c",
    "BTrees/BucketTemplate.c",
    "BTrees/MergeTemplate.c",
    "BTrees/SetOpTemplate.c",
    "BTrees/SetTemplate.c",
    "BTrees/TreeSetTemplate.c",
    "BTrees/sorters.c",
    ]

FLAVORS = {
    "O": "object",
    "F": "float",
    "I": "int", # Signed 32-bit
    "L": "int", # Signed 64-bit
    "U": "int", # Unsigned 32-bit
    "Q": "int"  # Unsigned 64-bit (from the printf "q" modifier for quad_t)
}
# XXX should 'fs' be in ZODB instead?
FAMILIES = (
    # Signed 32-bit keys
    "IO", # object value
    "II", # self value
    "IF", # float value
    "IU", # opposite sign value
    # Unsigned 32-bit keys
    "UO", # object value
    "UU", # self value
    "UF", # float value
    "UI", # opposite sign value
    # Signed 64-bit keys
    "LO", # object value
    "LL", # self value
    "LF", # float value
    "LQ", # opposite sign value
    # Unsigned 64-bit keys
    "QO", # object value
    "QQ", # self value
    "QF", # float value
    "QL", # opposite sign value
    # Object keys
    "OO", # object
    "OI", # 32-bit signed
    "OU", # 32-bit unsigned
    "OL", # 64-bit signed
    "OQ", # 64-bit unsigned
    "fs",
)

KEY_H = "BTrees/%skeymacros.h"
VALUE_H = "BTrees/%svaluemacros.h"


def BTreeExtension(family):
    key = family[0]
    value = family[1]
    name = "BTrees._%sBTree" % family
    sources = ["BTrees/_%sBTree.c" % family]
    kwargs = {"include_dirs": include}
    if family != "fs":
        kwargs["depends"] = (base_btrees_depends + [KEY_H % FLAVORS[key],
                                                    VALUE_H % FLAVORS[value]])
    else:
        kwargs["depends"] = base_btrees_depends
    if key != "O":
        kwargs["define_macros"] = [('EXCLUDE_INTSET_SUPPORT', None)]
    return Extension(name, sources, **kwargs)


ext_modules = [BTreeExtension(family) for family in FAMILIES]

REQUIRES = [
    # 4.1.0 is the first version that PURE_PYTHON can run
    # ZODB tests
    'persistent >= 4.1.0',
    'zope.interface',
]

TESTS_REQUIRE = [
    # Our tests check for the new repr strings
    # generated in persistent 4.4.
    'persistent >= 4.4.3',
    'transaction',
    'zope.testrunner',
]

setup(name='BTrees',
      version=version,
      description='Scalable persistent object containers',
      long_description=README,
      classifiers=[
          "Development Status :: 6 - Mature",
          "License :: OSI Approved :: Zope Public License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: Implementation :: CPython",
          "Programming Language :: Python :: Implementation :: PyPy",
          "Framework :: ZODB",
          "Topic :: Database",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: Unix",
      ],
      author="Zope Foundation",
      author_email="zodb-dev@zope.org",
      url="https://github.com/zopefoundation/BTrees",
      license="ZPL 2.1",
      platforms=["any"],
      # Make sure we don't get 'terryfy' included in wheels
      # created on macOS CI
      packages=find_packages(include=("BTrees",)),
      include_package_data=True,
      zip_safe=False,
      ext_modules=ext_modules,
      setup_requires=['persistent'],
      extras_require={
          'test': TESTS_REQUIRE,
          'ZODB': [
              'ZODB',
          ],
          'docs': [
              'Sphinx',
              'repoze.sphinx.autointerface',
              'sphinx_rtd_theme',
          ],
      },
      test_suite="BTrees.tests",
      tests_require=TESTS_REQUIRE,
      install_requires=REQUIRES,
      cmdclass={
          'build_ext': optional_build_ext,
      },
      entry_points="""\
      """
)
