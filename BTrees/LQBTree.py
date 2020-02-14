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
           'LQBucket', 'LQSet', 'LQBTree', 'LQTreeSet',
           'union', 'intersection', 'difference',
           'weightedUnion', 'weightedIntersection', 'multiunion',
          )

from zope.interface import moduleProvides

from .Interfaces import IIntegerUnsignedBTreeModule
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
from ._base import to_ulong as _to_value
from ._base import union as _union
from ._base import weightedIntersection as _weightedIntersection
from ._base import weightedUnion as _weightedUnion
from ._base import _fix_pickle
from ._compat import import_c_extension

_BUCKET_SIZE = 120
_TREE_SIZE = 500
using64bits = True


class LQBucketPy(Bucket):
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class LQSetPy(Set):
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class LQBTreePy(BTree):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class LQTreeSetPy(TreeSet):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class LQTreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

LQBucketPy._mapping_type = LQBucketPy._bucket_type = LQBucketPy
LQBucketPy._set_type = LQSetPy

LQSetPy._mapping_type = LQBucketPy
LQSetPy._set_type = LQSetPy._bucket_type = LQSetPy

LQBTreePy._mapping_type = LQBTreePy._bucket_type = LQBucketPy
LQBTreePy._set_type = LQSetPy

LQTreeSetPy._mapping_type = LQBucketPy
LQTreeSetPy._set_type = LQTreeSetPy._bucket_type = LQSetPy


differencePy = _set_operation(_difference, LQSetPy)
unionPy = _set_operation(_union, LQSetPy)
intersectionPy = _set_operation(_intersection, LQSetPy)
multiunionPy = _set_operation(_multiunion, LQSetPy)
weightedUnionPy = _set_operation(_weightedUnion, LQSetPy)
weightedIntersectionPy = _set_operation(_weightedIntersection, LQSetPy)

import_c_extension(globals())

_fix_pickle(globals(), __name__)

moduleProvides(IIntegerUnsignedBTreeModule)
