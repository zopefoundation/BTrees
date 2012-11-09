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
           'IFBucket', 'IFSet', 'IFBTree', 'IFTreeSet',
           'union', 'intersection', 'difference',  
           'weightedUnion', 'weightedIntersection', 'multiunion',
          )

from zope.interface import moduleProvides

from BTrees.Interfaces import IIntegerFloatBTreeModule
from BTrees.___BTree import Bucket
from BTrees.___BTree import MERGE
from BTrees.___BTree import MERGE_WEIGHT_numeric
from BTrees.___BTree import MERGE_DEFAULT_float
from BTrees.___BTree import Set
from BTrees.___BTree import Tree as BTree
from BTrees.___BTree import TreeSet
from BTrees.___BTree import difference as _difference
from BTrees.___BTree import intersection as _intersection
from BTrees.___BTree import multiunion as _multiunion
from BTrees.___BTree import setop as _setop
from BTrees.___BTree import to_int as _to_key
from BTrees.___BTree import to_float as _to_value
from BTrees.___BTree import union as _union
from BTrees.___BTree import weightedIntersection as _weightedIntersection
from BTrees.___BTree import weightedUnion as _weightedUnion

_BUCKET_SIZE = 120
_TREE_SIZE = 500
using64bits = False

class IFBucketPy(Bucket):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float
try:
    from _IFBTree import IFBucket
except ImportError:
    IFBucket = IFBucketPy
Bucket = IFBucket


class IFSetPy(Set):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float
try:
    from _IFBTree import IFSet
except ImportError:
    IFSet = IFSetPy
Set = IFSet


class IFBTreePy(BTree):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float
try:
    from _IFBTree import IFBTree
except ImportError:
    IFBTree = IFBTreePy
BTree = IFBTree


class IFTreeSetPy(TreeSet):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float
try:
    from _IFBTree import IFTreeSet
except ImportError:
    IFTreeSet = IFTreeSetPy
TreeSet = IFTreeSet


# Can't declare forward refs, so fix up afterwards:

IFBucketPy._mapping_type = IFBucketPy._bucket_type = IFBucketPy
IFBucketPy._set_type = IFSetPy

IFSetPy._mapping_type = IFBucketPy
IFSetPy._set_type = IFSetPy._bucket_type = IFSetPy

IFBTreePy._mapping_type = IFBTreePy._bucket_type = IFBucketPy
IFBTreePy._set_type = IFSetPy

IFTreeSetPy._mapping_type = IFBucketPy
IFTreeSetPy._set_type = IFTreeSetPy._bucket_type = IFSetPy


differencePy = _setop(_difference, IFSetPy)
try:
    from _IFBTree import difference
except ImportError:
    difference = differencePy

unionPy = _setop(_union, IFSetPy)
try:
    from _IFBTree import union
except ImportError:
    union = unionPy

intersectionPy = _setop(_intersection, IFSetPy)
try:
    from _IFBTree import intersection
except ImportError:
    intersection = intersectionPy

multiunionPy = _setop(_multiunion, IFSetPy)
try:
    from _IFBTree import multiunion
except ImportError:
    multiunion = multiunionPy

weightedUnionPy = _setop(_weightedUnion, IFSetPy)
try:
    from _OIBTree import union
except ImportError:
    weightedUnion = weightedUnionPy

weightedIntersectionPy = _setop(_weightedIntersection, IFSetPy)
try:
    from _OIBTree import weightedIntersection
except ImportError:
    weightedIntersection = weightedIntersectionPy


moduleProvides(IIntegerFloatBTreeModule)
