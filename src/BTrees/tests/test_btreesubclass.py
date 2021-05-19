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
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import unittest

from BTrees.OOBTree import OOBTree, OOBucket

class B(OOBucket):
    pass

class T(OOBTree):
    _bucket_type = B
    max_leaf_size = 2
    max_internal_size = 3

class S(T):
    pass


class SubclassTest(unittest.TestCase):

    def testSubclass(self):
        # test that a subclass that defines _bucket_type gets buckets
        # of that type
        t = T()
        t[0] = 0
        self.assertTrue(t._firstbucket.__class__ is B)

    def testCustomNodeSizes(self, TreeKind=S, BucketKind=B):
        # We override btree and bucket split sizes in BTree subclasses.
        t = TreeKind()
        for i in range(8):
            t[i] = i

        state = t.__getstate__()[0]
        self.assertEqual(len(state), 5)
        sub = state[0]
        # __class__ is a property in the Python implementation, and
        # if the C extension is available it returns the C version.
        self.assertIsInstance(sub, TreeKind)
        sub = sub.__getstate__()[0]
        self.assertEqual(len(sub), 5)
        sub = sub[0]
        self.assertIsInstance(sub, BucketKind)
        self.assertEqual(len(sub), 1)

    def _checkReplaceNodeSizes(self, TreeKind, BucketKind):
        # We can also change the node sizes globally.
        orig_leaf = TreeKind.max_leaf_size
        orig_internal = TreeKind.max_internal_size
        TreeKind.max_leaf_size = T.max_leaf_size
        TreeKind.max_internal_size = T.max_internal_size
        try:
            self.testCustomNodeSizes(TreeKind, BucketKind)
        finally:
            TreeKind.max_leaf_size = orig_leaf
            TreeKind.max_internal_size = orig_internal

    def testReplaceNodeSizesNative(self):
        self._checkReplaceNodeSizes(OOBTree, OOBucket)

    def testReplaceNodeSizesPython(self):
        from BTrees.OOBTree import OOBTreePy
        from BTrees.OOBTree import OOBucketPy
        self._checkReplaceNodeSizes(OOBTreePy, OOBucketPy)
