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

__all__ = ('Bucket', 'Set', 'BTree', 'TreeSet',
           'LOBucket', 'LOSet', 'LOBTree', 'LOTreeSet',
           'union', 'intersection', 'difference', 'multiunion',
          )

from zope.interface import moduleProvides

from BTrees.Interfaces import IIntegerObjectBTreeModule
from BTrees.___BTree import Bucket
from BTrees.___BTree import Set
from BTrees.___BTree import Tree as BTree
from BTrees.___BTree import TreeSet
from BTrees.___BTree import difference as _difference
from BTrees.___BTree import intersection as _intersection
from BTrees.___BTree import multiunion as _multiunion
from BTrees.___BTree import setop as _setop
from BTrees.___BTree import to_long as _to_key
from BTrees.___BTree import to_ob as _to_value
from BTrees.___BTree import union as _union

_BUCKET_SIZE = 60
_TREE_SIZE = 500
using64bits = True


class LOBucketPy(Bucket):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
    _to_value = _to_value

    def MERGE_WEIGHT(self, value, weight):
        return value


class LOSetPy(Set):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key


class LOBTreePy(BTree):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value

    def MERGE_WEIGHT(self, value, weight):
        return value


class LOTreeSetPy(TreeSet):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key


# Can't declare forward refs, so fix up afterwards:

LOBucketPy._mapping_type = LOBucketPy._bucket_type = LOBucketPy
LOBucketPy._set_type = LOSetPy

LOSetPy._mapping_type = LOBucketPy
LOSetPy._set_type = LOSetPy._bucket_type = LOSetPy

LOBTreePy._mapping_type = LOBTreePy._bucket_type = LOBucketPy
LOBTreePy._set_type = LOSetPy

LOTreeSetPy._mapping_type = LOBucketPy
LOTreeSetPy._set_type = LOTreeSetPy._bucket_type = LOSetPy


differencePy = _setop(_difference, LOSetPy)
unionPy = _setop(_union, LOSetPy)
intersectionPy = _setop(_intersection, LOSetPy)
multiunionPy = _setop(_multiunion, LOSetPy)

try:
    from _LOBTree import LOBucket
    from _LOBTree import LOSet
    from _LOBTree import LOBTree
    from _LOBTree import LOTreeSet
    from _LOBTree import difference
    from _LOBTree import union
    from _LOBTree import intersection
    from _LOBTree import multiunion
except ImportError: #pragma NO COVER
    LOBucket = LOBucketPy
    LOSet = LOSetPy
    LOBTree = LOBTreePy
    LOTreeSet = LOTreeSetPy
    difference = differencePy
    union = unionPy
    intersection = intersectionPy
    multiunion = multiunionPy

Bucket = LOBucket
Set = LOSet
BTree = LOBTree
TreeSet = LOTreeSet

moduleProvides(IIntegerObjectBTreeModule)
