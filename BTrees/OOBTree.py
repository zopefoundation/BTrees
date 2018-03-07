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
           'OOBucket', 'OOSet', 'OOBTree', 'OOTreeSet',
           'union', 'intersection','difference',
          )

from zope.interface import moduleProvides

from .Interfaces import IObjectObjectBTreeModule
from ._base import Bucket
from ._base import Set
from ._base import Tree as BTree
from ._base import TreeSet
from ._base import _TreeIterator
from ._base import difference as _difference
from ._base import intersection as _intersection
from ._base import set_operation as _set_operation
from ._base import to_ob as _to_key
_to_value = _to_key
from ._base import union as _union
from ._base import _fix_pickle
from ._compat import import_c_extension

_BUCKET_SIZE = 30
_TREE_SIZE = 250
using64bits = False


class OOBucketPy(Bucket):
    _to_key = _to_key
    _to_value = _to_value


class OOSetPy(Set):
    _to_key = _to_key


class OOBTreePy(BTree):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value


class OOTreeSetPy(TreeSet):
    max_leaf_size = _BUCKET_SIZE
    max_internal_size = _TREE_SIZE
    _to_key = _to_key


class OOTreeIteratorPy(_TreeIterator):
    pass


# Can't declare forward refs, so fix up afterwards:

OOBucketPy._mapping_type = OOBucketPy._bucket_type = OOBucketPy
OOBucketPy._set_type = OOSetPy

OOSetPy._mapping_type = OOBucketPy
OOSetPy._set_type = OOSetPy._bucket_type = OOSetPy

OOBTreePy._mapping_type = OOBTreePy._bucket_type = OOBucketPy
OOBTreePy._set_type = OOSetPy

OOTreeSetPy._mapping_type = OOBucketPy
OOTreeSetPy._set_type = OOTreeSetPy._bucket_type = OOSetPy


differencePy = _set_operation(_difference, OOSetPy)
unionPy = _set_operation(_union, OOSetPy)
intersectionPy = _set_operation(_intersection, OOSetPy)

import_c_extension(globals())

_fix_pickle(globals(), __name__)

moduleProvides(IObjectObjectBTreeModule)
