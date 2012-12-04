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


class Test_classify(unittest.TestCase):

    def _callFUT(self, obj):
        from BTrees.check import classify
        return classify(obj)

    def test_classify_w_unknown(self):
        class NotClassified(object):
            pass
        self.assertRaises(KeyError, self._callFUT, NotClassified())

    def test_classify_w_bucket(self):
        from BTrees.OOBTree import OOBucketPy
        from BTrees.check import TYPE_BUCKET
        kind, is_mapping = self._callFUT(OOBucketPy())
        self.assertEqual(kind, TYPE_BUCKET)
        self.assertTrue(is_mapping)

    def test_classify_w_set(self):
        from BTrees.OOBTree import OOSetPy
        from BTrees.check import TYPE_BUCKET
        kind, is_mapping = self._callFUT(OOSetPy())
        self.assertEqual(kind, TYPE_BUCKET)
        self.assertFalse(is_mapping)

    def test_classify_w_tree(self):
        from BTrees.OOBTree import OOBTreePy
        from BTrees.check import TYPE_BTREE
        kind, is_mapping = self._callFUT(OOBTreePy())
        self.assertEqual(kind, TYPE_BTREE)
        self.assertTrue(is_mapping)

    def test_classify_w_treeset(self):
        from BTrees.OOBTree import OOTreeSetPy
        from BTrees.check import TYPE_BTREE
        kind, is_mapping = self._callFUT(OOTreeSetPy())
        self.assertEqual(kind, TYPE_BTREE)
        self.assertFalse(is_mapping)


class Test_crack_btree(unittest.TestCase):

    def _callFUT(self, obj, is_mapping):
        from BTrees.check import crack_btree
        return crack_btree(obj, is_mapping)

    def test_w_empty_tree(self):
        from BTrees.check import BTREE_EMPTY
        class Empty(object):
            def __getstate__(self):
                return None
        kind, keys, kids = self._callFUT(Empty(), True)
        self.assertEqual(kind, BTREE_EMPTY)
        self.assertEqual(keys, [])
        self.assertEqual(kids, [])

    def test_w_degenerate_tree(self):
        from BTrees.check import BTREE_ONE
        class Degenerate(object):
            def __getstate__(self):
                return ((('a', 1, 'b', 2),),)
        kind, keys, kids = self._callFUT(Degenerate(), True)
        self.assertEqual(kind, BTREE_ONE)
        self.assertEqual(keys, ('a', 1, 'b', 2))
        self.assertEqual(kids, None)

    def test_w_normal_tree(self):
        from BTrees.check import BTREE_NORMAL
        first_bucket = [object()] * 8
        second_bucket = [object()] * 8
        class Normal(object):
            def __getstate__(self):
                return ((first_bucket, 'b', second_bucket), first_bucket)
        kind, keys, kids = self._callFUT(Normal(), True)
        self.assertEqual(kind, BTREE_NORMAL)
        self.assertEqual(keys, ['b'])
        self.assertEqual(kids, [first_bucket, second_bucket])


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


class Test_helpers(unittest.TestCase):

    def test_type_and_adr_w_oid(self):
        from BTrees.check import type_and_adr
        class WOid(object):
            _p_oid = 'DEADBEEF'
        t_and_a = type_and_adr(WOid())
        self.assertTrue(t_and_a.startswith('WOid'))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_classify),
        unittest.makeSuite(Test_crack_btree),
        unittest.makeSuite(Test_check),
        unittest.makeSuite(Test_helpers),
    ))
