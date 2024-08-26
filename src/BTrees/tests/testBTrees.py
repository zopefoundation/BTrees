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
import unittest

from BTrees.tests.common import permutations


class DegenerateBTree(unittest.TestCase):
    # Build a degenerate tree (set).  Boxes are BTree nodes.  There are
    # 5 leaf buckets, each containing a single int.  Keys in the BTree
    # nodes don't appear in the buckets.  Seven BTree nodes are purely
    # indirection nodes (no keys).  Buckets aren't all at the same depth:
    #
    #     +------------------------+
    #     |          4             |
    #     +------------------------+
    #         |              |
    #         |              v
    #         |             +-+
    #         |             | |
    #         |             +-+
    #         |              |
    #         v              v
    #     +-------+   +-------------+
    #     |   2   |   |   6     10  |
    #     +-------+   +-------------+
    #      |     |     |     |     |
    #      v     v     v     v     v
    #     +-+   +-+   +-+   +-+   +-+
    #     | |   | |   | |   | |   | |
    #     +-+   +-+   +-+   +-+   +-+
    #      |     |     |     |     |
    #      v     v     v     v     v
    #      1     3    +-+    7     11
    #                 | |
    #                 +-+
    #                  |
    #                  v
    #                  5
    #
    # This is nasty for many algorithms.  Consider a high-end range search
    # for 4.  The BTree nodes direct it to the 5 bucket, but the correct
    # answer is the 3 bucket, which requires going in a different direction
    # at the very top node already.  Consider a low-end range search for
    # 9.  The BTree nodes direct it to the 7 bucket, but the correct answer
    # is the 11 bucket.  This is also a nasty-case tree for deletions.

    def _build_degenerate_tree(self):
        # Build the buckets and chain them together.
        from BTrees.check import check
        from BTrees.IIBTree import IISet
        from BTrees.IIBTree import IITreeSet
        bucket11 = IISet([11])

        bucket7 = IISet()
        bucket7.__setstate__(((7,), bucket11))

        bucket5 = IISet()
        bucket5.__setstate__(((5,), bucket7))

        bucket3 = IISet()
        bucket3.__setstate__(((3,), bucket5))

        bucket1 = IISet()
        bucket1.__setstate__(((1,), bucket3))

        # Build the deepest layers of indirection nodes.
        ts = IITreeSet
        tree1 = ts()
        tree1.__setstate__(((bucket1,), bucket1))

        tree3 = ts()
        tree3.__setstate__(((bucket3,), bucket3))

        tree5lower = ts()
        tree5lower.__setstate__(((bucket5,), bucket5))
        tree5 = ts()
        tree5.__setstate__(((tree5lower,), bucket5))

        tree7 = ts()
        tree7.__setstate__(((bucket7,), bucket7))

        tree11 = ts()
        tree11.__setstate__(((bucket11,), bucket11))

        # Paste together the middle layers.
        tree13 = ts()
        tree13.__setstate__(((tree1, 2, tree3), bucket1))

        tree5711lower = ts()
        tree5711lower.__setstate__(((tree5, 6, tree7, 10, tree11), bucket5))
        tree5711 = ts()
        tree5711.__setstate__(((tree5711lower,), bucket5))

        # One more.
        t = ts()
        t.__setstate__(((tree13, 4, tree5711), bucket1))
        t._check()
        check(t)
        return t, [1, 3, 5, 7, 11]

    def testBasicOps(self):
        t, keys = self._build_degenerate_tree()
        self.assertEqual(len(t), len(keys))
        self.assertEqual(list(t.keys()), keys)

        self.assertTrue(t.has_key(1))
        self.assertTrue(t.has_key(3))
        self.assertTrue(t.has_key(5))
        self.assertTrue(t.has_key(7))
        self.assertTrue(t.has_key(11))
        for i in 0, 2, 4, 6, 8, 9, 10, 12:
            self.assertNotIn(i, t)

    def _checkRanges(self, tree, keys):
        self.assertEqual(len(tree), len(keys))
        sorted_keys = keys[:]
        sorted_keys.sort()
        self.assertEqual(list(tree.keys()), sorted_keys)
        for k in keys:
            self.assertIn(k, tree)
        if keys:
            lokey = sorted_keys[0]
            hikey = sorted_keys[-1]
            self.assertEqual(lokey, tree.minKey())
            self.assertEqual(hikey, tree.maxKey())
        else:
            lokey = hikey = 42

        # Try all range searches.
        for lo in range(lokey - 1, hikey + 2):
            for hi in range(lo - 1, hikey + 2):
                for skipmin in False, True:
                    for skipmax in False, True:
                        wantlo, wanthi = lo, hi
                        if skipmin:
                            wantlo += 1
                        if skipmax:
                            wanthi -= 1
                        want = [k for k in keys if wantlo <= k <= wanthi]
                        got = list(tree.keys(lo, hi, skipmin, skipmax))
                        self.assertEqual(want, got)

    def testRanges(self):
        t, keys = self._build_degenerate_tree()
        self._checkRanges(t, keys)

    def testDeletes(self):
        # Delete keys in all possible orders, checking each tree along
        # the way.

        # This is a tough test.  Previous failure modes included:
        # 1. A variety of assertion failures in _checkRanges.
        # 2. Assorted "Invalid firstbucket pointer" failures at
        #    seemingly random times, coming out of the BTree destructor.
        # 3. Under Python 2.3 CVS, some baffling
        #      RuntimeWarning: tp_compare didn't return -1 or -2 for exception
        #    warnings, possibly due to memory corruption after a BTree
        #    goes insane.
        # On CPython in PURE_PYTHON mode, this is a *slow* test, taking 15+s
        # on a 2015 laptop.
        from BTrees.check import check
        t, keys = self._build_degenerate_tree()
        for oneperm in permutations(keys):
            t, keys = self._build_degenerate_tree()
            for key in oneperm:
                t.remove(key)
                keys.remove(key)
                t._check()
                check(t)
                self._checkRanges(t, keys)
            # We removed all the keys, so the tree should be empty now.
            self.assertEqual(t.__getstate__(), None)

            # A damaged tree may trigger an "invalid firstbucket pointer"
            # failure at the time its destructor is invoked.  Try to force
            # that to happen now, so it doesn't look like a baffling failure
            # at some unrelated line.
            del t   # trigger destructor


