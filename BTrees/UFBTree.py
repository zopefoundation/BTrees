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
           'UFBucket', 'UFSet', 'UFBTree', 'UFTreeSet',
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
from ._base import to_uint as _to_key
from ._base import to_float as _to_value
from ._base import union as _union
from ._base import weightedIntersection as _weightedIntersection
from ._base import weightedUnion as _weightedUnion
from ._base import _fix_pickle
from ._compat import import_c_extension

_BUCKET_SIZE = 120
_TREE_SIZE = 500
using64bits = False

class UFBucketPy(Bucket):
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class UFSetPy(Set):
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class UFBTreePy(BTree):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class UFTreeSetPy(TreeSet):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class UFTreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

UFBucketPy._mapping_type = UFBucketPy._bucket_type = UFBucketPy
UFBucketPy._set_type = UFSetPy

UFSetPy._mapping_type = UFBucketPy
UFSetPy._set_type = UFSetPy._bucket_type = UFSetPy

UFBTreePy._mapping_type = UFBTreePy._bucket_type = UFBucketPy
UFBTreePy._set_type = UFSetPy

UFTreeSetPy._mapping_type = UFBucketPy
UFTreeSetPy._set_type = UFTreeSetPy._bucket_type = UFSetPy


differencePy = _set_operation(_difference, UFSetPy)
unionPy = _set_operation(_union, UFSetPy)
intersectionPy = _set_operation(_intersection, UFSetPy)
multiunionPy = _set_operation(_multiunion, UFSetPy)
weightedUnionPy = _set_operation(_weightedUnion, UFSetPy)
weightedIntersectionPy = _set_operation(_weightedIntersection, UFSetPy)

import_c_extension(globals())

_fix_pickle(globals(), __name__)

moduleProvides(IUnsignedFloatBTreeModule)
