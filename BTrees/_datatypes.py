##############################################################################
#
# Copyright Zope Foundation and Contributors.
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
"""
Descriptions of the datatypes supported by this package.
"""
from __future__ import absolute_import

from operator import index as object_to_index
from struct import Struct
from struct import error as struct_error

from ._compat import int_types
from .utils import Lazy


class DataType(object):
    """
    Describes a data type used as a value.

    Subclasses will be defined for each particular
    supported type.
    """

    # The name for this datatype as used in interface names.
    long_name = None

    # The prefix code for this data type. Usually a single letter.
    prefix_code = None

    # The multiplication identity for this data type. Used in
    # combining (merging) data types. Leave undefined if this is
    # not a valid operation.
    multiplication_identity = None

    # Does the data take up 64-bits? Currently only relevant for the
    # integer key types.
    using64bits = False

    def __init__(self):
        if not self.prefix_code:
            self.prefix_code = type(self).__name__

    def __call__(self, item):
        """
        Convert *item* into the correct format and return it.

        If this cannot be done, raise an appropriate exception.
        """
        raise NotImplementedError

    def apply_weight(self, item, weight): # pylint:disable=unused-argument
        """
        Apply a *weight* multiplier to *item*.

        Used when merging data structures. The *item* will be a
        value.
        """
        return item

    def as_value_type(self):
        # Because ``O'`` is used for both key and value,
        # we can override this to get the less restrictive value type.
        return self

    def supports_value_union(self):
        raise NotImplementedError

    def getTwoExamples(self):
        """
        Provide two distinct (non equal) examples acceptable to `__call__`.

        This is for testing.
        """
        return "object1", "object2"

    def get_lower_bound(self):
        """
        If there is a lower bound (inclusive) on the data type, return
        it. Otherwise, return ``None``.

        For integer types, this will only depend on whether it
        supports signed or unsigned values, and the answer will be 0
        or a negative number. For object types, ``None`` is always
        defined to sort as the lowest bound.

        This can be relevant for both key and value types.
        """
        return None

    def get_upper_bound(self):
        """
        If there is an upper bound (inclusive) on the data type,
        return it. Otherwise, return ``None``.

        Remarks are as for `get_lower_bound`.
        """
        return None


class KeyDataType(DataType):
    """
    Describes a data type that has additional restrictions allowing it
    to be used as a key.
    """

    # When used as the key, this number determines the
    # max_internal_size.
    tree_size = 500

    default_bucket_size = 120

    def __call__(self, item):
        raise NotImplementedError

    def bucket_size_for_value(self, value_type):
        """
        What should the bucket (``max_leaf_size``) be when
        this data type is used with the given *value_type*?
        """
        if isinstance(value_type, Any):
            return self.default_bucket_size // 2
        return self.default_bucket_size


class Any(DataType):
    """
    Arbitrary Python objects.
    """
    prefix_code = 'O'
    long_name = 'Object'

    def __call__(self, item):
        return item

    def supports_value_union(self):
        return False


class O(KeyDataType):
    """
    Arbitrary (sortable) Python objects.
    """
    long_name = 'Object'
    tree_size = 250
    default_bucket_size = 60

    def as_value_type(self):
        return Any()

    def supports_value_union(self):
        return False

    @staticmethod
    def _check_default_comparison(
            item,
            # PyPy2 doesn't define __lt__ on object; PyPy3 and
            # CPython 2 and 3 do.
            _object_lt=getattr(object, '__lt__', object())
    ):
        # Enforce test that key has non-default comparison.
        # (With the exception of None, because we define a sort order
        # for it.)

        if item is None:
            return

        if type(item) is object: # pylint:disable=unidiomatic-typecheck
            raise TypeError("Can't use object() as keys")

        # Now more complicated checks to be sure we didn't
        # inherit default comparison on any version of Python.


        # TODO: Using a custom ABC and doing ``isinstance(item, NoDefaultComparison)``
        # would automatically gain us caching.

        # XXX: Comparisons only use special methods defined on the
        # type, not instance variables. So shouldn't this be getattr(type(key)...)?
        # Note that changes some things below; for example, on CPython 2,
        # every subclass of object inherits __lt__ (unless it overrides), and it
        # has __objclass__ of ``type`` (of course it is also the same object
        # as ``_object_lt`` at that point). Also, weirdly, CPython 2 classes inherit
        # ``__lt__``, but *instances* do not.

        lt = getattr(item, '__lt__', None)
        if lt is not None:
            # CPython 2 and 3 follow PEP 252, defining '__objclass__'
            # for methods of builtin types like str; methods of
            # classes defined in Python don't get it. ``__objclass__``
            if getattr(lt, '__objclass__', None) is object:
                lt = None  # pragma: no cover Py3k
            # PyPy3 doesn't follow PEP 252, but defines '__func__'
            elif getattr(lt, '__func__', None) is _object_lt:
                lt = None  # pragma: no cover PyPy3

        if (lt is None
                # TODO: Shouldn't we only check __cmp__ on Python 2?
                # Python 3 won't use it.
                and getattr(item, '__cmp__', None) is None):
            raise TypeError("Object has default comparison")


    def __call__(self, item):
        self._check_default_comparison(item)
        return item


