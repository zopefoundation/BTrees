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

import os
import sys
from distutils.errors import CCompilerError
from distutils.errors import DistutilsExecError
from distutils.errors import DistutilsPlatformError

from setuptools import Extension
from setuptools import find_packages
from setuptools import setup
from setuptools.command.build_ext import build_ext


version = '5.3.dev0'

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

# Set up dependencies for the BTrees package
base_btrees_depends = [
    "src/BTrees/BTreeItemsTemplate.c",
    "src/BTrees/BTreeModuleTemplate.c",
    "src/BTrees/BTreeTemplate.c",
    "src/BTrees/BucketTemplate.c",
    "src/BTrees/MergeTemplate.c",
    "src/BTrees/SetOpTemplate.c",
    "src/BTrees/SetTemplate.c",
    "src/BTrees/TreeSetTemplate.c",
    "src/BTrees/sorters.c",
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

KEY_H = "src/BTrees/%skeymacros.h"
VALUE_H = "src/BTrees/%svaluemacros.h"


def BTreeExtension(family):
    key = family[0]
    value = family[1]
    name = "BTrees._%sBTree" % family
    sources = ["src/BTrees/_%sBTree.c" % family]
    kwargs = {"include_dirs": [os.path.join('include', 'persistent')]}
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
    # 5.0.0 added zope.interface.common.collections
    'zope.interface >= 5.0.0',
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
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
          "Programming Language :: Python :: 3.12",
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
      project_urls={
        'Documentation': 'https://btrees.readthedocs.io',
        'Issue Tracker': 'https://github.com/zopefoundation/BTrees/issues',
        'Sources': 'https://github.com/zopefoundation/BTrees',
      },
      license="ZPL 2.1",
      platforms=["any"],
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      ext_modules=ext_modules,
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
      python_requires='>=3.7',
      install_requires=REQUIRES,
      cmdclass={
          'build_ext': optional_build_ext,
      },
      entry_points="""\
      """
)
