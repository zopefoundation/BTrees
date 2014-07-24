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
           'IBBucket', 'IBSet', 'IBBTree', 'IBTreeSet',
           'union', 'intersection', 'difference',  
           'weightedUnion', 'weightedIntersection', 'multiunion',
          )

from zope.interface import moduleProvides

from .Interfaces import IIntegerByteBTreeModule
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

_BUCKET_SIZE = 120
_TREE_SIZE = 500
using64bits = False


class IBBucketPy(Bucket):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class IBSetPy(Set):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class IBBTreePy(BTree):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class IBTreeSetPy(TreeSet):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class IBTreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

IBBucketPy._mapping_type = IBBucketPy._bucket_type = IBBucketPy
IBBucketPy._set_type = IBSetPy

IBSetPy._mapping_type = IBBucketPy
IBSetPy._set_type = IBSetPy._bucket_type = IBSetPy

IBBTreePy._mapping_type = IBBTreePy._bucket_type = IBBucketPy
IBBTreePy._set_type = IBSetPy

IBTreeSetPy._mapping_type = IBBucketPy
IBTreeSetPy._set_type = IBTreeSetPy._bucket_type = IBSetPy


differencePy = _set_operation(_difference, IBSetPy)
unionPy = _set_operation(_union, IBSetPy)
intersectionPy = _set_operation(_intersection, IBSetPy)
multiunionPy = _set_operation(_multiunion, IBSetPy)
weightedUnionPy = _set_operation(_weightedUnion, IBSetPy)
weightedIntersectionPy = _set_operation(_weightedIntersection, IBSetPy)

try:
    from ._IBBTree import IBBucket
except ImportError: #pragma NO COVER w/ C extensions
    IBBucket = IBBucketPy
    IBSet = IBSetPy
    IBBTree = IBBTreePy
    IBTreeSet = IBTreeSetPy
    IBTreeIterator = IBTreeIteratorPy
    difference = differencePy
    union = unionPy
    intersection = intersectionPy
    multiunion = multiunionPy
    weightedUnion = weightedUnionPy
    weightedIntersection = weightedIntersectionPy
else: #pragma NO COVER w/o C extensions
    from ._IBBTree import IBSet
    from ._IBBTree import IBBTree
    from ._IBBTree import IBTreeSet
    from ._IBBTree import IBTreeIterator
    from ._IBBTree import difference
    from ._IBBTree import union
    from ._IBBTree import intersection
    from ._IBBTree import multiunion
    from ._IBBTree import weightedUnion
    from ._IBBTree import weightedIntersection

Bucket = IBBucket
Set = IBSet
BTree = IBBTree
TreeSet = IBTreeSet

moduleProvides(IIntegerByteBTreeModule)
