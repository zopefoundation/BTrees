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
           'LLBucket', 'LLSet', 'LLBTree', 'LLTreeSet',
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
from BTrees.___BTree import to_long as _to_key
from BTrees.___BTree import to_long as _to_value
from BTrees.___BTree import union as _union
from BTrees.___BTree import weightedIntersection as _weightedIntersection
from BTrees.___BTree import weightedUnion as _weightedUnion

_BUCKET_SIZE = 120
_TREE_SIZE = 500
using64bits = True


class LLBucketPy(Bucket):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class LLSetPy(Set):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class LLBTreePy(BTree):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class LLTreeSetPy(TreeSet):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


# Can't declare forward refs, so fix up afterwards:

LLBucketPy._mapping_type = LLBucketPy._bucket_type = LLBucketPy
LLBucketPy._set_type = LLSetPy

LLSetPy._mapping_type = LLBucketPy
LLSetPy._set_type = LLSetPy._bucket_type = LLSetPy

LLBTreePy._mapping_type = LLBTreePy._bucket_type = LLBucketPy
LLBTreePy._set_type = LLSetPy

LLTreeSetPy._mapping_type = LLBucketPy
LLTreeSetPy._set_type = LLTreeSetPy._bucket_type = LLSetPy


differencePy = _setop(_difference, LLSetPy)
unionPy = _setop(_union, LLSetPy)
intersectionPy = _setop(_intersection, LLSetPy)
multiunionPy = _setop(_multiunion, LLSetPy)
weightedUnionPy = _setop(_weightedUnion, LLSetPy)
weightedIntersectionPy = _setop(_weightedIntersection, LLSetPy)

try:
    from _LLBTree import LLBucket
    from _LLBTree import LLSet
    from _LLBTree import LLBTree
    from _LLBTree import LLTreeSet
    from _LLBTree import difference
    from _LLBTree import union
    from _LLBTree import intersection
    from _LLBTree import multiunion
    from _LLBTree import weightedUnion
    from _LLBTree import weightedIntersection
except ImportError: #pragma NO COVER
    LLBucket = LLBucketPy
    LLSet = LLSetPy
    LLBTree = LLBTreePy
    LLTreeSet = LLTreeSetPy
    difference = differencePy
    union = unionPy
    intersection = intersectionPy
    multiunion = multiunionPy
    weightedUnion = weightedUnionPy
    weightedIntersection = weightedIntersectionPy

Bucket = LLBucket
Set = LLSet
BTree = LLBTree
TreeSet = LLTreeSet

moduleProvides(IIntegerIntegerBTreeModule)
