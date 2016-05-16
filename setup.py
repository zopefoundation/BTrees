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

__version__ = '4.3.1'

import os
import platform
import sys

from setuptools import Extension
from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = (open(os.path.join(here, 'README.rst')).read()
          + '\n\n' +
          open(os.path.join(here, 'CHANGES.rst')).read())

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

FLAVORS = {"O": "object", "I": "int", "F": "float", 'L': 'int'}
#XXX should 'fs' be in ZODB instead?
FAMILIES = ("OO", "IO", "OI", "II", "IF", "fs", "LO", "OL", "LL", "LF")

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

py_impl = getattr(platform, 'python_implementation', lambda: None)
pure_python = os.environ.get('PURE_PYTHON', False)
is_pypy = py_impl() == 'PyPy'
is_jython = 'java' in sys.platform

# Jython cannot build the C optimizations, while on PyPy they are
# anti-optimizations (the C extension compatibility layer is known-slow,
# and defeats JIT opportunities).
if pure_python or is_pypy or is_jython:
    ext_modules = []
else:

    ext_modules = [BTreeExtension(family) for family in FAMILIES]

if sys.version_info[0] >= 3:
    REQUIRES = [
        'persistent>=4.0.4',
        'zope.interface',
    ]
else:
    REQUIRES = [
        'persistent',
        'zope.interface',
    ]
TESTS_REQUIRE = REQUIRES + ['transaction']

setup(name='BTrees',
      version=__version__,
      description='Scalable persistent object containers',
      long_description=README,
      classifiers=[
        "Development Status :: 6 - Mature",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
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
      url="http://packages.python.org/BTrees",
      license="ZPL 2.1",
      platforms=["any"],
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      ext_modules = ext_modules,
      setup_requires=['persistent'],
      extras_require = {
        'test': TESTS_REQUIRE,
        'ZODB': ['ZODB'],
        'testing': TESTS_REQUIRE + ['nose', 'coverage'],
        'docs': ['Sphinx', 'repoze.sphinx.autointerface'],
      },
      test_suite="BTrees.tests",
      tests_require=TESTS_REQUIRE,
      install_requires=REQUIRES,
      entry_points = """\
      """
     )
