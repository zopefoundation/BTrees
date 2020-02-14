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
           'OUBucket', 'OUSet', 'OUBTree', 'OUTreeSet',
           'union', 'intersection', 'difference',
           'weightedUnion', 'weightedIntersection',
          )

from zope.interface import moduleProvides

from .Interfaces import IObjectUnsignedBTreeModule
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
from ._base import to_uint as _to_value
from ._base import union as _union
from ._base import weightedIntersection as _weightedIntersection
from ._base import weightedUnion as _weightedUnion
from ._base import _fix_pickle
from ._compat import import_c_extension

_BUCKET_SIZE = 60
_TREE_SIZE = 250
using64bits = True

class OUBucketPy(Bucket):
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class OUSetPy(Set):
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class OUBTreePy(BTree):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class OUTreeSetPy(TreeSet):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_float


class OUTreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

OUBucketPy._mapping_type = OUBucketPy._bucket_type = OUBucketPy
OUBucketPy._set_type = OUSetPy

OUSetPy._mapping_type = OUBucketPy
OUSetPy._set_type = OUSetPy._bucket_type = OUSetPy

OUBTreePy._mapping_type = OUBTreePy._bucket_type = OUBucketPy
OUBTreePy._set_type = OUSetPy

OUTreeSetPy._mapping_type = OUBucketPy
OUTreeSetPy._set_type = OUTreeSetPy._bucket_type = OUSetPy


differencePy = _set_operation(_difference, OUSetPy)
unionPy = _set_operation(_union, OUSetPy)
intersectionPy = _set_operation(_intersection, OUSetPy)
weightedUnionPy = _set_operation(_weightedUnion, OUSetPy)
weightedIntersectionPy = _set_operation(_weightedIntersection, OUSetPy)

import_c_extension(globals())

_fix_pickle(globals(), __name__)

moduleProvides(IObjectUnsignedBTreeModule)