class _AbstractNativeDataType(KeyDataType):
    """
    Uses `struct.Struct` to verify that the data can fit into a native
    type.
    """

    _struct_format = None
    _as_python_type = NotImplementedError
    _required_python_type = object
    _error_description = None
    _as_packable = object_to_index

    @Lazy
    def _check_native(self):
        return Struct(self._struct_format).pack

    def __call__(self, item):
        try:
            self._check_native(self._as_packable(item)) # pylint:disable=too-many-function-args
        except (struct_error, TypeError, ValueError):
            # PyPy can raise ValueError converting a negative number to a
            # unsigned value.
            if isinstance(item, int_types):
                raise OverflowError("Value out of range", item)
            raise TypeError(self._error_description)

        return self._as_python_type(item)

    def apply_weight(self, item, weight):
        return item * weight

    def supports_value_union(self):
        return True

class _AbstractIntDataType(_AbstractNativeDataType):
    _as_python_type = int
    _required_python_type = int_types
    multiplication_identity = 1
    long_name = "Integer"

    def getTwoExamples(self):
        return 1, 2

    # On Python 2, it's important for these values to be actual `int`
    # values, not `long` when they fit; passing a value that's too big
    # to `int` will still result in it being a `long`. For some reason
    # on Windows, even the 32-bit values somehow wind up as longs
    # unless we do the conversion.
    def get_lower_bound(self):
        exp = 64 if self.using64bits else 32
        exp -= 1
        return int(-(2 ** exp))

    def get_upper_bound(self):
        exp = 64 if self.using64bits else 32
        exp -= 1
        return int(2 ** exp - 1)


class _AbstractUIntDataType(_AbstractIntDataType):
    long_name = 'Unsigned'

    def get_lower_bound(self):
        return 0

    def get_upper_bound(self):
        exp = 64 if self.using64bits else 32
        return int(2 ** exp - 1)


class I(_AbstractIntDataType):
    _struct_format = 'i'
    _error_description = "32-bit integer expected"


class U(_AbstractUIntDataType):
    _struct_format = 'I'
    _error_description = 'non-negative 32-bit integer expected'


class F(_AbstractNativeDataType):
    _struct_format = 'f'
    _as_python_type = float
    _error_description = 'float expected'
    _as_packable = lambda self, k: k # identity
    multiplication_identity = 1.0
    long_name = 'Float'

    def getTwoExamples(self):
        return 0.5, 1.5

class L(_AbstractIntDataType):
    _struct_format = 'q'
    _error_description = '64-bit integer expected'
    using64bits = True


class Q(_AbstractUIntDataType):
    _struct_format = 'Q'
    _error_description = 'non-negative 64-bit integer expected'
    using64bits = True


class Bytes(KeyDataType):
    """
    An exact-length byte string type.
    """
    __slots__ = ()
    prefix_code = 'fs'
    default_bucket_size = 500

    def __init__(self, length):
        super(Bytes, self).__init__()
        self._length = length

    def __call__(self, item):
        if not isinstance(item, bytes) or len(item) != self._length:
            raise TypeError("%s-byte array expected" % self._length)
        return item

    def supports_value_union(self):
        return False
