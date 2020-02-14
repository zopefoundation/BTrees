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
           'QFBucket', 'QFSet', 'QFBTree', 'QFTreeSet',
           'union', 'intersection', 'difference',
           'weightedUnion', 'weightedIntersection', 'multiunion',
          )

from zope.interface import moduleProvides

from .Interfaces import IUnsignedFloatBTreeModule
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
from ._base import to_ulong as _to_key
from ._base import to_float as _to_value
from ._base import union as _union
from ._base import weightedIntersection as _weightedIntersection
from ._base import weightedUnion as _weightedUnion
from ._base import _fix_pickle
from ._compat import import_c_extension

_BUCKET_SIZE = 120
_TREE_SIZE = 500
using64bits = True


class QFBucketPy(Bucket):
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class QFSetPy(Set):
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class QFBTreePy(BTree):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class QFTreeSetPy(TreeSet):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class QFTreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

QFBucketPy._mapping_type = QFBucketPy._bucket_type = QFBucketPy
QFBucketPy._set_type = QFSetPy

QFSetPy._mapping_type = QFBucketPy
QFSetPy._set_type = QFSetPy._bucket_type = QFSetPy

QFBTreePy._mapping_type = QFBTreePy._bucket_type = QFBucketPy
QFBTreePy._set_type = QFSetPy

QFTreeSetPy._mapping_type = QFBucketPy
QFTreeSetPy._set_type = QFTreeSetPy._bucket_type = QFSetPy


differencePy = _set_operation(_difference, QFSetPy)
unionPy = _set_operation(_union, QFSetPy)
intersectionPy = _set_operation(_intersection, QFSetPy)
multiunionPy = _set_operation(_multiunion, QFSetPy)
weightedUnionPy = _set_operation(_weightedUnion, QFSetPy)
weightedIntersectionPy = _set_operation(_weightedIntersection, QFSetPy)

import_c_extension(globals())

_fix_pickle(globals(), __name__)

moduleProvides(IUnsignedFloatBTreeModule)
