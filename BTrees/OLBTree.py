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
           'OLBucket', 'OLSet', 'OLBTree', 'OLTreeSet',
           'union', 'intersection', 'difference',  
           'weightedUnion', 'weightedIntersection',
          )

from zope.interface import moduleProvides

from BTrees.Interfaces import IObjectIntegerBTreeModule
from BTrees.___BTree import Bucket
from BTrees.___BTree import MERGE
from BTrees.___BTree import MERGE_WEIGHT_numeric
from BTrees.___BTree import MERGE_DEFAULT_int
from BTrees.___BTree import Set
from BTrees.___BTree import Tree as BTree
from BTrees.___BTree import TreeSet
from BTrees.___BTree import difference as _difference
from BTrees.___BTree import intersection as _intersection
from BTrees.___BTree import setop as _setop
from BTrees.___BTree import to_ob as _to_key
from BTrees.___BTree import to_int as _to_value
from BTrees.___BTree import union as _union
from BTrees.___BTree import weightedIntersection as _weightedIntersection
from BTrees.___BTree import weightedUnion as _weightedUnion

_BUCKET_SIZE = 60
_TREE_SIZE = 250
using64bits = True

class OLBucketPy(Bucket):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int
try:
    from _OLBTree import OLBucket
except ImportError:
    OLBucket = OLBucketPy
Bucket = OLBucket


class OLSetPy(Set):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int
try:
    from _OLBTree import OLSet
except ImportError:
    OLSet = OLSetPy
Set = OLSet


class OLBTreePy(BTree):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int
try:
    from _OLBTree import OLBTree
except ImportError:
    OLBTree = OLBTreePy
BTree = OLBTree


class OLTreeSetPy(TreeSet):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int
try:
    from _OLBTree import OLTreeSet
except ImportError:
    OLTreeSet = OLTreeSetPy
TreeSet = OLTreeSet


# Can't declare forward refs, so fix up afterwards:

OLBucketPy._mapping_type = OLBucketPy._bucket_type = OLBucketPy
OLBucketPy._set_type = OLSetPy

OLSetPy._mapping_type = OLBucketPy
OLSetPy._set_type = OLSetPy._bucket_type = OLSetPy

OLBTreePy._mapping_type = OLBTreePy._bucket_type = OLBucketPy
OLBTreePy._set_type = OLSetPy

OLTreeSetPy._mapping_type = OLBucketPy
OLTreeSetPy._set_type = OLTreeSetPy._bucket_type = OLSetPy


differencePy = _setop(_difference, OLSetPy)
try:
    from _OLBTree import difference
except ImportError:
    difference = differencePy

unionPy = _setop(_union, OLSetPy)
try:
    from _OLBTree import union
except ImportError:
    union = unionPy

intersectionPy = _setop(_intersection, OLSetPy)
try:
    from _OLBTree import intersection
except ImportError:
    intersection = intersectionPy

weightedUnionPy = _setop(_weightedUnion, OLSetPy)
try:
    from _OLBTree import union
except ImportError:
    weightedUnion = weightedUnionPy

weightedIntersectionPy = _setop(_weightedIntersection, OLSetPy)
try:
    from _OLBTree import weightedIntersection
except ImportError:
    weightedIntersection = weightedIntersectionPy


moduleProvides(IObjectIntegerBTreeModule)
