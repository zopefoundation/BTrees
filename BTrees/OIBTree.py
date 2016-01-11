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
           'OIBucket', 'OISet', 'OIBTree', 'OITreeSet',
           'union', 'intersection', 'difference',
           'weightedUnion', 'weightedIntersection',
          )

from zope.interface import moduleProvides

from .Interfaces import IObjectIntegerBTreeModule
from ._base import Bucket
from ._base import MERGE
from ._base import MERGE_WEIGHT_numeric
from ._base import MERGE_DEFAULT_float
from ._base import Set
from ._base import Tree as BTree
from ._base import TreeSet
from ._base import _TreeIterator
from ._base import difference as _difference
from ._base import intersection as _intersection
from ._base import set_operation as _set_operation
from ._base import to_ob as _to_key
from ._base import to_int as _to_value
from ._base import union as _union
from ._base import weightedIntersection as _weightedIntersection
from ._base import weightedUnion as _weightedUnion
from ._base import _fix_pickle

_BUCKET_SIZE = 60
_TREE_SIZE = 250
using64bits = True

class OIBucketPy(Bucket):
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class OISetPy(Set):
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class OIBTreePy(BTree):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class OITreeSetPy(TreeSet):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class OITreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

OIBucketPy._mapping_type = OIBucketPy._bucket_type = OIBucketPy
OIBucketPy._set_type = OISetPy

OISetPy._mapping_type = OIBucketPy
OISetPy._set_type = OISetPy._bucket_type = OISetPy

OIBTreePy._mapping_type = OIBTreePy._bucket_type = OIBucketPy
OIBTreePy._set_type = OISetPy

OITreeSetPy._mapping_type = OIBucketPy
OITreeSetPy._set_type = OITreeSetPy._bucket_type = OISetPy


differencePy = _set_operation(_difference, OISetPy)
unionPy = _set_operation(_union, OISetPy)
intersectionPy = _set_operation(_intersection, OISetPy)
weightedUnionPy = _set_operation(_weightedUnion, OISetPy)
weightedIntersectionPy = _set_operation(_weightedIntersection, OISetPy)

try:
    from ._OIBTree import OIBucket
except ImportError: #pragma NO COVER w/ C extensions
    OIBucket = OIBucketPy
    OISet = OISetPy
    OIBTree = OIBTreePy
    OITreeSet = OITreeSetPy
    OITreeIterator = OITreeIteratorPy
    difference = differencePy
    union = unionPy
    intersection = intersectionPy
    weightedUnion = weightedUnionPy
    weightedIntersection = weightedIntersectionPy
else: #pragma NO COVER w/o C extensions
    from ._OIBTree import OISet
    from ._OIBTree import OIBTree
    from ._OIBTree import OITreeSet
    from ._OIBTree import OITreeIterator
    from ._OIBTree import difference
    from ._OIBTree import union
    from ._OIBTree import intersection
    from ._OIBTree import weightedUnion
    from ._OIBTree import weightedIntersection


Bucket = OIBucket
Set = OISet
BTree = OIBTree
TreeSet = OITreeSet

_fix_pickle(globals(), __name__)

moduleProvides(IObjectIntegerBTreeModule)
