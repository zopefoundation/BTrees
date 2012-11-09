##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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

from zope.interface import moduleProvides

from BTrees.Interfaces import IObjectObjectBTreeModule
from BTrees.___BTree import Bucket
from BTrees.___BTree import Set
from BTrees.___BTree import Tree as BTree
from BTrees.___BTree import TreeSet
from BTrees.___BTree import difference as _difference
from BTrees.___BTree import intersection as _intersection
from BTrees.___BTree import setop as _setop
from BTrees.___BTree import union as _union
from BTrees.___BTree import to_ob as _to_key
from BTrees.___BTree import to_ob as _to_value

_BUCKET_SIZE = 30
_TREE_SIZE = 250
using64bits = False

class OOBucketPy(Bucket):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
    _to_value = _to_value
    def MERGE_WEIGHT(self, value, weight):
        return value
try:
    from _OOBTree import OOBucket
except ImportError:
    OOBucket = OOBucketPy
Bucket = OOBucket


class OOSetPy(Set):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
try:
    from _OOBTree import OOSet
except ImportError:
    OOSet = OOSetPy
Set = OOSet


class OOBTreePy(BTree):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    def MERGE_WEIGHT(self, value, weight):
        return value
try:
    from _OOBTree import OOBTree
except ImportError:
    OOBTree = OOBTreePy
BTree = OOBTree


class OOTreeSetPy(TreeSet):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
try:
    from _OOBTree import OOTreeSet
except ImportError:
    OOTreeSet = OOTreeSetPy
TreeSet = OOTreeSet


# Can't declare forward refs, so fix up afterwards:

OOBucketPy._mapping_type = OOBucketPy._bucket_type = OOBucketPy
OOBucketPy._set_type = OOSetPy

OOSetPy._mapping_type = OOSetPy
OOSetPy._set_type = OOSetPy._bucket_type = OOSetPy

OOBTreePy._mapping_type = OOBTreePy._bucket_type = OOBucketPy
OOBTreePy._set_type = OOSetPy

OOTreeSetPy._mapping_type = OOSetPy
OOTreeSetPy._set_type = OOTreeSetPy._bucket_type = OOSetPy


differencePy = _setop(_difference, OOSetPy)
try:
    from _OOBTree import difference
except ImportError:
    difference = differencePy

unionPy = _setop(_union, OOSetPy)
try:
    from _OOBTree import union
except ImportError:
    union = unionPy

intersectionPy = _setop(_intersection, OOSetPy)
try:
    from _OOBTree import intersection
except ImportError:
    intersection = intersectionPy


moduleProvides(IObjectObjectBTreeModule)
