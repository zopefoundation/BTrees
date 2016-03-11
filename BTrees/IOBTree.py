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
           'IOBucket', 'IOSet', 'IOBTree', 'IOTreeSet',
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
from ._base import to_int as _to_key
from ._base import to_ob as _to_value
from ._base import union as _union
from ._base import _fix_pickle

_BUCKET_SIZE = 60
_TREE_SIZE = 500
using64bits = False


class IOBucketPy(Bucket):
    _to_key = _to_key
    _to_value = _to_value
    MERGE_WEIGHT = MERGE_WEIGHT_default


class IOSetPy(Set):
    _to_key = _to_key


class IOBTreePy(BTree):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE_WEIGHT = MERGE_WEIGHT_default


class IOTreeSetPy(TreeSet):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key

class IOTreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

IOBucketPy._mapping_type = IOBucketPy._bucket_type = IOBucketPy
IOBucketPy._set_type = IOSetPy

IOSetPy._mapping_type = IOBucketPy
IOSetPy._set_type = IOSetPy._bucket_type = IOSetPy

IOBTreePy._mapping_type = IOBTreePy._bucket_type = IOBucketPy
IOBTreePy._set_type = IOSetPy

IOTreeSetPy._mapping_type = IOBucketPy
IOTreeSetPy._set_type = IOTreeSetPy._bucket_type = IOSetPy


differencePy = _set_operation(_difference, IOSetPy)
unionPy = _set_operation(_union, IOSetPy)
intersectionPy = _set_operation(_intersection, IOSetPy)
multiunionPy = _set_operation(_multiunion, IOSetPy)

try:
    from ._IOBTree import IOBucket
except ImportError: #pragma NO COVER w/ C extensions
    IOBucket = IOBucketPy
    IOSet = IOSetPy
    IOBTree = IOBTreePy
    IOTreeSet = IOTreeSetPy
    IOTreeIterator = IOTreeIteratorPy
    difference = differencePy
    union = unionPy
    intersection = intersectionPy
    multiunion = multiunionPy
else: #pragma NO COVER w/o C extensions
    from ._IOBTree import IOSet
    from ._IOBTree import IOBTree
    from ._IOBTree import IOTreeSet
    from ._IOBTree import IOTreeIterator
    from ._IOBTree import difference
    from ._IOBTree import union
    from ._IOBTree import intersection
    from ._IOBTree import multiunion

Bucket = IOBucket
Set = IOSet
BTree = IOBTree
TreeSet = IOTreeSet

_fix_pickle(globals(), __name__)

moduleProvides(IIntegerObjectBTreeModule)
