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

from .Interfaces import IIntegerIntegerBTreeModule
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
from ._base import multiunion as _multiunion
from ._base import set_operation as _set_operation
from ._base import to_long as _to_key
from ._base import to_long as _to_value
from ._base import union as _union
from ._base import weightedIntersection as _weightedIntersection
from ._base import weightedUnion as _weightedUnion
from ._base import _fix_pickle

_BUCKET_SIZE = 120
_TREE_SIZE = 500
using64bits = True


class LLBucketPy(Bucket):
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class LLSetPy(Set):
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class LLBTreePy(BTree):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class LLTreeSetPy(TreeSet):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class LLTreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

LLBucketPy._mapping_type = LLBucketPy._bucket_type = LLBucketPy
LLBucketPy._set_type = LLSetPy

LLSetPy._mapping_type = LLBucketPy
LLSetPy._set_type = LLSetPy._bucket_type = LLSetPy

LLBTreePy._mapping_type = LLBTreePy._bucket_type = LLBucketPy
LLBTreePy._set_type = LLSetPy

LLTreeSetPy._mapping_type = LLBucketPy
LLTreeSetPy._set_type = LLTreeSetPy._bucket_type = LLSetPy


differencePy = _set_operation(_difference, LLSetPy)
unionPy = _set_operation(_union, LLSetPy)
intersectionPy = _set_operation(_intersection, LLSetPy)
multiunionPy = _set_operation(_multiunion, LLSetPy)
weightedUnionPy = _set_operation(_weightedUnion, LLSetPy)
weightedIntersectionPy = _set_operation(_weightedIntersection, LLSetPy)

try:
    from ._LLBTree import LLBucket
except ImportError: #pragma NO COVER w/ C extensions
    LLBucket = LLBucketPy
    LLSet = LLSetPy
    LLBTree = LLBTreePy
    LLTreeSet = LLTreeSetPy
    LLTreeIterator = LLTreeIteratorPy
    difference = differencePy
    union = unionPy
    intersection = intersectionPy
    multiunion = multiunionPy
    weightedUnion = weightedUnionPy
    weightedIntersection = weightedIntersectionPy
else: #pragma NO COVER w/o C extensions
    from ._LLBTree import LLSet
    from ._LLBTree import LLBTree
    from ._LLBTree import LLTreeSet
    from ._LLBTree import LLTreeIterator
    from ._LLBTree import difference
    from ._LLBTree import union
    from ._LLBTree import intersection
    from ._LLBTree import multiunion
    from ._LLBTree import weightedUnion
    from ._LLBTree import weightedIntersection

Bucket = LLBucket
Set = LLSet
BTree = LLBTree
TreeSet = LLTreeSet

_fix_pickle(globals(), __name__)

moduleProvides(IIntegerIntegerBTreeModule)