LP294788_ids = {}


class ToBeDeleted:
    def __init__(self, id):
        assert isinstance(id, int)  # don't want to store any object ref here
        self.id = id

        global LP294788_ids
        LP294788_ids[id] = 1

    def __del__(self):
        global LP294788_ids
        LP294788_ids.pop(self.id, None)

    def __le__(self, other):
        return self.id <= other.id

    def __lt__(self, other):
        return self.id < other.id

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id

    def __hash__(self):
        return hash(self.id)


class TestBugFixes(unittest.TestCase):

    # Collector 1843.  Error returns were effectively ignored in
    # Bucket_rangeSearch(), leading to "delayed" errors, or worse.
    def testFixed1843(self):
        from BTrees.IIBTree import IISet
        t = IISet()
        t.insert(1)
        # This one used to fail to raise the TypeError when it occurred.
        self.assertRaises(TypeError, t.keys, "")
        # This one used to segfault.
        self.assertRaises(TypeError, t.keys, 0, "")

    def test_LP294788(self):
        # https://bugs.launchpad.net/bugs/294788
        # BTree keeps some deleted objects referenced

        # The logic here together with the ToBeDeleted class is that
        # a separate reference dict is populated on object creation
        # and removed in __del__
        # That means what's left in the reference dict is never GC'ed
        # therefore referenced somewhere
        # To simulate real life, some random data is used to exercise the tree
        import gc
        import random

        from BTrees.OOBTree import OOBTree

        t = OOBTree()

        trandom = random.Random('OOBTree')

        global LP294788_ids

        # /// BTree keys are integers, value is an object
        LP294788_ids = {}
        ids = {}
        for i in range(1024):
            if trandom.random() > 0.1 or not ids:
                # add
                id = None
                while id is None or id in ids:
                    id = trandom.randint(0, 1000000)

                ids[id] = 1
                t[id] = ToBeDeleted(id)
            else:
                # del
                keys = list(ids.keys())
                if keys:
                    id = trandom.choice(list(ids.keys()))
                    del t[id]
                    del ids[id]

        ids = ids.keys()
        trandom.shuffle(list(ids))
        for id in ids:
            del t[id]
        ids = None

        # to be on the safe side run a full GC
        gc.collect()

        # print LP294788_ids

        self.assertEqual(len(t), 0)
        self.assertEqual(len(LP294788_ids), 0)
        # \\\

        # /// BTree keys are integers, value is a tuple having an object
        LP294788_ids = {}
        ids = {}
        for i in range(1024):
            if trandom.random() > 0.1 or not ids:
                # add
                id = None
                while id is None or id in ids:
                    id = trandom.randint(0, 1000000)

                ids[id] = 1
                t[id] = (id, ToBeDeleted(id), 'somename')
            else:
                # del
                keys = list(ids.keys())
                if keys:
                    id = trandom.choice(keys)
                    del t[id]
                    del ids[id]

        ids = ids.keys()
        trandom.shuffle(list(ids))
        for id in ids:
            del t[id]
        ids = None

        # to be on the safe side run a full GC
        gc.collect()

        # print LP294788_ids

        self.assertEqual(len(t), 0)
        self.assertEqual(len(LP294788_ids), 0)
        # \\\

        # /// BTree keys are objects, value is an int
        t = OOBTree()
        LP294788_ids = {}
        ids = {}
        for i in range(1024):
            if trandom.random() > 0.1 or not ids:
                # add
                id = None
                while id is None or id in ids:
                    id = ToBeDeleted(trandom.randint(0, 1000000))

                ids[id] = 1
                t[id] = 1
            else:
                # del
                id = trandom.choice(list(ids.keys()))
                del ids[id]
                del t[id]

        ids = ids.keys()
        trandom.shuffle(list(ids))
        for id in ids:
            del t[id]
        # release all refs
        ids = id = None

        # to be on the safe side run a full GC
        gc.collect()

        # print LP294788_ids

        self.assertEqual(len(t), 0)
        self.assertEqual(len(LP294788_ids), 0)

        # /// BTree keys are tuples having objects, value is an int
        t = OOBTree()
        LP294788_ids = {}
        ids = {}
        for i in range(1024):
            if trandom.random() > 0.1 or not ids:
                # add
                id = None
                while id is None or id in ids:
                    id = trandom.randint(0, 1000000)
                    id = (id, ToBeDeleted(id), 'somename')

                ids[id] = 1
                t[id] = 1
            else:
                # del
                id = trandom.choice(list(ids.keys()))
                del ids[id]
                del t[id]

        ids = ids.keys()
        trandom.shuffle(list(ids))
        for id in ids:
            del t[id]
        # release all refs
        ids = id = None

        # to be on the safe side run a full GC
        gc.collect()

        # print LP294788_ids

        self.assertEqual(len(t), 0)
        self.assertEqual(len(LP294788_ids), 0)


