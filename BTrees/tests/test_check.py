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


def _assertRaises(self, e_type, checked, *args, **kw):
    try:
        checked(*args, **kw)
    except e_type as e:
        return e
    self.fail("Didn't raise: %s" % e_type.__name__)


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


class Test_crack_bucket(unittest.TestCase):

    def _callFUT(self, obj, is_mapping):
        from BTrees.check import crack_bucket
        return crack_bucket(obj, is_mapping)

    def test_w_empty_set(self):
        class EmptySet(object):
            def __getstate__(self):
                return ([],)
        keys, values = self._callFUT(EmptySet(), False)
        self.assertEqual(keys, [])
        self.assertEqual(values, [])

    def test_w_non_empty_set(self):
        class NonEmptySet(object):
            def __getstate__(self):
                return (['a', 'b', 'c'],)
        keys, values = self._callFUT(NonEmptySet(), False)
        self.assertEqual(keys, ['a', 'b', 'c'])
        self.assertEqual(values, [])

    def test_w_empty_mapping(self):
        class EmptyMapping(object):
            def __getstate__(self):
                return ([], object())
        keys, values = self._callFUT(EmptyMapping(), True)
        self.assertEqual(keys, [])
        self.assertEqual(values, [])

    def test_w_non_empty_mapping(self):
        class NonEmptyMapping(object):
            def __getstate__(self):
                return (['a', 1, 'b', 2, 'c', 3], object())
        keys, values = self._callFUT(NonEmptyMapping(), True)
        self.assertEqual(keys, ['a', 'b', 'c'])
        self.assertEqual(values, [1, 2, 3])


class Test_type_and_adr(unittest.TestCase):

    def _callFUT(self, obj):
        from BTrees.check import type_and_adr
        return type_and_adr(obj)

    def test_type_and_adr_w_oid(self):
        from BTrees.utils import oid_repr
        class WithOid(object):
            _p_oid = b'DEADBEEF'
        t_and_a = self._callFUT(WithOid())
        self.assertTrue(t_and_a.startswith('WithOid (0x'))
        self.assertTrue(t_and_a.endswith('oid=%s)' % oid_repr(b'DEADBEEF')))

    def test_type_and_adr_wo_oid(self):
        class WithoutOid(object):
            pass
        t_and_a = self._callFUT(WithoutOid())
        self.assertTrue(t_and_a.startswith('WithoutOid (0x'))
        self.assertTrue(t_and_a.endswith('oid=None)'))


