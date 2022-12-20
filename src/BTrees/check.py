##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""
Utilities for working with BTrees (TreeSets, Buckets, and Sets) at a low
level.

The primary function is check(btree), which performs value-based consistency
checks of a kind ``BTree._Tree._check()`` does not perform.  See the function docstring
for details.

display(btree) displays the internal structure of a BTree (TreeSet, etc) to
stdout.

CAUTION:  When a BTree node has only a single bucket child, it can be
impossible to get at the bucket from Python code (__getstate__() may squash
the bucket object out of existence, as a pickling storage optimization).  In
such a case, the code here synthesizes a temporary bucket with the same keys
(and values, if the bucket is of a mapping type).  This has no first-order
consequences, but can mislead if you pay close attention to reported object
addresses and/or object identity (the synthesized bucket has an address
that doesn't exist in the actual BTree).
"""

# 32-bit signed int
from BTrees.IFBTree import IFBTree, IFBucket, IFSet, IFTreeSet
from BTrees.IFBTree import IFBTreePy, IFBucketPy, IFSetPy, IFTreeSetPy
from BTrees.IIBTree import IIBTree, IIBucket, IISet, IITreeSet
from BTrees.IIBTree import IIBTreePy, IIBucketPy, IISetPy, IITreeSetPy
from BTrees.IOBTree import IOBTree, IOBucket, IOSet, IOTreeSet
from BTrees.IOBTree import IOBTreePy, IOBucketPy, IOSetPy, IOTreeSetPy
from BTrees.IUBTree import IUBTree, IUBucket, IUSet, IUTreeSet
from BTrees.IUBTree import IUBTreePy, IUBucketPy, IUSetPy, IUTreeSetPy

# 32-bit unsigned int
from BTrees.UFBTree import UFBTree, UFBucket, UFSet, UFTreeSet
from BTrees.UFBTree import UFBTreePy, UFBucketPy, UFSetPy, UFTreeSetPy
from BTrees.UIBTree import UIBTree, UIBucket, UISet, UITreeSet
from BTrees.UIBTree import UIBTreePy, UIBucketPy, UISetPy, UITreeSetPy
from BTrees.UOBTree import UOBTree, UOBucket, UOSet, UOTreeSet
from BTrees.UOBTree import UOBTreePy, UOBucketPy, UOSetPy, UOTreeSetPy
from BTrees.UUBTree import UUBTree, UUBucket, UUSet, UUTreeSet
from BTrees.UUBTree import UUBTreePy, UUBucketPy, UUSetPy, UUTreeSetPy

# 64-bit signed int
from BTrees.LFBTree import LFBTree, LFBucket, LFSet, LFTreeSet
from BTrees.LFBTree import LFBTreePy, LFBucketPy, LFSetPy, LFTreeSetPy
from BTrees.LLBTree import LLBTree, LLBucket, LLSet, LLTreeSet
from BTrees.LLBTree import LLBTreePy, LLBucketPy, LLSetPy, LLTreeSetPy
from BTrees.LOBTree import LOBTree, LOBucket, LOSet, LOTreeSet
from BTrees.LOBTree import LOBTreePy, LOBucketPy, LOSetPy, LOTreeSetPy
from BTrees.LQBTree import LQBTree, LQBucket, LQSet, LQTreeSet
from BTrees.LQBTree import LQBTreePy, LQBucketPy, LQSetPy, LQTreeSetPy

# 64-bit unsigned int
from BTrees.QFBTree import QFBTree, QFBucket, QFSet, QFTreeSet
from BTrees.QFBTree import QFBTreePy, QFBucketPy, QFSetPy, QFTreeSetPy
from BTrees.QLBTree import QLBTree, QLBucket, QLSet, QLTreeSet
from BTrees.QLBTree import QLBTreePy, QLBucketPy, QLSetPy, QLTreeSetPy
from BTrees.QOBTree import QOBTree, QOBucket, QOSet, QOTreeSet
from BTrees.QOBTree import QOBTreePy, QOBucketPy, QOSetPy, QOTreeSetPy
from BTrees.QQBTree import QQBTree, QQBucket, QQSet, QQTreeSet
from BTrees.QQBTree import QQBTreePy, QQBucketPy, QQSetPy, QQTreeSetPy


from BTrees.OIBTree import OIBTree, OIBucket, OISet, OITreeSet
from BTrees.OIBTree import OIBTreePy, OIBucketPy, OISetPy, OITreeSetPy
from BTrees.OLBTree import OLBTree, OLBucket, OLSet, OLTreeSet
from BTrees.OLBTree import OLBTreePy, OLBucketPy, OLSetPy, OLTreeSetPy
from BTrees.OOBTree import OOBTree, OOBucket, OOSet, OOTreeSet
from BTrees.OOBTree import OOBTreePy, OOBucketPy, OOSetPy, OOTreeSetPy
from BTrees.OUBTree import OUBTree, OUBucket, OUSet, OUTreeSet
from BTrees.OUBTree import OUBTreePy, OUBucketPy, OUSetPy, OUTreeSetPy
from BTrees.OQBTree import OQBTree, OQBucket, OQSet, OQTreeSet
from BTrees.OQBTree import OQBTreePy, OQBucketPy, OQSetPy, OQTreeSetPy

from BTrees.fsBTree import fsBTree, fsBucket, fsSet, fsTreeSet
from BTrees.fsBTree import fsBTreePy, fsBucketPy, fsSetPy, fsTreeSetPy

from BTrees.utils import positive_id
from BTrees.utils import oid_repr

TYPE_UNKNOWN, TYPE_BTREE, TYPE_BUCKET = range(3)

from ._compat import compare

_type2kind = {}
_FAMILIES = (
    'OO', 'OI', 'OU', 'OL', 'OQ',
    'II', 'IO', 'IF', 'IU',
    'LL', 'LO', 'LF', 'LQ',
    'UU', 'UO', 'UF', 'UI',
    'QQ', 'QO', 'QF', 'QL',
    'fs',
)
for kv in _FAMILIES:
    for name, kind in (
            ('BTree', (TYPE_BTREE, True)),
            ('Bucket', (TYPE_BUCKET, True)),
            ('TreeSet', (TYPE_BTREE, False)),
            ('Set', (TYPE_BUCKET, False)),
    ):
        _type2kind[globals()[kv + name]] = kind
        py = kv + name + 'Py'
        _type2kind[globals()[py]] = kind

# Return pair
#
#     TYPE_BTREE or TYPE_BUCKET, is_mapping

def classify(obj):
    return _type2kind[type(obj)]


BTREE_EMPTY, BTREE_ONE, BTREE_NORMAL = range(3)

# If the BTree is empty, returns
#
#     BTREE_EMPTY, [], []
#
# If the BTree has only one bucket, sometimes returns
#
#     BTREE_ONE, bucket_state, None
#
# Else returns
#
#     BTREE_NORMAL, list of keys, list of kids
#
# and the list of kids has one more entry than the list of keys.
#
# BTree.__getstate__() docs:
#
# For an empty BTree (self->len == 0), None.
#
# For a BTree with one child (self->len == 1), and that child is a bucket,
# and that bucket has a NULL oid, a one-tuple containing a one-tuple
# containing the bucket's state:
#
#     (
#         (
#              child[0].__getstate__(),
#         ),
#     )
#
# Else a two-tuple.  The first element is a tuple interleaving the BTree's
# keys and direct children, of size 2*self->len - 1 (key[0] is unused and
# is not saved).  The second element is the firstbucket:
#
#     (
#          (child[0], key[1], child[1], key[2], child[2], ...,
#                                       key[len-1], child[len-1]),
#          self->firstbucket
#     )

_btree2bucket = {}
for kv in _FAMILIES:
    _btree2bucket[globals()[kv+'BTree']] = globals()[kv+'Bucket']
    py = kv + 'BTreePy'
    _btree2bucket[globals()[py]] = globals()[kv+'BucketPy']
    _btree2bucket[globals()[kv+'TreeSet']] = globals()[kv+'Set']
    py = kv + 'TreeSetPy'
    _btree2bucket[globals()[kv+'TreeSetPy']] = globals()[kv+'SetPy']


def crack_btree(t, is_mapping):
    state = t.__getstate__()
    if state is None:
        return BTREE_EMPTY, [], []

    assert isinstance(state, tuple)
    if len(state) == 1:
        state = state[0]
        assert isinstance(state, tuple) and len(state) == 1
        state = state[0]
        return BTREE_ONE, state, None

    assert len(state) == 2
    data, firstbucket = state
    n = len(data)
    assert n & 1
    kids = []
    keys = []
    i = 0
    for x in data:
        if i & 1:
            keys.append(x)
        else:
            kids.append(x)
        i += 1
    return BTREE_NORMAL, keys, kids

# Returns
#
#     keys, values  # for a mapping; len(keys) == len(values) in this case
# or
#     keys, []      # for a set
#
# bucket.__getstate__() docs:
#
# For a set bucket (self->values is NULL), a one-tuple or two-tuple.  The
# first element is a tuple of keys, of length self->len.  The second element
# is the next bucket, present if and only if next is non-NULL:
#
#     (
#          (keys[0], keys[1], ..., keys[len-1]),
#          <self->next iff non-NULL>
#     )
#
# For a mapping bucket (self->values is not NULL), a one-tuple or two-tuple.
# The first element is a tuple interleaving keys and values, of length
# 2 * self->len.  The second element is the next bucket, present iff next is
# non-NULL:
#
#     (
#          (keys[0], values[0], keys[1], values[1], ...,
#                               keys[len-1], values[len-1]),
#          <self->next iff non-NULL>
#     )

def crack_bucket(b, is_mapping):
    state = b.__getstate__()
    assert isinstance(state, tuple)
    assert 1 <= len(state) <= 2
    data = state[0]
    if not is_mapping:
        return data, []
    keys = []
    values = []
    n = len(data)
    assert n & 1 == 0
    i = 0
    for x in data:
        if i & 1:
            values.append(x)
        else:
            keys.append(x)
        i += 1
    return keys, values

def type_and_adr(obj):
    if hasattr(obj, '_p_oid'):
        oid = oid_repr(obj._p_oid)
    else:
        oid = 'None'
    return "{} (0x{:x} oid={})".format(type(obj).__name__, positive_id(obj), oid)

# Walker implements a depth-first search of a BTree (or TreeSet or Set or
# Bucket).  Subclasses must implement the visit_btree() and visit_bucket()
# methods, and arrange to call the walk() method.  walk() calls the
# visit_XYZ() methods once for each node in the tree, in depth-first
# left-to-right order.

class Walker:
    def __init__(self, obj):
        self.obj = obj

    # obj is the BTree (BTree or TreeSet).
    # path is a list of indices, from the root.  For example, if a BTree node
    # is child[5] of child[3] of the root BTree, [3, 5].
    # parent is the parent BTree object, or None if this is the root BTree.
    # is_mapping is True for a BTree and False for a TreeSet.
    # keys is a list of the BTree's internal keys.
    # kids is a list of the BTree's children.
    # If the BTree is an empty root node, keys == kids == [].
    # Else len(kids) == len(keys) + 1.
    # lo and hi are slice bounds on the values the elements of keys *should*
    # lie in (lo inclusive, hi exclusive).  lo is None if there is no lower
    # bound known, and hi is None if no upper bound is known.

    def visit_btree(self, obj, path, parent, is_mapping,
                    keys, kids, lo, hi):
        raise NotImplementedError

    # obj is the bucket (Bucket or Set).
    # path is a list of indices, from the root.  For example, if a bucket
    # node is child[5] of child[3] of the root BTree, [3, 5].
    # parent is the parent BTree object.
    # is_mapping is True for a Bucket and False for a Set.
    # keys is a list of the bucket's keys.
    # values is a list of the bucket's values.
    # If is_mapping is false, values == [].  Else len(keys) == len(values).
    # lo and hi are slice bounds on the values the elements of keys *should*
    # lie in (lo inclusive, hi exclusive).  lo is None if there is no lower
    # bound known, and hi is None if no upper bound is known.

    def visit_bucket(self, obj, path, parent, is_mapping,
                     keys, values, lo, hi):
        raise NotImplementedError

    def walk(self):
        obj = self.obj
        path = []
        stack = [(obj, path, None, None, None)]
        while stack:
            obj, path, parent, lo, hi = stack.pop()
            kind, is_mapping = classify(obj)
            if kind is TYPE_BTREE:
                bkind, keys, kids = crack_btree(obj, is_mapping)
                if bkind is BTREE_NORMAL:
                    # push the kids, in reverse order (so they're popped off
                    # the stack in forward order)
                    n = len(kids)
                    for i in range(len(kids)-1, -1, -1):
                        newlo, newhi = lo,  hi
                        if i < n-1:
                            newhi = keys[i]
                        if i > 0:
                            newlo = keys[i-1]
                        stack.append((kids[i],
                                      path + [i],
                                      obj,
                                      newlo,
                                      newhi))

                elif bkind is BTREE_EMPTY:
                    pass
                else:
                    assert bkind is BTREE_ONE
                    # Yuck.  There isn't a bucket object to pass on, as
                    # the bucket state is embedded directly in the BTree
                    # state.  Synthesize a bucket.
                    assert kids is None   # and "keys" is really the bucket
                                          # state
                    bucket = _btree2bucket[type(obj)]()
                    bucket.__setstate__(keys)
                    stack.append((bucket,
                                  path + [0],
                                  obj,
                                  lo,
                                  hi))
                    keys = []
                    kids = [bucket]

                self.visit_btree(obj,
                                 path,
                                 parent,
                                 is_mapping,
                                 keys,
                                 kids,
                                 lo,
                                 hi)
            else:
                assert kind is TYPE_BUCKET
                keys, values = crack_bucket(obj, is_mapping)
                self.visit_bucket(obj,
                                  path,
                                  parent,
                                  is_mapping,
                                  keys,
                                  values,
                                  lo,
                                  hi)


class Checker(Walker):
    def __init__(self, obj):
        Walker.__init__(self, obj)
        self.errors = []

    def check(self):
        self.walk()
        if self.errors:
            s = "Errors found in %s:" % type_and_adr(self.obj)
            self.errors.insert(0, s)
            s = "\n".join(self.errors)
            raise AssertionError(s)

    def visit_btree(self, obj, path, parent, is_mapping,
                    keys, kids, lo, hi):
        self.check_sorted(obj, path, keys, lo, hi)

    def visit_bucket(self, obj, path, parent, is_mapping,
                     keys, values, lo, hi):
        self.check_sorted(obj, path, keys, lo, hi)

    def check_sorted(self, obj, path, keys, lo, hi):
        i, n = 0, len(keys)
        for x in keys:
            # lo or hi are ommitted by supplying None. Thus the not
            # None checkes below.
            if lo is not None and not compare(lo, x) <= 0:
                s = "key %r < lower bound %r at index %d" % (x, lo, i)
                self.complain(s, obj, path)
            if hi is not None and not compare(x, hi) < 0:
                s = "key %r >= upper bound %r at index %d" % (x, hi, i)
                self.complain(s, obj, path)
            if i < n-1 and not compare(x, keys[i+1]) < 0:
                s = "key %r at index %d >= key %r at index %d" % (
                    x, i, keys[i+1], i+1)
                self.complain(s, obj, path)
            i += 1

    def complain(self, msg, obj, path):
        s = "{}, in {}, path from root {}".format(
                msg,
                type_and_adr(obj),
                ".".join(map(str, path)))
        self.errors.append(s)

class Printer(Walker): # pragma: no cover
    def __init__(self, obj):
        Walker.__init__(self, obj)

    def display(self):
        self.walk()

    def visit_btree(self, obj, path, parent, is_mapping,
                    keys, kids, lo, hi):
        indent = "    " * len(path)
        print("%s%s %s with %d children" % (
                  indent,
                  ".".join(map(str, path)),
                  type_and_adr(obj),
                  len(kids)))
        indent += "    "
        n = len(keys)
        for i in range(n):
            print("%skey %d: %r" % (indent, i, keys[i]))

    def visit_bucket(self, obj, path, parent, is_mapping,
                     keys, values, lo, hi):
        indent = "    " * len(path)
        print("%s%s %s with %d keys" % (
                  indent,
                  ".".join(map(str, path)),
                  type_and_adr(obj),
                  len(keys)))
        indent += "    "
        n = len(keys)
        for i in range(n):
            print("%skey %d: %r" % (indent, i, keys[i]),)
            if is_mapping:
                print("value {!r}".format(values[i]))

def check(btree):
    """Check internal value-based invariants in a BTree or TreeSet.

    The ``BTrees._base._Tree._check`` method checks internal C-level pointer consistency.
    The :func:`~BTrees.check.check` function here checks value-based invariants:  whether the
    keys in leaf bucket and internal nodes are in strictly increasing order,
    and whether they all lie in their expected range.  The latter is a subtle
    invariant that can't be checked locally -- it requires propagating
    range info down from the root of the tree, and modifying it at each
    level for each child.

    Raises :class:`AssertionError` if anything is wrong, with a string detail
    explaining the problems.  The entire tree is checked before
    :class:`AssertionError` is raised, and the string detail may be large (depending
    on how much went wrong).
    """

    Checker(btree).check()

def display(btree): # pragma: no cover
    "Display the internal structure of a BTree, Bucket, TreeSet or Set."
    Printer(btree).display()
