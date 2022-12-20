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

from operator import index as operator__index__
from struct import Struct
from struct import error as struct_error

from abc import ABC

from .utils import Lazy

# pylint:disable=raise-missing-from

class DataType:
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
        Verify *item* is in the correct format (or "close" enough)
        and return the item or its suitable conversion.

        If this cannot be done, raise a :exc:`TypeError`.

        The definition of "close" varies according to the datatypes.
        For example, integer datatypes will accept anything that can
        be converted into an integer using normal python coercion
        rules (calling ``__index__``) and where the integer fits into
        the required native type size (e.g., 4 bytes).
        """
        raise NotImplementedError

    def coerce(self, item):
        """
        Coerce *item* into something that can be used with
        ``__call__`` and return it.

        The coercion rules will vary by datatype. This exists only
        for test cases. The default is to perform the same validation
        as ``__call__``.
        """
        return self(item)

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

    def add_extra_methods(self, base_name, cls):
        """
        Hook method called on the key datatype to add zero or more
        desired arbitrary additional, non-standard, methods to the
        *cls* being constructed.

        *base_name* will be a string identifying the particular family
        of class being constructed, such as 'Bucket' or 'BTree'.
        """


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



class _HasDefaultComparison(ABC):
    """
    An `ABC <https://docs.python.org/3/library/abc.html>_` for
    checking whether an item has default comparison.

    All we have to do is override ``__subclasshook__`` to implement an
    algorithm determining whether a class has default comparison.
    Python and the ABC machinery will take care of translating
    ``isinstance(thing, _HasDefaultComparison)`` into something like
    ``_HasDefaultComparison.__subclasshook__(type(thing))``. The ABC
    handles caching the answer (based on exact classes, no MRO), and
    getting the type from ``thing`` (including mostly dealing with
    old-style) classes on Python 2.
    """

    # Comparisons only use special methods defined on the
    # type, not instance variables.

    # On CPython 3, classes inherit __lt__ with ``__objclass__`` of ``object``.
    # On PyPy3, they do.
    #
    # Test these conditions at runtime and define the method variant
    # appropriately.
    #
    # Remember the method is checking if the object has default comparison
    assert '__lt__' not in DataType.__dict__
    if getattr(DataType.__lt__, '__objclass__', None) is object:
        # CPython 3
        @classmethod
        def __subclasshook__(cls, C, _NoneType=type(None)):
            if C is _NoneType:
                return False
            defining_class = getattr(C.__lt__, '__objclass__', None)
            if defining_class is None:
                # Implemented in Python
                return False
            return C.__lt__.__objclass__ is object
    else:
        # PyPy3
        @classmethod
        def __subclasshook__(cls, C, _object_lt=object.__lt__, _NoneType=type(None)):
            if C is _NoneType:
                return False
            return C.__lt__ is _object_lt


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

    def __call__(self, item):
        if isinstance(item, _HasDefaultComparison):
            raise TypeError("Object of class {} has default comparison".format(type(item).__name__))
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
    _as_packable = operator__index__ # calls ``obj.__index__`` to yield integer

    @Lazy
    def _check_native(self):
        return Struct(self._struct_format).pack

    def __call__(self, item):
        try:
            self._check_native(self._as_packable(item)) # pylint:disable=too-many-function-args
        except (struct_error, TypeError, ValueError):
            # PyPy can raise ValueError converting a negative number to a
            # unsigned value.
            if isinstance(item, int):
                raise TypeError("Value out of range", item)
            raise TypeError(self._error_description)

        return self._as_python_type(item)

    def apply_weight(self, item, weight):
        return item * weight

    def supports_value_union(self):
        return True

class _AbstractIntDataType(_AbstractNativeDataType):
    _as_python_type = int
    _required_python_type = int
    multiplication_identity = 1
    long_name = "Integer"

    def getTwoExamples(self):
        return 1, 2

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


class _AbstractBytes(KeyDataType):
    """
    An exact-length byte string type.

    This must be subclassed to provide the actual byte length.
    """
    tree_size = 500
    default_bucket_size = 500
    _length = None

    def __call__(self, item):
        if not isinstance(item, bytes) or len(item) != self._length:
            raise TypeError("{}-byte array expected, not {!r}".format(self._length, item))
        return item

    def supports_value_union(self):
        # We don't implement 'multiunion' for fsBTree.
        return False


class f(_AbstractBytes):
    """
    The key type for an ``fs`` tree.

    This is a two-byte prefix of an overall 8-byte value
    like a ZODB object ID or transaction ID.
    """

    # Our keys are treated like integers; the module
    # implements IIntegerObjectBTreeModule
    long_name = 'Integer'
    prefix_code = 'f'
    _length = 2

    # Check it can be converted to a two-byte
    # value. Note that even though we allow negative values
    # that can break test assumptions: -1 < 0 < 1, but the byte
    # values for those are \xff\xff > \x00\x00 < \x00\x01.
    _as_2_bytes = Struct('>h').pack

    def coerce(self, item):
        try:
            return self(item)
        except TypeError:
            try:
                return self._as_2_bytes(operator__index__(item))
            except struct_error as e:
                raise TypeError(e)

    @staticmethod
    def _make_Bucket_toString():
        def toString(self):
            return b''.join(self._keys) + b''.join(self._values)
        return toString

    @staticmethod
    def _make_Bucket_fromString():
        def fromString(self, v):
            length = len(v)
            if length % 8 != 0:
                raise ValueError()
            count = length // 8
            keys, values = v[:count*2], v[count*2:]
            self.clear()
            while keys and values:
                key, keys = keys[:2], keys[2:]
                value, values = values[:6], values[6:]
                self._keys.append(key)
                self._values.append(value)
            return self
        return fromString

    def add_extra_methods(self, base_name, cls):
        if base_name == 'Bucket':
            cls.toString = self._make_Bucket_toString()
            cls.fromString = self._make_Bucket_fromString()

class s(_AbstractBytes):
    """
    The value type for an ``fs`` tree.

    This is a 6-byte suffix of an overall 8-byte value
    like a ZODB object ID or transaction ID.
    """

    # Our values are treated like objects; the
    # module implements IIntegerObjectBTreeModule
    long_name = 'Object'
    prefix_code = 's'
    _length = 6

    def get_lower_bound(self):
        # Negative values have the high bit set, which is incompatible
        # with our transformation.
        return 0

    # To coerce an integer, as used in tests, first convert to 8 bytes
    # in big-endian order, then ensure the first two
    # are 0 and cut them off.
    _as_8_bytes = Struct('>q').pack

    def coerce(self, item):
        try:
            return self(item)
        except TypeError:
            try:
                as_bytes = self._as_8_bytes(operator__index__(item))
            except struct_error as e:
                raise TypeError(e)

            if as_bytes[:2] != b'\x00\x00':
                raise TypeError("Cannot convert {!r} to 6 bytes ({!r})".format(item, as_bytes))
            return as_bytes[2:]
