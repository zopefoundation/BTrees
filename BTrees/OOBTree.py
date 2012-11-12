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
from ._base import difference as _difference
from ._base import intersection as _intersection
from ._base import setop as _setop
from ._base import to_ob as _to_key
from ._base import to_ob as _to_value
from ._base import union as _union

_BUCKET_SIZE = 30
_TREE_SIZE = 250
using64bits = False


class OOBucketPy(Bucket):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
    _to_value = _to_value

    def MERGE_WEIGHT(self, value, weight):
        return value

class OOSetPy(Set):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key


class OOBTreePy(BTree):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value

    def MERGE_WEIGHT(self, value, weight):
        return value


class OOTreeSetPy(TreeSet):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key


# Can't declare forward refs, so fix up afterwards:

OOBucketPy._mapping_type = OOBucketPy._bucket_type = OOBucketPy
OOBucketPy._set_type = OOSetPy

OOSetPy._mapping_type = OOBucketPy
OOSetPy._set_type = OOSetPy._bucket_type = OOSetPy

OOBTreePy._mapping_type = OOBTreePy._bucket_type = OOBucketPy
OOBTreePy._set_type = OOSetPy

OOTreeSetPy._mapping_type = OOBucketPy
OOTreeSetPy._set_type = OOTreeSetPy._bucket_type = OOSetPy


differencePy = _setop(_difference, OOSetPy)
unionPy = _setop(_union, OOSetPy)
intersectionPy = _setop(_intersection, OOSetPy)

try:
    from _OOBTree import OOBucket
    from _OOBTree import OOSet
    from _OOBTree import OOBTree
    from _OOBTree import OOTreeSet
    from _OOBTree import difference
    from _OOBTree import union
    from _OOBTree import intersection
except ImportError: #pragma NO COVER
    OOBucket = OOBucketPy
    OOSet = OOSetPy
    OOBTree = OOBTreePy
    OOTreeSet = OOTreeSetPy
    difference = differencePy
    union = unionPy
    intersection = intersectionPy

Bucket = OOBucket
Set = OOSet
BTree = OOBTree
TreeSet = OOTreeSet

moduleProvides(IObjectObjectBTreeModule)
