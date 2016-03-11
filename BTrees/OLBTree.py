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

from .Interfaces import IObjectIntegerBTreeModule
from ._base import Bucket
from ._base import MERGE
from ._base import MERGE_WEIGHT_numeric
from ._base import MERGE_DEFAULT_int
from ._base import Set
from ._base import Tree as BTree
from ._base import TreeSet
from ._base import _TreeIterator
from ._base import difference as _difference
from ._base import intersection as _intersection
from ._base import set_operation as _set_operation
from ._base import to_ob as _to_key
from ._base import to_long as _to_value
from ._base import union as _union
from ._base import weightedIntersection as _weightedIntersection
from ._base import weightedUnion as _weightedUnion
from ._base import _fix_pickle

_BUCKET_SIZE = 60
_TREE_SIZE = 250
using64bits = True


class OLBucketPy(Bucket):
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class OLSetPy(Set):
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class OLBTreePy(BTree):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class OLTreeSetPy(TreeSet):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class OLTreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

OLBucketPy._mapping_type = OLBucketPy._bucket_type = OLBucketPy
OLBucketPy._set_type = OLSetPy

OLSetPy._mapping_type = OLBucketPy
OLSetPy._set_type = OLSetPy._bucket_type = OLSetPy

OLBTreePy._mapping_type = OLBTreePy._bucket_type = OLBucketPy
OLBTreePy._set_type = OLSetPy

OLTreeSetPy._mapping_type = OLBucketPy
OLTreeSetPy._set_type = OLTreeSetPy._bucket_type = OLSetPy


differencePy = _set_operation(_difference, OLSetPy)
unionPy = _set_operation(_union, OLSetPy)
intersectionPy = _set_operation(_intersection, OLSetPy)
weightedUnionPy = _set_operation(_weightedUnion, OLSetPy)
weightedIntersectionPy = _set_operation(_weightedIntersection, OLSetPy)

try:
    from ._OLBTree import OLBucket
except ImportError: #pragma NO COVER w/ C extensions
    OLBucket = OLBucketPy
    OLSet = OLSetPy
    OLBTree = OLBTreePy
    OLTreeSet = OLTreeSetPy
    OLTreeIterator = OLTreeIteratorPy
    difference = differencePy
    union = unionPy
    intersection = intersectionPy
    weightedUnion = weightedUnionPy
    weightedIntersection = weightedIntersectionPy
else: #pragma NO COVER w/o C extensions
    from ._OLBTree import OLSet
    from ._OLBTree import OLBTree
    from ._OLBTree import OLTreeSet
    from ._OLBTree import OLTreeIterator
    from ._OLBTree import difference
    from ._OLBTree import union
    from ._OLBTree import intersection
    from ._OLBTree import weightedUnion
    from ._OLBTree import weightedIntersection

Bucket = OLBucket
Set = OLSet
BTree = OLBTree
TreeSet = OLTreeSet

_fix_pickle(globals(), __name__)

moduleProvides(IObjectIntegerBTreeModule)
