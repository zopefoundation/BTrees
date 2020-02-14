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
           'QLBucket', 'QLSet', 'QLBTree', 'QLTreeSet',
           'union', 'intersection', 'difference',
           'weightedUnion', 'weightedIntersection', 'multiunion',
          )

from zope.interface import moduleProvides

from .Interfaces import IUnsignedIntegerBTreeModule
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
from ._base import to_ulong as _to_key
from ._base import to_long as _to_value
from ._base import union as _union
from ._base import weightedIntersection as _weightedIntersection
from ._base import weightedUnion as _weightedUnion
from ._base import _fix_pickle
from ._compat import import_c_extension

_BUCKET_SIZE = 120
_TREE_SIZE = 500
using64bits = True


class QLBucketPy(Bucket):
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class QLSetPy(Set):
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class QLBTreePy(BTree):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class QLTreeSetPy(TreeSet):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class QLTreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

QLBucketPy._mapping_type = QLBucketPy._bucket_type = QLBucketPy
QLBucketPy._set_type = QLSetPy

QLSetPy._mapping_type = QLBucketPy
QLSetPy._set_type = QLSetPy._bucket_type = QLSetPy

QLBTreePy._mapping_type = QLBTreePy._bucket_type = QLBucketPy
QLBTreePy._set_type = QLSetPy

QLTreeSetPy._mapping_type = QLBucketPy
QLTreeSetPy._set_type = QLTreeSetPy._bucket_type = QLSetPy


differencePy = _set_operation(_difference, QLSetPy)
unionPy = _set_operation(_union, QLSetPy)
intersectionPy = _set_operation(_intersection, QLSetPy)
multiunionPy = _set_operation(_multiunion, QLSetPy)
weightedUnionPy = _set_operation(_weightedUnion, QLSetPy)
weightedIntersectionPy = _set_operation(_weightedIntersection, QLSetPy)

import_c_extension(globals())

_fix_pickle(globals(), __name__)

moduleProvides(IUnsignedIntegerBTreeModule)
