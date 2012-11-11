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
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import unittest


class Test_check(unittest.TestCase):

    def _callFUT(self, tree):
        from BTrees.check import check
        return check(tree)

    def _makeOne(self):
        from BTrees.OOBTree import OOBTree
        tree = OOBTree()
        for i in range(31):
            tree[i] = 2*i
        return tree

    def test_normal(self):
        # Looks like (state, first_bucket)
        # where state looks like (bucket0, 15, bucket1).
        tree = self._makeOne()
        state = tree.__getstate__()
        self.assertEqual(len(state), 2)
        self.assertEqual(len(state[0]), 3)
        self.assertEqual(state[0][1], 15)
        tree._check() # shouldn't blow up
        self._callFUT(tree)   # shouldn't blow up

    def test_key_too_large(self):
        # Damage an invariant by dropping the BTree key to 14.
        tree = self._makeOne()
        state = tree.__getstate__()
        news = (state[0][0], 14, state[0][2]), state[1]
        tree.__setstate__(news)
        tree._check() # not caught
        try:
            # Expecting "... key %r >= upper bound %r at index %d"
            self._callFUT(tree)
        except AssertionError as detail:
            self.assertTrue(">= upper bound" in str(detail))
        else:
            self.fail("expected check(tree) to catch the problem")

    def test_key_too_small(self):
        # Damage an invariant by bumping the BTree key to 16.
        tree = self._makeOne()
        state = tree.__getstate__()
        news = (state[0][0], 16, state[0][2]), state[1]
        tree.__setstate__(news)
        tree._check() # not caught
        try:
            # Expecting "... key %r < lower bound %r at index %d"
            self._callFUT(tree)
        except AssertionError as detail:
            self.assertTrue("< lower bound" in str(detail))
        else:
            self.fail("expected check(tree) to catch the problem")

    def test_keys_swapped(self):
        # Damage an invariant by swapping two key/value pairs.
        tree = self._makeOne()
        state = tree.__getstate__()
        # Looks like (state, first_bucket)
        # where state looks like (bucket0, 15, bucket1).
        (b0, num, b1), firstbucket = state
        self.assertEqual(b0[4], 8)
        self.assertEqual(b0[5], 10)
        b0state = b0.__getstate__()
        self.assertEqual(len(b0state), 2)
        # b0state looks like
        # ((k0, v0, k1, v1, ...), nextbucket)
        pairs, nextbucket = b0state
        self.assertEqual(pairs[8], 4)
        self.assertEqual(pairs[9], 8)
        self.assertEqual(pairs[10], 5)
        self.assertEqual(pairs[11], 10)
        newpairs = pairs[:8] + (5, 10, 4, 8) + pairs[12:]
        b0.__setstate__((newpairs, nextbucket))
        tree._check() # not caught
        try:
            self._callFUT(tree)
        except AssertionError, detail:
            self.assertTrue(
                "key 5 at index 4 >= key 4 at index 5" in str(detail))
        else:
            self.fail("expected check(tree) to catch the problem")


def test_suite():
    return unittest.makeSuite(Test_check)
