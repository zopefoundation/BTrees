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
from BTrees.OOBTree import OOBTree, OOBucket

class B(OOBucket):
    pass

class T(OOBTree):
    _bucket_type = B
    max_leaf_size = 2
    max_internal_size = 3

class S(T):
    pass

import unittest

class SubclassTest(unittest.TestCase):

    def testSubclass(self):
        # test that a subclass that defines _bucket_type gets buckets
        # of that type
        t = T()
        t[0] = 0
        self.assertTrue(t._firstbucket.__class__ is B)

    def testCustomNodeSizes(self):
        # We override btree and bucket split sizes in BTree subclasses.
        t = S()
        for i in range(8):
            t[i] = i
        state = t.__getstate__()[0]
        self.assertEqual(len(state), 5)
        sub = state[0]
        self.assertEqual(sub.__class__, S)
        sub = sub.__getstate__()[0]
        self.assertEqual(len(sub), 5)
        sub = sub[0]
        self.assertEqual(sub.__class__, B)
        self.assertEqual(len(sub), 1)

def test_suite():
    return unittest.makeSuite(SubclassTest)
