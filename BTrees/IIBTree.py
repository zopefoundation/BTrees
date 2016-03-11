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
from ._base import to_int as _to_key
from ._base import to_int as _to_value
from ._base import union as _union
from ._base import weightedIntersection as _weightedIntersection
from ._base import weightedUnion as _weightedUnion
from ._base import _fix_pickle

_BUCKET_SIZE = 120
_TREE_SIZE = 500
using64bits = False


class IIBucketPy(Bucket):
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class IISetPy(Set):
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class IIBTreePy(BTree):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class IITreeSetPy(TreeSet):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class IITreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

IIBucketPy._mapping_type = IIBucketPy._bucket_type = IIBucketPy
IIBucketPy._set_type = IISetPy

IISetPy._mapping_type = IIBucketPy
IISetPy._set_type = IISetPy._bucket_type = IISetPy

IIBTreePy._mapping_type = IIBTreePy._bucket_type = IIBucketPy
IIBTreePy._set_type = IISetPy

IITreeSetPy._mapping_type = IIBucketPy
IITreeSetPy._set_type = IITreeSetPy._bucket_type = IISetPy


differencePy = _set_operation(_difference, IISetPy)
unionPy = _set_operation(_union, IISetPy)
intersectionPy = _set_operation(_intersection, IISetPy)
multiunionPy = _set_operation(_multiunion, IISetPy)
weightedUnionPy = _set_operation(_weightedUnion, IISetPy)
weightedIntersectionPy = _set_operation(_weightedIntersection, IISetPy)

try:
    from ._IIBTree import IIBucket
except ImportError: #pragma NO COVER w/ C extensions
    IIBucket = IIBucketPy
    IISet = IISetPy
    IIBTree = IIBTreePy
    IITreeSet = IITreeSetPy
    IITreeIterator = IITreeIteratorPy
    difference = differencePy
    union = unionPy
    intersection = intersectionPy
    multiunion = multiunionPy
    weightedUnion = weightedUnionPy
    weightedIntersection = weightedIntersectionPy
else: #pragma NO COVER w/o C extensions
    from ._IIBTree import IISet
    from ._IIBTree import IIBTree
    from ._IIBTree import IITreeSet
    from ._IIBTree import IITreeIterator
    from ._IIBTree import difference
    from ._IIBTree import union
    from ._IIBTree import intersection
    from ._IIBTree import multiunion
    from ._IIBTree import weightedUnion
    from ._IIBTree import weightedIntersection

Bucket = IIBucket
Set = IISet
BTree = IIBTree
TreeSet = IITreeSet

_fix_pickle(globals(), __name__)

moduleProvides(IIntegerIntegerBTreeModule)
