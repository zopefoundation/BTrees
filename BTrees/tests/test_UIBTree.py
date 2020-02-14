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
import unittest

from .common import UnsignedKeysBTreeTests as BTreeTests
from .common import UnsignedExtendedSetTests as ExtendedSetTests
from .common import I_SetsBase
from .common import InternalKeysMappingTest
from .common import UnsignedKeysMappingBase as MappingBase
from .common import UnsignedKeysMappingConflictTestBase as MappingConflictTestBase
from .common import ModuleTest
from .common import MultiUnion
from .common import UnsignedNormalSetTests as NormalSetTests
from .common import UnsignedSetConflictTestBase as SetConflictTestBase
from .common import SetResult
from .common import Weighted
from .common import itemsToSet
from .common import makeBuilder
from .common import UnsignedKeysMixin
from .common import UnsignedError



# pylint:disable=no-name-in-module,arguments-differ

class UIBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UIBTree import UIBTree
        return UIBTree


class UIBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UIBTree import UIBTreePy
        return UIBTreePy


class UIBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UIBTree import UIBucket
        return UIBucket


class UIBucketPyTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UIBTree import UIBucketPy
        return UIBucketPy


class UITreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UIBTree import UITreeSet
        return UITreeSet


class UITreeSetPyTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UIBTree import UITreeSetPy
        return UITreeSetPy


class UISetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UIBTree import UISet
        return UISet


class UISetPyTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UIBTree import UISetPy
        return UISetPy


class _UIBTreeTestBase(BTreeTests):

    def testUIBTreeOverflow(self):
        good = set()
        b = self._makeOne()

        def trial(i):
            i = int(i)
            try:
                b[i] = 0
            except (UnsignedError):
                __traceback_info__ = i
                if i > 2 ** 31:
                    with self.assertRaises(UnsignedError):
                        b[0] = i
            else:
                good.add(i)
                if i < 2 ** 31:
                    b[0] = i
                    self.assertEqual(b[0], i)
                else:
                    with self.assertRaises(UnsignedError):
                        b[0] = i

        for i in range((1<<31) - 3, (1<<31) + 3):
            trial(i)
            trial(-i)

        del b[0]
        self.assertEqual(sorted(good), sorted(b))


class UIBTreeTest(_UIBTreeTestBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UIBTree import UIBTree
        return UIBTree()


class UIBTreeTestPy(_UIBTreeTestBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UIBTree import UIBTreePy
        return UIBTreePy()


class _TestUIBTreesBase(object):

    def testNonIntegerKeyRaises(self):
        self.assertRaises(TypeError, self._stringraiseskey)
        self.assertRaises(TypeError, self._floatraiseskey)
        self.assertRaises(TypeError, self._noneraiseskey)

    def testNonIntegerValueRaises(self):
        self.assertRaises(TypeError, self._stringraisesvalue)
        self.assertRaises(TypeError, self._floatraisesvalue)
        self.assertRaises(TypeError, self._noneraisesvalue)

    def _stringraiseskey(self):
        self._makeOne()['c'] = 1

    def _floatraiseskey(self):
        self._makeOne()[2.5] = 1

    def _noneraiseskey(self):
        self._makeOne()[None] = 1

    def _stringraisesvalue(self):
        self._makeOne()[1] = 'c'

    def _floatraisesvalue(self):
        self._makeOne()[1] = 1.4

    def _noneraisesvalue(self):
        self._makeOne()[1] = None


class TestUIBTrees(_TestUIBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UIBTree import UIBTree
        return UIBTree()


class TestUIBTreesPy(_TestUIBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UIBTree import UIBTreePy
        return UIBTreePy()


class TestUISets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UIBTree import UISet
        return UISet()


class TestUISetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UIBTree import UISetPy
        return UISetPy()


class TestUITreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UIBTree import UITreeSet
        return UITreeSet()


class TestUITreeSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UIBTree import UITreeSetPy
        return UITreeSetPy()


class PureUI(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.UIBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.UIBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.UIBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.UIBTree import UIBTree
        from BTrees.UIBTree import UIBucket
        from BTrees.UIBTree import UITreeSet
        from BTrees.UIBTree import UISet
        return UISet, UITreeSet, makeBuilder(UIBTree), makeBuilder(UIBucket)


class PureUIPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.UIBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.UIBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.UIBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.UIBTree import UIBTreePy
        from BTrees.UIBTree import UIBucketPy
        from BTrees.UIBTree import UITreeSetPy
        from BTrees.UIBTree import UISetPy
        return (UISetPy, UITreeSetPy,
                makeBuilder(UIBTreePy), makeBuilder(UIBucketPy))


class TestUIMultiUnion(UnsignedKeysMixin, MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.UIBTree import multiunion
        return multiunion(*args)

    def union(self, *args):
        from BTrees.UIBTree import union
        return union(*args)

    def mkset(self, *args):
        from BTrees.UIBTree import UISet as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.UIBTree import UITreeSet as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.UIBTree import UIBucket as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.UIBTree import UIBTree as mkbtree
        return mkbtree(*args)


class TestUIMultiUnionPy(UnsignedKeysMixin, MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.UIBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.UIBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.UIBTree import UISetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.UIBTree import UITreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.UIBTree import UIBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.UIBTree import UIBTreePy as mkbtree
        return mkbtree(*args)


class TestWeightedUI(UnsignedKeysMixin, Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.UIBTree import weightedUnion
        return weightedUnion

    def weightedIntersection(self):
        from BTrees.UIBTree import weightedIntersection
        return weightedIntersection

    def union(self):
        from BTrees.UIBTree import union
        return union

    def intersection(self):
        from BTrees.UIBTree import intersection
        return intersection

    def mkbucket(self, *args):
        from BTrees.UIBTree import UIBucket as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.UIBTree import UIBTree
        from BTrees.UIBTree import UIBucket
        from BTrees.UIBTree import UITreeSet
        from BTrees.UIBTree import UISet
        return UIBucket, UIBTree, itemsToSet(UISet), itemsToSet(UITreeSet)


class TestWeightedUIPy(Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.UIBTree import weightedUnionPy
        return weightedUnionPy

    def weightedIntersection(self):
        from BTrees.UIBTree import weightedIntersectionPy
        return weightedIntersectionPy

    def union(self):
        from BTrees.UIBTree import unionPy
        return unionPy

    def intersection(self):
        from BTrees.UIBTree import intersectionPy
        return intersectionPy

    def mkbucket(self, *args):
        from BTrees.UIBTree import UIBucketPy as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.UIBTree import UIBTreePy
        from BTrees.UIBTree import UIBucketPy
        from BTrees.UIBTree import UITreeSetPy
        from BTrees.UIBTree import UISetPy
        return (UIBucketPy, UIBTreePy,
                itemsToSet(UISetPy), itemsToSet(UITreeSetPy))


class UIBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UIBTree import UIBTree
        return UIBTree


class UIBTreeConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UIBTree import UIBTreePy
        return UIBTreePy


class UIBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UIBTree import UIBucket
        return UIBucket


class UIBucketConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UIBTree import UIBucketPy
        return UIBucketPy


class UITreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UIBTree import UITreeSet
        return UITreeSet


class UITreeSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UIBTree import UITreeSetPy
        return UITreeSetPy


class UISetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UIBTree import UISet
        return UISet


class UISetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UIBTree import UISetPy
        return UISetPy


class UIModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'UI'

    def _getModule(self):
        import BTrees
        return BTrees.UIBTree
    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IUnsignedIntegerBTreeModule
