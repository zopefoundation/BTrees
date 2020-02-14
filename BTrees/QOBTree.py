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
           'QOBucket', 'QOSet', 'QOBTree', 'QOTreeSet',
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
from ._base import to_ulong as _to_key
from ._base import to_ob as _to_value
from ._base import union as _union
from ._base import _fix_pickle
from ._compat import import_c_extension

_BUCKET_SIZE = 60
_TREE_SIZE = 500
using64bits = True


class QOBucketPy(Bucket):
    _to_key = _to_key
    _to_value = _to_value
    MERGE_WEIGHT = MERGE_WEIGHT_default


class QOSetPy(Set):
    _to_key = _to_key


class QOBTreePy(BTree):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    MERGE_WEIGHT = MERGE_WEIGHT_default


class QOTreeSetPy(TreeSet):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key


class QOTreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

QOBucketPy._mapping_type = QOBucketPy._bucket_type = QOBucketPy
QOBucketPy._set_type = QOSetPy

QOSetPy._mapping_type = QOBucketPy
QOSetPy._set_type = QOSetPy._bucket_type = QOSetPy

QOBTreePy._mapping_type = QOBTreePy._bucket_type = QOBucketPy
QOBTreePy._set_type = QOSetPy

QOTreeSetPy._mapping_type = QOBucketPy
QOTreeSetPy._set_type = QOTreeSetPy._bucket_type = QOSetPy


differencePy = _set_operation(_difference, QOSetPy)
unionPy = _set_operation(_union, QOSetPy)
intersectionPy = _set_operation(_intersection, QOSetPy)
multiunionPy = _set_operation(_multiunion, QOSetPy)

import_c_extension(globals())

_fix_pickle(globals(), __name__)

moduleProvides(IUnsignedObjectBTreeModule)
