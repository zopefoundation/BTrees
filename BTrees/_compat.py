##############################################################################
#
# Copyright (c) 2001-2012 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
import os
import sys

PYPY = hasattr(sys, 'pypy_version_info')
# We can and do build the C extensions on PyPy, but
# as of Persistent 4.2.5 the persistent C extension is not
# built on PyPy, so importing our C extension will fail anyway.
PURE_PYTHON = os.environ.get('PURE_PYTHON', PYPY)


if sys.version_info[0] < 3: #pragma NO COVER Python2

    PY2 = True
    PY3 = False

    int_types = int, long
    xrange = xrange
    def compare(x, y):
        if x is None:
            if y is None:
                return 0
            else:
                return -1
        elif y is None:
            return 1
        else:
            return cmp(x, y)

    _bytes = str
    def _ascii(x):
        return bytes(x)

else: #pragma NO COVER Python3

    PY2 = False
    PY3 = True

    int_types = int,
    xrange = range

    def compare(x, y):
        if x is None:
            if y is None:
                return 0
            else:
                return -1
        elif y is None:
            return 1
        else:
            return (x > y) - (y > x)

    _bytes = bytes
    def _ascii(x):
        return bytes(x, 'ascii')


def import_c_extension(mod_globals):
    import importlib
    c_module = None
    module_name = mod_globals['__name__']
    assert module_name.startswith('BTrees.')
    module_name = module_name.split('.')[1]
    if not PURE_PYTHON:
        try:
            c_module = importlib.import_module('BTrees._' + module_name)
        except ImportError:
            pass
    if c_module is not None:
        new_values = dict(c_module.__dict__)
        new_values.pop("__name__", None)
        new_values.pop('__file__', None)
        new_values.pop('__doc__', None)
        mod_globals.update(new_values)
    else:
        # No C extension, make the Py versions available without that
        # extension. The list comprehension both filters and prevents
        # concurrent modification errors.
        for py in [k for k in mod_globals if k.endswith('Py')]:
            mod_globals[py[:-2]] = mod_globals[py]

    # Assign the global aliases
    prefix = module_name[:2]
    for name in ('Bucket', 'Set', 'BTree', 'TreeSet'):
        mod_globals[name] = mod_globals[prefix + name]

    # Cleanup
    del mod_globals['import_c_extension']
