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
           'IUBucket', 'IUSet', 'IUBTree', 'IUTreeSet',
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
from ._base import to_int as _to_key
from ._base import to_uint as _to_value
from ._base import union as _union
from ._base import weightedIntersection as _weightedIntersection
from ._base import weightedUnion as _weightedUnion
from ._base import _fix_pickle
from ._compat import import_c_extension

_BUCKET_SIZE = 120
_TREE_SIZE = 500
using64bits = False


class IUBucketPy(Bucket):
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class IUSetPy(Set):
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class IUBTreePy(BTree):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class IUTreeSetPy(TreeSet):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    MERGE = MERGE
    MERGE_WEIGHT = MERGE_WEIGHT_numeric
    MERGE_DEFAULT = MERGE_DEFAULT_int


class IUTreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

IUBucketPy._mapping_type = IUBucketPy._bucket_type = IUBucketPy
IUBucketPy._set_type = IUSetPy

IUSetPy._mapping_type = IUBucketPy
IUSetPy._set_type = IUSetPy._bucket_type = IUSetPy

IUBTreePy._mapping_type = IUBTreePy._bucket_type = IUBucketPy
IUBTreePy._set_type = IUSetPy

IUTreeSetPy._mapping_type = IUBucketPy
IUTreeSetPy._set_type = IUTreeSetPy._bucket_type = IUSetPy


differencePy = _set_operation(_difference, IUSetPy)
unionPy = _set_operation(_union, IUSetPy)
intersectionPy = _set_operation(_intersection, IUSetPy)
multiunionPy = _set_operation(_multiunion, IUSetPy)
weightedUnionPy = _set_operation(_weightedUnion, IUSetPy)
weightedIntersectionPy = _set_operation(_weightedIntersection, IUSetPy)

import_c_extension(globals())

_fix_pickle(globals(), __name__)

moduleProvides(IIntegerUnsignedBTreeModule)
