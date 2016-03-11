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
           'BIBucket', 'BISet', 'BIBTree', 'BITreeSet',
           'union', 'intersection', 'difference',  
           'weightedUnion', 'weightedIntersection', 'multiunion',
          )

from zope.interface import moduleProvides

from .Interfaces import IByteIntegerBTreeModule
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
from ._base import to_int as _to_key
from ._base import to_int as _to_value
from ._base import union as _union
from ._base import weightedIntersection as _weightedIntersection
from ._base import weightedUnion as _weightedUnion
from ._base import _fix_pickle

_BUCKET_SIZE = 120
_TREE_SIZE = 500
using64bits = False


class BIBucketPy(Bucket):
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class BISetPy(Set):
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class BIBTreePy(BTree):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class BITreeSetPy(TreeSet):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class BITreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

BIBucketPy._mapping_type = BIBucketPy._bucket_type = BIBucketPy
BIBucketPy._set_type = BISetPy

BISetPy._mapping_type = BIBucketPy
BISetPy._set_type = BISetPy._bucket_type = BISetPy

BIBTreePy._mapping_type = BIBTreePy._bucket_type = BIBucketPy
BIBTreePy._set_type = BISetPy

BITreeSetPy._mapping_type = BIBucketPy
BITreeSetPy._set_type = BITreeSetPy._bucket_type = BISetPy


differencePy = _set_operation(_difference, BISetPy)
unionPy = _set_operation(_union, BISetPy)
intersectionPy = _set_operation(_intersection, BISetPy)
multiunionPy = _set_operation(_multiunion, BISetPy)
weightedUnionPy = _set_operation(_weightedUnion, BISetPy)
weightedIntersectionPy = _set_operation(_weightedIntersection, BISetPy)

try:
    from ._BIBTree import BIBucket
except ImportError: #pragma NO COVER w/ C extensions
    BIBucket = BIBucketPy
    BISet = BISetPy
    BIBTree = BIBTreePy
    BITreeSet = BITreeSetPy
    BITreeIterator = BITreeIteratorPy
    difference = differencePy
    union = unionPy
    intersection = intersectionPy
    multiunion = multiunionPy
    weightedUnion = weightedUnionPy
    weightedIntersection = weightedIntersectionPy
else: #pragma NO COVER w/o C extensions
    from ._BIBTree import BISet
    from ._BIBTree import BIBTree
    from ._BIBTree import BITreeSet
    from ._BIBTree import BITreeIterator
    from ._BIBTree import difference
    from ._BIBTree import union
    from ._BIBTree import intersection
    from ._BIBTree import multiunion
    from ._BIBTree import weightedUnion
    from ._BIBTree import weightedIntersection

Bucket = BIBucket
Set = BISet
BTree = BIBTree
TreeSet = BITreeSet

_fix_pickle(globals(), __name__)

moduleProvides(IByteIntegerBTreeModule)
