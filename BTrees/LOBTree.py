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
           'LOBucket', 'LOSet', 'LOBTree', 'LOTreeSet',
           'union', 'intersection', 'difference', 'multiunion',
          )

from zope.interface import moduleProvides

from .Interfaces import IIntegerObjectBTreeModule
from ._base import Bucket
from ._base import MERGE_WEIGHT_default
from ._base import Set
from ._base import Tree as BTree
from ._base import TreeSet
from ._base import _TreeIterator
from ._base import difference as _difference
from ._base import intersection as _intersection
from ._base import multiunion as _multiunion
from ._base import set_operation as _set_operation
from ._base import to_long as _to_key
from ._base import to_ob as _to_value
from ._base import union as _union
from ._base import _fix_pickle

_BUCKET_SIZE = 60
_TREE_SIZE = 500
using64bits = True


class LOBucketPy(Bucket):
    _to_key = _to_key
    _to_value = _to_value
    MERGE_WEIGHT = MERGE_WEIGHT_default


class LOSetPy(Set):
    _to_key = _to_key


class LOBTreePy(BTree):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE_WEIGHT = MERGE_WEIGHT_default


class LOTreeSetPy(TreeSet):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key


class LOTreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

LOBucketPy._mapping_type = LOBucketPy._bucket_type = LOBucketPy
LOBucketPy._set_type = LOSetPy

LOSetPy._mapping_type = LOBucketPy
LOSetPy._set_type = LOSetPy._bucket_type = LOSetPy

LOBTreePy._mapping_type = LOBTreePy._bucket_type = LOBucketPy
LOBTreePy._set_type = LOSetPy

LOTreeSetPy._mapping_type = LOBucketPy
LOTreeSetPy._set_type = LOTreeSetPy._bucket_type = LOSetPy


differencePy = _set_operation(_difference, LOSetPy)
unionPy = _set_operation(_union, LOSetPy)
intersectionPy = _set_operation(_intersection, LOSetPy)
multiunionPy = _set_operation(_multiunion, LOSetPy)

try:
    from ._LOBTree import LOBucket
except ImportError: #pragma NO COVER w/ C extensions
    LOBucket = LOBucketPy
    LOSet = LOSetPy
    LOBTree = LOBTreePy
    LOTreeSet = LOTreeSetPy
    LOTreeIterator = LOTreeIteratorPy
    difference = differencePy
    union = unionPy
    intersection = intersectionPy
    multiunion = multiunionPy
else: #pragma NO COVER w/o C extensions
    from ._LOBTree import LOSet
    from ._LOBTree import LOBTree
    from ._LOBTree import LOTreeSet
    from ._LOBTree import LOTreeIterator
    from ._LOBTree import difference
    from ._LOBTree import union
    from ._LOBTree import intersection
    from ._LOBTree import multiunion

Bucket = LOBucket
Set = LOSet
BTree = LOBTree
TreeSet = LOTreeSet

_fix_pickle(globals(), __name__)

moduleProvides(IIntegerObjectBTreeModule)
