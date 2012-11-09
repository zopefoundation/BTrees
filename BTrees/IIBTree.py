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
           'IIBucket', 'IISet', 'IIBTree', 'IITreeSet',
           'union', 'intersection', 'difference',  
           'weightedUnion', 'weightedIntersection', 'multiunion',
          )

from zope.interface import moduleProvides

from BTrees.Interfaces import IIntegerIntegerBTreeModule
from BTrees.___BTree import Bucket
from BTrees.___BTree import MERGE
from BTrees.___BTree import MERGE_WEIGHT_numeric
from BTrees.___BTree import MERGE_DEFAULT_int
from BTrees.___BTree import Set
from BTrees.___BTree import Tree as BTree
from BTrees.___BTree import TreeSet
from BTrees.___BTree import difference as _difference
from BTrees.___BTree import intersection as _intersection
from BTrees.___BTree import multiunion as _multiunion
from BTrees.___BTree import setop as _setop
from BTrees.___BTree import to_int as _to_key
from BTrees.___BTree import to_int as _to_value
from BTrees.___BTree import union as _union
from BTrees.___BTree import weightedIntersection as _weightedIntersection
from BTrees.___BTree import weightedUnion as _weightedUnion

_BUCKET_SIZE = 120
_TREE_SIZE = 500
using64bits = False

class IIBucketPy(Bucket):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int
try:
    from _IIBTree import IIBucket
except ImportError:
    IIBucket = IIBucketPy
Bucket = IIBucket


class IISetPy(Set):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int
try:
    from _IIBTree import IISet
except ImportError:
    IISet = IISetPy
Set = IISet


class IIBTreePy(BTree):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int
try:
    from _IIBTree import IIBTree
except ImportError:
    IIBTree = IIBTreePy
BTree = IIBTree


class IITreeSetPy(TreeSet):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int
try:
    from _IIBTree import IITreeSet
except ImportError:
    IITreeSet = IITreeSetPy
TreeSet = IITreeSet


# Can't declare forward refs, so fix up afterwards:

IIBucketPy._mapping_type = IIBucketPy._bucket_type = IIBucketPy
IIBucketPy._set_type = IISetPy

IISetPy._mapping_type = IIBucketPy
IISetPy._set_type = IISetPy._bucket_type = IISetPy

IIBTreePy._mapping_type = IIBTreePy._bucket_type = IIBucketPy
IIBTreePy._set_type = IISetPy

IITreeSetPy._mapping_type = IIBucketPy
IITreeSetPy._set_type = IITreeSetPy._bucket_type = IISetPy


differencePy = _setop(_difference, IISetPy)
try:
    from _IIBTree import difference
except ImportError:
    difference = differencePy

unionPy = _setop(_union, IISetPy)
try:
    from _IIBTree import union
except ImportError:
    union = unionPy

intersectionPy = _setop(_intersection, IISetPy)
try:
    from _IIBTree import intersection
except ImportError:
    intersection = intersectionPy

multiunionPy = _setop(_multiunion, IISetPy)
try:
    from _IIBTree import multiunion
except ImportError:
    multiunion = multiunionPy

weightedUnionPy = _setop(_weightedUnion, IISetPy)
try:
    from _OIBTree import union
except ImportError:
    weightedUnion = weightedUnionPy

weightedIntersectionPy = _setop(_weightedIntersection, IISetPy)
try:
    from _OIBTree import weightedIntersection
except ImportError:
    weightedIntersection = weightedIntersectionPy


moduleProvides(IIntegerIntegerBTreeModule)
