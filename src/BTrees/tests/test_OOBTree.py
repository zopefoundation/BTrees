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
from BTrees import OOBTree

from ._test_builder import update_module
from .common import BTreeTests


class OOBTreeTest(BTreeTests):

    def test_byValue(self):
        ITEMS = [(y, x) for x, y in enumerate('abcdefghijklmnopqrstuvwxyz')]
        tree = self._makeOne(ITEMS)
        self.assertEqual(list(tree.byValue(22)),
                         [(y, x) for x, y in reversed(ITEMS[22:])])

    def testRejectDefaultComparisonOnSet(self):
        # Check that passing in keys w default comparison fails. Only
        # applies to new-style class instances if we're using the C
        # extensions; old-style instances are too hard to introspect
        # in C.

        # This is white box because we know that the check is being
        # used in a function that's used in lots of places.
        # Otherwise, there are many permutations that would have to be
        # checked.
        t = self._makeOne()

        class OldStyle:
            pass

        if self._getTargetClass() is OOBTree.OOBTreePy:
            with self.assertRaises(TypeError):
                t[OldStyle()] = 1

        class C:
            pass

        with self.assertRaises(TypeError) as raising:
            t[C()] = 1

        self.assertEqual(
            raising.exception.args[0],
            "Object of class C has default comparison")

        class With___lt__:
            def __lt__(*args):
                return 1

        c = With___lt__()
        t[c] = 1
        t.clear()

        class With___lt__Old:
            def __lt__(*args):
                return 1

        c = With___lt__Old()
        t[c] = 1

        t.clear()

    def testAcceptDefaultComparisonOnGet(self):
        # Issue #42
        t = self._makeOne()

        class C:
            pass

        self.assertEqual(t.get(C(), 42), 42)
        self.assertRaises(KeyError, t.__getitem__, C())
        self.assertNotIn(C(), t)

    def testNewStyleClassWithCustomMetaClassAllowed(self):
        class Meta(type):
            def __lt__(cls, other):
                return 1

        cls = Meta('Class', (object,), {})
        m = self._makeOne()
        m[cls] = self.getTwoValues()[0]

    def test_None_is_smallest(self):
        t = self._makeOne()
        for i in range(999):  # Make sure we multiple buckets
            t[i] = i * i
        t[None] = -1
        for i in range(-99, 0):  # Make sure we multiple buckets
            t[i] = i * i
        self.assertEqual(list(t), [None] + list(range(-99, 999)))
        self.assertEqual(list(t.values()),
                         [-1] + [i * i for i in range(-99, 999)])
        self.assertEqual(t[2], 4)
        self.assertEqual(t[-2], 4)
        self.assertEqual(t[None], -1)
        t[None] = -2
        self.assertEqual(t[None], -2)
        t2 = t.__class__(t)
        del t[None]
        self.assertEqual(list(t), list(range(-99, 999)))

        if 'Py' in self.__class__.__name__:
            return
        from BTrees.OOBTree import difference
        from BTrees.OOBTree import intersection
        from BTrees.OOBTree import union
        self.assertEqual(list(difference(t2, t).items()), [(None, -2)])
        self.assertEqual(list(union(t, t2)), list(t2))
        self.assertEqual(list(intersection(t, t2)), list(t))

    def testDeleteNoneKey(self):
        # Check that a None key can be deleted in Python 2.
        # This doesn't work on Python 3 because None is unorderable,
        # so the tree can't be searched. But None also can't be inserted,
        # and we don't support migrating Python 2 databases to Python 3.
        t = self._makeOne()
        bucket_state = ((None, 42),)
        tree_state = ((bucket_state,),)
        t.__setstate__(tree_state)

        self.assertEqual(t[None], 42)
        del t[None]

    def testUnpickleNoneKey(self):
        # All versions (py2 and py3, C and Python) can unpickle
        # data that looks like this: {None: 42}, even though None
        # is unorderable..
        # This pickle was captured in BTree/ZODB3 3.10.7
        import pickle

        data = (
            b'ccopy_reg\n__newobj__\np0\n('
            b'cBTrees.OOBTree\nOOBTree\np1\ntp2\nRp3\n('
            b'(((NI42\ntp4\ntp5\ntp6\ntp7\nb.'
        )

        t = pickle.loads(data)
        keys = list(t)
        self.assertEqual([None], keys)

    def testIdentityTrumpsBrokenComparison(self):
        # Identical keys always match, even if their comparison is
        # broken. See https://github.com/zopefoundation/BTrees/issues/50
        from functools import total_ordering

        @total_ordering
        class Bad:
            def __eq__(self, other):
                return False

            __lt__ = __cmp__ = __eq__

        t = self._makeOne()
        bad_key = Bad()
        t[bad_key] = 42

        self.assertIn(bad_key, t)
        self.assertEqual(list(t), [bad_key])

        del t[bad_key]
        self.assertNotIn(bad_key, t)
        self.assertEqual(list(t), [])


update_module(globals(), OOBTree, btree_tests_base=OOBTreeTest)