class WalkerTests(unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.check import Walker
        return Walker

    def _makeOne(self, obj):
        return self._getTargetClass()(obj)

    def test_visit_btree_abstract(self):
        walker = self._makeOne(object())
        obj = object()
        path = '/'
        parent = object()
        is_mapping = True
        keys = []
        kids = []
        lo = 0
        hi = None
        self.assertRaises(NotImplementedError, walker.visit_btree,
                          obj, path, parent, is_mapping, keys, kids, lo, hi)

    def test_visit_bucket_abstract(self):
        walker = self._makeOne(object())
        obj = object()
        path = '/'
        parent = object()
        is_mapping = True
        keys = []
        kids = []
        lo = 0
        hi = None
        self.assertRaises(NotImplementedError, walker.visit_bucket,
                          obj, path, parent, is_mapping, keys, kids, lo, hi)

    def test_walk_w_empty_bucket(self):
        from BTrees.OOBTree import OOBucket
        obj = OOBucket()
        walker = self._makeOne(obj)
        path = '/'
        parent = object()
        is_mapping = True
        keys = []
        kids = []
        lo = 0
        hi = None
        self.assertRaises(NotImplementedError, walker.walk)

    def test_walk_w_empty_btree(self):
        from BTrees.OOBTree import OOBTree
        obj = OOBTree()
        walker = self._makeOne(obj)
        path = '/'
        parent = object()
        is_mapping = True
        keys = []
        kids = []
        lo = 0
        hi = None
        self.assertRaises(NotImplementedError, walker.walk)

    def test_walk_w_degenerate_btree(self):
        from BTrees.OOBTree import OOBTree
        obj = OOBTree()
        obj['a'] = 1
        walker = self._makeOne(obj)
        path = '/'
        parent = object()
        is_mapping = True
        keys = []
        kids = []
        lo = 0
        hi = None
        self.assertRaises(NotImplementedError, walker.walk)

    def test_walk_w_normal_btree(self):
        from BTrees.IIBTree import IIBTree
        obj = IIBTree()
        for i in range(1000):
            obj[i] = i
        walker = self._makeOne(obj)
        path = '/'
        parent = object()
        is_mapping = True
        keys = []
        kids = []
        lo = 0
        hi = None
        self.assertRaises(NotImplementedError, walker.walk)


class CheckerTests(unittest.TestCase):

    assertRaises = _assertRaises

    def _getTargetClass(self):
        from BTrees.check import Checker
        return Checker

    def _makeOne(self, obj):
        return self._getTargetClass()(obj)

    def test_walk_w_empty_bucket(self):
        from BTrees.OOBTree import OOBucket
        obj = OOBucket()
        checker = self._makeOne(obj)
        path = '/'
        parent = object()
        is_mapping = True
        keys = []
        kids = []
        lo = 0
        hi = None
        checker.check() #noraise

    def test_walk_w_empty_btree(self):
        obj = _makeTree(False)
        checker = self._makeOne(obj)
        path = '/'
        parent = object()
        is_mapping = True
        keys = []
        kids = []
        lo = 0
        hi = None
        checker.check() #noraise

    def test_walk_w_degenerate_btree(self):
        obj = _makeTree(False)
        obj['a'] = 1
        checker = self._makeOne(obj)
        path = '/'
        parent = object()
        is_mapping = True
        keys = []
        kids = []
        lo = 0
        hi = None
        checker.check() #noraise

    def test_walk_w_normal_btree(self):
        obj = _makeTree(False)
        checker = self._makeOne(obj)
        path = '/'
        parent = object()
        is_mapping = True
        keys = []
        kids = []
        lo = 0
        hi = None
        checker.check() #noraise

    def test_walk_w_key_too_large(self):
        obj = _makeTree(True)
        state = obj.__getstate__()
        # Damage an invariant by dropping the BTree key to 14.
        new_state = (state[0][0], 14, state[0][2]), state[1]
        obj.__setstate__(new_state)
        checker = self._makeOne(obj)
        path = '/'
        parent = object()
        is_mapping = True
        keys = []
        kids = []
        lo = 0
        hi = None
        e = self.assertRaises(AssertionError, checker.check)
        self.assertTrue(">= upper bound" in str(e))

    def test_walk_w_key_too_small(self):
        obj = _makeTree(True)
        state = obj.__getstate__()
        # Damage an invariant by bumping the BTree key to 16.
        new_state = (state[0][0], 16, state[0][2]), state[1]
        obj.__setstate__(new_state)
        checker = self._makeOne(obj)
        path = '/'
        parent = object()
        is_mapping = True
        keys = []
        kids = []
        lo = 0
        hi = None
        e = self.assertRaises(AssertionError, checker.check)
        self.assertTrue("< lower bound" in str(e))

    def test_walk_w_keys_swapped(self):
        obj = _makeTree(True)
        state = obj.__getstate__()
        # Damage an invariant by bumping the BTree key to 16.
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
        checker = self._makeOne(obj)
        path = '/'
        parent = object()
        is_mapping = True
        keys = []
        kids = []
        lo = 0
        hi = None
        e = self.assertRaises(AssertionError, checker.check)
        self.assertTrue("key 5 at index 4 >= key 4 at index 5" in str(e))


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
        from BTrees.OOBTree import OOBTree
        tree = OOBTree()
        for i in range(31):
            tree[i] = 2*i
        state = tree.__getstate__()
        self.assertEqual(len(state), 2)
        self.assertEqual(len(state[0]), 3)
        self.assertEqual(state[0][1], 15)
        self._callFUT(tree)   #noraise


def _makeTree(fill):
    from BTrees.OOBTree import OOBTree
    from BTrees.OOBTree import _BUCKET_SIZE
    tree = OOBTree()
    if fill:
        for i in range(_BUCKET_SIZE + 1):
            tree[i] = 2*i
    return tree


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_classify),
        unittest.makeSuite(Test_crack_btree),
        unittest.makeSuite(Test_crack_bucket),
        unittest.makeSuite(Test_type_and_adr),
        unittest.makeSuite(WalkerTests),
        unittest.makeSuite(CheckerTests),
        unittest.makeSuite(Test_check),
    ))
