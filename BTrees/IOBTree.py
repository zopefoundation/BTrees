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

from BTrees.Interfaces import IIntegerObjectBTreeModule
from BTrees.___BTree import Bucket
from BTrees.___BTree import Set
from BTrees.___BTree import Tree as BTree
from BTrees.___BTree import TreeSet
from BTrees.___BTree import difference as _difference
from BTrees.___BTree import intersection as _intersection
from BTrees.___BTree import multiunion as _multiunion
from BTrees.___BTree import setop as _setop
from BTrees.___BTree import to_int as _to_key
from BTrees.___BTree import to_ob as _to_value
from BTrees.___BTree import union as _union

_BUCKET_SIZE = 60
_TREE_SIZE = 500
using64bits = False

class IOBucketPy(Bucket):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
    _to_value = _to_value
    def MERGE_WEIGHT(self, value, weight):
        return value
try:
    from _IOBTree import IOBucket
except ImportError:
    IOBucket = IOBucketPy
Bucket = IOBucket


class IOSetPy(Set):
    MAX_SIZE = _BUCKET_SIZE
    _to_key = _to_key
try:
    from _IOBTree import IOSet
except ImportError:
    IOSet = IOSetPy
Set = IOSet


class IOBTreePy(BTree):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
    _to_value = _to_value
    def MERGE_WEIGHT(self, value, weight):
        return value
try:
    from _IOBTree import IOBTree
except ImportError:
    IOBTree = IOBTreePy
BTree = IOBTree


class IOTreeSetPy(TreeSet):
    MAX_SIZE = _TREE_SIZE
    _to_key = _to_key
try:
    from _IOBTree import IOTreeSet
except ImportError:
    IOTreeSet = IOTreeSetPy
TreeSet = IOTreeSet


# Can't declare forward refs, so fix up afterwards:

IOBucketPy._mapping_type = IOBucketPy._bucket_type = IOBucketPy
IOBucketPy._set_type = IOSetPy

IOSetPy._mapping_type = IOBucketPy
IOSetPy._set_type = IOSetPy._bucket_type = IOSetPy

IOBTreePy._mapping_type = IOBTreePy._bucket_type = IOBucketPy
IOBTreePy._set_type = IOSetPy

IOTreeSetPy._mapping_type = IOBucketPy
IOTreeSetPy._set_type = IOTreeSetPy._bucket_type = IOSetPy


differencePy = _setop(_difference, IOSetPy)
try:
    from _IOBTree import difference
except ImportError:
    difference = differencePy

unionPy = _setop(_union, IOSetPy)
try:
    from _IOBTree import union
except ImportError:
    union = unionPy

intersectionPy = _setop(_intersection, IOSetPy)
try:
    from _IOBTree import intersection
except ImportError:
    intersection = intersectionPy

multiunionPy = _setop(_multiunion, IOSetPy)
try:
    from _IOBTree import multiunion
except ImportError:
    multiunion = multiunionPy


moduleProvides(IIntegerObjectBTreeModule)
