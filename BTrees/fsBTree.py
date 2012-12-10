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

# fsBTrees are data structures used for ZODB FileStorage.  They are not
# expected to be "public" excpect to FileStorage.

__all__ = ('Bucket', 'Set', 'BTree', 'TreeSet',
           'fsBucket', 'fsSet', 'fsBTree', 'fsTreeSet',
           'union', 'intersection', 'difference', 'multiunion',
          )


from zope.interface import moduleProvides

from .Interfaces import IIntegerObjectBTreeModule
from ._base import Bucket
from ._base import Set
from ._base import Tree as BTree
from ._base import TreeSet
from ._base import difference as _difference
from ._base import intersection as _intersection
from ._base import multiunion as _multiunion
from ._base import set_operation as _set_operation
from ._base import to_str as _to_str
from ._base import union as _union

_BUCKET_SIZE = 500
_TREE_SIZE = 500
using64bits = False
_to_key = _to_str(2)
_to_value = _to_str(6)


class fsBucketPy(Bucket):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
    _to_value = _to_value

    def MERGE_WEIGHT(self, value, weight):
        return value

    def toString(self):
        return ''.join(self._keys) + ''.join(self._values)

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


class fsSetPy(Set):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key


class fsBTreePy(BTree):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    def MERGE_WEIGHT(self, value, weight):
        return value


class fsTreeSetPy(TreeSet):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key


# Can't declare forward refs, so fix up afterwards:

fsBucketPy._mapping_type = fsBucketPy._bucket_type = fsBucketPy
fsBucketPy._set_type = fsSetPy

fsSetPy._mapping_type = fsBucketPy
fsSetPy._set_type = fsSetPy._bucket_type = fsSetPy

fsBTreePy._mapping_type = fsBTreePy._bucket_type = fsBucketPy
fsBTreePy._set_type = fsSetPy

fsTreeSetPy._mapping_type = fsBucketPy
fsTreeSetPy._set_type = fsTreeSetPy._bucket_type = fsSetPy


differencePy = _set_operation(_difference, fsSetPy)
unionPy = _set_operation(_union, fsSetPy)
intersectionPy = _set_operation(_intersection, fsSetPy)
multiunionPy = _set_operation(_multiunion, fsSetPy)

try:
    from _fsBTree import fsBucket
    from _fsBTree import fsSet
    from _fsBTree import fsBTree
    from _fsBTree import fsTreeSet
    from _fsBTree import difference
    from _fsBTree import union
    from _fsBTree import intersection
    from _fsBTree import multiunion
except ImportError: #pragma NO COVER
    fsBucket = fsBucketPy
    fsSet = fsSetPy
    fsBTree = fsBTreePy
    fsTreeSet = fsTreeSetPy
    difference = differencePy
    union = unionPy
    intersection = intersectionPy
    multiunion = multiunionPy

Bucket = fsBucket
Set = fsSet
BTree = fsBTree
TreeSet = fsTreeSet

moduleProvides(IIntegerObjectBTreeModule)
