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
from setuptools import setup
from setuptools.command.build_ext import build_ext


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
    "I": "int",  # Signed 32-bit
    "L": "int",  # Signed 64-bit
    "U": "int",  # Unsigned 32-bit
    "Q": "int"  # Unsigned 64-bit (from the printf "q" modifier for quad_t)
}
# XXX should 'fs' be in ZODB instead?
FAMILIES = (
    # Signed 32-bit keys
    "IO",  # object value
    "II",  # self value
    "IF",  # float value
    "IU",  # opposite sign value
    # Unsigned 32-bit keys
    "UO",  # object value
    "UU",  # self value
    "UF",  # float value
    "UI",  # opposite sign value
    # Signed 64-bit keys
    "LO",  # object value
    "LL",  # self value
    "LF",  # float value
    "LQ",  # opposite sign value
    # Unsigned 64-bit keys
    "QO",  # object value
    "QQ",  # self value
    "QF",  # float value
    "QL",  # opposite sign value
    # Object keys
    "OO",  # object
    "OI",  # 32-bit signed
    "OU",  # 32-bit unsigned
    "OL",  # 64-bit signed
    "OQ",  # 64-bit unsigned
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


setup(ext_modules=ext_modules,
      cmdclass={'build_ext': optional_build_ext})
