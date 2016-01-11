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

from .Interfaces import IIntegerFloatBTreeModule
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
from ._base import multiunion as _multiunion
from ._base import set_operation as _set_operation
from ._base import to_int as _to_key
from ._base import to_float as _to_value
from ._base import union as _union
from ._base import weightedIntersection as _weightedIntersection
from ._base import weightedUnion as _weightedUnion
from ._base import _fix_pickle

_BUCKET_SIZE = 120
_TREE_SIZE = 500
using64bits = False

class IFBucketPy(Bucket):
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class IFSetPy(Set):
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class IFBTreePy(BTree):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class IFTreeSetPy(TreeSet):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class IFTreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

IFBucketPy._mapping_type = IFBucketPy._bucket_type = IFBucketPy
IFBucketPy._set_type = IFSetPy

IFSetPy._mapping_type = IFBucketPy
IFSetPy._set_type = IFSetPy._bucket_type = IFSetPy

IFBTreePy._mapping_type = IFBTreePy._bucket_type = IFBucketPy
IFBTreePy._set_type = IFSetPy

IFTreeSetPy._mapping_type = IFBucketPy
IFTreeSetPy._set_type = IFTreeSetPy._bucket_type = IFSetPy


differencePy = _set_operation(_difference, IFSetPy)
unionPy = _set_operation(_union, IFSetPy)
intersectionPy = _set_operation(_intersection, IFSetPy)
multiunionPy = _set_operation(_multiunion, IFSetPy)
weightedUnionPy = _set_operation(_weightedUnion, IFSetPy)
weightedIntersectionPy = _set_operation(_weightedIntersection, IFSetPy)

try:
    from ._IFBTree import IFBucket
except ImportError: #pragma NO COVER w/ C extensions
    IFBucket = IFBucketPy
    IFSet = IFSetPy
    IFBTree = IFBTreePy
    IFTreeSet = IFTreeSetPy
    IFTreeIterator = IFTreeIteratorPy
    difference = differencePy
    union = unionPy
    intersection = intersectionPy
    multiunion = multiunionPy
    weightedUnion = weightedUnionPy
    weightedIntersection = weightedIntersectionPy
else: #pragma NO COVER w/o C extensions
    from ._IFBTree import IFSet
    from ._IFBTree import IFBTree
    from ._IFBTree import IFTreeSet
    from ._IFBTree import IFTreeIterator
    from ._IFBTree import difference
    from ._IFBTree import union
    from ._IFBTree import intersection
    from ._IFBTree import multiunion
    from ._IFBTree import weightedUnion
    from ._IFBTree import weightedIntersection

Bucket = IFBucket
Set = IFSet
BTree = IFBTree
TreeSet = IFTreeSet

_fix_pickle(globals(), __name__)

moduleProvides(IIntegerFloatBTreeModule)