# comparison error propagation tests


class DoesntLikeBeingCompared:

    def _cmp(self, other):
        raise ValueError('incomparable')

    __lt__ = __le__ = __eq__ = __ne__ = __ge__ = __gt__ = _cmp


class TestCmpError(unittest.TestCase):

    def testFoo(self):
        from BTrees.OOBTree import OOBTree
        t = OOBTree()
        t['hello world'] = None
        try:
            t[DoesntLikeBeingCompared()] = None
        except ValueError as e:
            self.assertEqual(str(e), 'incomparable')
        else:
            self.fail('incomarable objects should not be allowed into '
                      'the tree')


class FamilyTest(unittest.TestCase):
    def test32(self):
        from zope.interface.verify import verifyObject

        import BTrees
        from BTrees.IOBTree import IOTreeSet
        verifyObject(BTrees.Interfaces.IBTreeFamily, BTrees.family32)
        self.assertEqual(
            BTrees.family32.IO, BTrees.IOBTree)
        self.assertEqual(
            BTrees.family32.OI, BTrees.OIBTree)
        self.assertEqual(
            BTrees.family32.II, BTrees.IIBTree)
        self.assertEqual(
            BTrees.family32.IF, BTrees.IFBTree)
        self.assertEqual(
            BTrees.family32.UO, BTrees.UOBTree)
        self.assertEqual(
            BTrees.family32.OU, BTrees.OUBTree)
        self.assertEqual(
            BTrees.family32.UU, BTrees.UUBTree)
        self.assertEqual(
            BTrees.family32.UF, BTrees.UFBTree)
        self.assertEqual(
            BTrees.family32.OO, BTrees.OOBTree)
        self.assertEqual(
            BTrees.family32.OU, BTrees.OUBTree)
        s = IOTreeSet()
        s.insert(BTrees.family32.maxint)
        self.assertIn(BTrees.family32.maxint, s)
        s = IOTreeSet()
        s.insert(BTrees.family32.minint)
        self.assertIn(BTrees.family32.minint, s)
        s = IOTreeSet()
        # this next bit illustrates an, um, "interesting feature".  If
        # the characteristics change to match the 64 bit version, please
        # feel free to change.
        with self.assertRaises((TypeError, OverflowError)):
            s.insert(BTrees.family32.maxint + 1)

        with self.assertRaises((TypeError, OverflowError)):
            s.insert(BTrees.family32.minint - 1)
        self.check_pickling(BTrees.family32)

    def test64(self):
        from zope.interface.verify import verifyObject

        import BTrees
        from BTrees.LOBTree import LOTreeSet
        verifyObject(BTrees.Interfaces.IBTreeFamily, BTrees.family64)
        self.assertEqual(
            BTrees.family64.IO, BTrees.LOBTree)
        self.assertEqual(
            BTrees.family64.OI, BTrees.OLBTree)
        self.assertEqual(
            BTrees.family64.II, BTrees.LLBTree)
        self.assertEqual(
            BTrees.family64.IF, BTrees.LFBTree)
        self.assertEqual(
            BTrees.family64.UO, BTrees.QOBTree)
        self.assertEqual(
            BTrees.family64.OU, BTrees.OQBTree)
        self.assertEqual(
            BTrees.family64.UU, BTrees.QQBTree)
        self.assertEqual(
            BTrees.family64.UF, BTrees.QFBTree)
        self.assertEqual(
            BTrees.family64.OO, BTrees.OOBTree)
        self.assertEqual(
            BTrees.family64.OU, BTrees.OQBTree)
        s = LOTreeSet()
        s.insert(BTrees.family64.maxint)
        self.assertIn(BTrees.family64.maxint, s)
        s = LOTreeSet()
        s.insert(BTrees.family64.minint)
        self.assertIn(BTrees.family64.minint, s)
        s = LOTreeSet()

        # XXX why oh why do we expect ValueError here, but TypeError in test32?
        with self.assertRaises((TypeError, OverflowError)):
            s.insert(BTrees.family64.maxint + 1)

        with self.assertRaises((TypeError, OverflowError)):
            s.insert(BTrees.family64.minint - 1)

        self.check_pickling(BTrees.family64)

    def check_pickling(self, family):
        # The "family" objects are singletons; they can be pickled and
        # unpickled, and the same instances will always be returned on
        # unpickling, whether from the same unpickler or different
        # unpicklers.
        import pickle
        from io import BytesIO

        s = pickle.dumps((family, family))
        (f1, f2) = pickle.loads(s)
        self.assertIs(f1, family)
        self.assertIs(f2, family)

        # Using a single memo across multiple pickles:
        sio = BytesIO()
        p = pickle.Pickler(sio)
        p.dump(family)
        p.dump([family])
        u = pickle.Unpickler(BytesIO(sio.getvalue()))
        f1 = u.load()
        f2, = u.load()
        self.assertIs(f1, family)
        self.assertIs(f2, family)

        # Using separate memos for each pickle:
        sio = BytesIO()
        p = pickle.Pickler(sio)
        p.dump(family)
        p.clear_memo()
        p.dump([family])
        u = pickle.Unpickler(BytesIO(sio.getvalue()))
        f1 = u.load()
        f2, = u.load()
        self.assertIs(f1, family)
        self.assertIs(f2, family)
