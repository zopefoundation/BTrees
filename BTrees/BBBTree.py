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
           'BBBucket', 'BBSet', 'BBBTree', 'BBTreeSet',
           'union', 'intersection', 'difference',  
           'weightedUnion', 'weightedIntersection', 'multiunion',
          )

from zope.interface import moduleProvides

from .Interfaces import IByteByteBTreeModule
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


class BBBucketPy(Bucket):
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class BBSetPy(Set):
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class BBBTreePy(BTree):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class BBTreeSetPy(TreeSet):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class BBTreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

BBBucketPy._mapping_type = BBBucketPy._bucket_type = BBBucketPy
BBBucketPy._set_type = BBSetPy

BBSetPy._mapping_type = BBBucketPy
BBSetPy._set_type = BBSetPy._bucket_type = BBSetPy

BBBTreePy._mapping_type = BBBTreePy._bucket_type = BBBucketPy
BBBTreePy._set_type = BBSetPy

BBTreeSetPy._mapping_type = BBBucketPy
BBTreeSetPy._set_type = BBTreeSetPy._bucket_type = BBSetPy


differencePy = _set_operation(_difference, BBSetPy)
unionPy = _set_operation(_union, BBSetPy)
intersectionPy = _set_operation(_intersection, BBSetPy)
multiunionPy = _set_operation(_multiunion, BBSetPy)
weightedUnionPy = _set_operation(_weightedUnion, BBSetPy)
weightedIntersectionPy = _set_operation(_weightedIntersection, BBSetPy)

try:
    from ._BBBTree import BBBucket
except ImportError: #pragma NO COVER w/ C extensions
    BBBucket = BBBucketPy
    BBSet = BBSetPy
    BBBTree = BBBTreePy
    BBTreeSet = BBTreeSetPy
    BBTreeIterator = BBTreeIteratorPy
    difference = differencePy
    union = unionPy
    intersection = intersectionPy
    multiunion = multiunionPy
    weightedUnion = weightedUnionPy
    weightedIntersection = weightedIntersectionPy
else: #pragma NO COVER w/o C extensions
    from ._BBBTree import BBSet
    from ._BBBTree import BBBTree
    from ._BBBTree import BBTreeSet
    from ._BBBTree import BBTreeIterator
    from ._BBBTree import difference
    from ._BBBTree import union
    from ._BBBTree import intersection
    from ._BBBTree import multiunion
    from ._BBBTree import weightedUnion
    from ._BBBTree import weightedIntersection

Bucket = BBBucket
Set = BBSet
BTree = BBBTree
TreeSet = BBTreeSet

_fix_pickle(globals(), __name__)

moduleProvides(IByteByteBTreeModule)
