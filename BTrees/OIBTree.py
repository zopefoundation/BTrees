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

from zope.interface import moduleProvides

from BTrees.Interfaces import IObjectIntegerBTreeModule
from BTrees.___BTree import Bucket
from BTrees.___BTree import MERGE
from BTrees.___BTree import MERGE_WEIGHT_numeric
from BTrees.___BTree import MERGE_DEFAULT_float
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

class OIBucketPy(Bucket):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float
try:
    from _OIBTree import OIBucket
except ImportError:
    OIBucket = OIBucketPy
Bucket = OIBucket


class OISetPy(Set):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float
try:
    from _OIBTree import OISet
except ImportError:
    OISet = OISetPy
Set = OISet


class OIBTreePy(BTree):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float
try:
    from _OIBTree import OIBTree
except ImportError:
    OIBTree = OIBTreePy
BTree = OIBTree


class OITreeSetPy(TreeSet):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float
try:
    from _OIBTree import OITreeSet
except ImportError:
    OITreeSet = OITreeSetPy
TreeSet = OITreeSet


# Can't declare forward refs, so fix up afterwards:

OIBucketPy._mapping_type = OIBucketPy._bucket_type = OIBucketPy
OIBucketPy._set_type = OISetPy

OISetPy._mapping_type = OIBucketPy
OISetPy._set_type = OISetPy._bucket_type = OISetPy

OIBTreePy._mapping_type = OIBTreePy._bucket_type = OIBucketPy
OIBTreePy._set_type = OISetPy

OITreeSetPy._mapping_type = OIBucketPy
OITreeSetPy._set_type = OITreeSetPy._bucket_type = OISetPy


differencePy = _setop(_difference, OISetPy)
try:
    from _OIBTree import difference
except ImportError:
    difference = differencePy

unionPy = _setop(_union, OISetPy)
try:
    from _OIBTree import union
except ImportError:
    union = unionPy

intersectionPy = _setop(_intersection, OISetPy)
try:
    from _OIBTree import intersection
except ImportError:
    intersection = intersectionPy

weightedUnionPy = _setop(_weightedUnion, OISetPy)
try:
    from _OIBTree import union
except ImportError:
    weightedUnion = weightedUnionPy

weightedIntersectionPy = _setop(_weightedIntersection, OISetPy)
try:
    from _OIBTree import weightedIntersection
except ImportError:
    weightedIntersection = weightedIntersectionPy


moduleProvides(IObjectIntegerBTreeModule)
