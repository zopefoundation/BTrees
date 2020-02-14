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
           'UOBucket', 'UOSet', 'UOBTree', 'UOTreeSet',
           'union', 'intersection', 'difference', 'multiunion',
          )

from zope.interface import moduleProvides

from .Interfaces import IUnsignedObjectBTreeModule
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
from ._base import to_uint as _to_key
from ._base import to_ob as _to_value
from ._base import union as _union
from ._base import _fix_pickle
from ._compat import import_c_extension

_BUCKET_SIZE = 60
_TREE_SIZE = 500
using64bits = False


class UOBucketPy(Bucket):
    _to_key = _to_key
    _to_value = _to_value
    MERGE_WEIGHT = MERGE_WEIGHT_default


class UOSetPy(Set):
    _to_key = _to_key


class UOBTreePy(BTree):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE_WEIGHT = MERGE_WEIGHT_default


class UOTreeSetPy(TreeSet):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key

class UOTreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

UOBucketPy._mapping_type = UOBucketPy._bucket_type = UOBucketPy
UOBucketPy._set_type = UOSetPy

UOSetPy._mapping_type = UOBucketPy
UOSetPy._set_type = UOSetPy._bucket_type = UOSetPy

UOBTreePy._mapping_type = UOBTreePy._bucket_type = UOBucketPy
UOBTreePy._set_type = UOSetPy

UOTreeSetPy._mapping_type = UOBucketPy
UOTreeSetPy._set_type = UOTreeSetPy._bucket_type = UOSetPy


differencePy = _set_operation(_difference, UOSetPy)
unionPy = _set_operation(_union, UOSetPy)
intersectionPy = _set_operation(_intersection, UOSetPy)
multiunionPy = _set_operation(_multiunion, UOSetPy)

import_c_extension(globals())

_fix_pickle(globals(), __name__)

moduleProvides(IUnsignedObjectBTreeModule)
