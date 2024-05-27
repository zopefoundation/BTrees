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


def _ascii(x):
    return bytes(x, 'ascii')


def _c_optimizations_required():
    """Return a true value if the C optimizations are required.

    Uses the ``PURE_PYTHON`` variable as documented in `import_c_extension`.
    """
    pure_env = os.environ.get('PURE_PYTHON')
    require_c = pure_env == "0"
    return require_c


def _c_optimizations_available(module_name):
    """
    Return the C optimization module, if available, otherwise
    a false value.

    If the optimizations are required but not available, this
    raises the ImportError.

    This does not say whether they should be used or not.
    """
    import importlib
    catch = () if _c_optimizations_required() else (ImportError,)
    try:
        return importlib.import_module('BTrees._' + module_name)
    except catch:  # pragma: no cover
        return False


def _c_optimizations_ignored():
    """
    The opposite of `_c_optimizations_required`.
    """
    pure_env = os.environ.get('PURE_PYTHON')
    return pure_env != "0" if pure_env is not None else PYPY


def _should_attempt_c_optimizations():
    """
    Return a true value if we should attempt to use the C optimizations.

    This takes into account whether we're on PyPy and the value of the
    ``PURE_PYTHON`` environment variable, as defined in `import_c_extension`.
    """
    if PYPY:
        return False

    if _c_optimizations_required():
        return True
    return not _c_optimizations_ignored()


def import_c_extension(mod_globals):
    """
    Call this function with the globals of a module that implements
    Python versions of a BTree family to find the C optimizations.

    If the ``PURE_PYTHON`` environment variable is set to any value
    other than ``"0"``, or we're on PyPy, ignore the C implementation.
    If the C implementation cannot be imported, return the Python
    version. If ``PURE_PYTHON`` is set to ``"0"``, *require* the C
    implementation (let the ImportError propagate); the exception again
    is PyPy, where we never use the C extension (although it builds here, the
    ``persistent`` library doesn't provide native extensions for PyPy).

    """
    c_module = None
    module_name = mod_globals['__name__']
    assert module_name.startswith('BTrees.')
    module_name = module_name.split('.')[1]
    if _should_attempt_c_optimizations():
        c_module = _c_optimizations_available(module_name)

    if c_module:
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
    mod_globals.pop('import_c_extension', None)
