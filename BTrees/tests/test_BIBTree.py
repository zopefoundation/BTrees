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

from .common import BTreeTests
from .common import ExtendedSetTests
from .common import I_SetsBase
from .common import InternalKeysMappingTest
from .common import InternalKeysSetTest
from .common import MappingBase
from .common import MappingConflictTestBase
from .common import ModuleTest
from .common import MultiUnion
from .common import NormalSetTests
from .common import SetConflictTestBase
from .common import SetResult
from .common import TestLongIntKeys
from .common import TestLongIntValues
from .common import Weighted
from .common import itemsToSet
from .common import makeBuilder
from BTrees.BIBTree import using64bits #XXX Ugly, but unavoidable

 
class BIBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BIBTree import BIBTree
        return BIBTree

 
class BIBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BIBTree import BIBTreePy
        return BIBTreePy


class BITreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BIBTree import BITreeSet
        return BITreeSet


class BITreeSetPyInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BIBTree import BITreeSetPy
        return BITreeSetPy


class BIBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BIBTree import BIBucket
        return BIBucket


class BIBucketPyTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BIBTree import BIBucketPy
        return BIBucketPy


class BITreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BIBTree import BITreeSet
        return BITreeSet


class BITreeSetPyTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BIBTree import BITreeSetPy
        return BITreeSetPy


class BISetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BIBTree import BISet
        return BISet


class BISetPyTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BIBTree import BISetPy
        return BISetPy


class _BIBTreeTestBase(BTreeTests):

    def testBIBTreeOverflow(self):
        good = set()
        b = self._makeOne()

        def trial(i):
            i = int(i)
            try:
                b[i] = 0
            except OverflowError:
                self.assertRaises(OverflowError, b.__setitem__, 0, i)
            except TypeError:
                self.assertRaises(TypeError, b.__setitem__, 0, i)
            else:
                good.add(i)
                b[0] = i
                self.assertEqual(b[0], i)

        for i in range((1<<31) - 3, (1<<31) + 3):
            trial(i)
            trial(-i)

        del b[0]
        self.assertEqual(sorted(good), sorted(b))


class BIBTreeTest(_BIBTreeTestBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.BIBTree import BIBTree
        return BIBTree()


class BIBTreeTestPy(_BIBTreeTestBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.BIBTree import BIBTreePy
        return BIBTreePy()


if using64bits:

    class BIBTreeTest(BTreeTests, TestLongIntKeys, TestLongIntValues,
                      unittest.TestCase):

        def _makeOne(self):
            from BTrees.BIBTree import BIBTree
            return BIBTree()

        def getTwoValues(self):
            return 1, 2

    class BIBTreeTest(BTreeTests, TestLongIntKeys, TestLongIntValues,
                      unittest.TestCase):

        def _makeOne(self):
            from BTrees.BIBTree import BIBTreePy
            return BIBTreePy()

        def getTwoValues(self):
            return 1, 2


class _TestBIBTreesBase(object):

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


class TestBIBTrees(_TestBIBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.BIBTree import BIBTree
        return BIBTree()


class TestBIBTreesPy(_TestBIBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.BIBTree import BIBTreePy
        return BIBTreePy()


class TestBISets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.BIBTree import BISet
        return BISet()


class TestBISetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.BIBTree import BISetPy
        return BISetPy()


class TestBITreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.BIBTree import BITreeSet
        return BITreeSet()


class TestBITreeSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.BIBTree import BITreeSetPy
        return BITreeSetPy()


class PureBI(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.BIBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.BIBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.BIBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.BIBTree import BIBTree
        from BTrees.BIBTree import BIBucket
        from BTrees.BIBTree import BITreeSet
        from BTrees.BIBTree import BISet
        return BISet, BITreeSet, makeBuilder(BIBTree), makeBuilder(BIBucket)


class PureBIPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.BIBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.BIBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.BIBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.BIBTree import BIBTreePy
        from BTrees.BIBTree import BIBucketPy
        from BTrees.BIBTree import BITreeSetPy
        from BTrees.BIBTree import BISetPy
        return (BISetPy, BITreeSetPy,
                makeBuilder(BIBTreePy), makeBuilder(BIBucketPy))


class TestBIMultiUnion(MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.BIBTree import multiunion
        return multiunion(*args)

    def union(self, *args):
        from BTrees.BIBTree import union
        return union(*args)

    def mkset(self, *args):
        from BTrees.BIBTree import BISet as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.BIBTree import BITreeSet as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.BIBTree import BIBucket as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.BIBTree import BIBTree as mkbtree
        return mkbtree(*args)


class TestBIMultiUnionPy(MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.BIBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.BIBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.BIBTree import BISetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.BIBTree import BITreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.BIBTree import BIBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.BIBTree import BIBTreePy as mkbtree
        return mkbtree(*args)


class TestWeightedBI(Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.BIBTree import weightedUnion
        return weightedUnion

    def weightedIntersection(self):
        from BTrees.BIBTree import weightedIntersection
        return weightedIntersection

    def union(self):
        from BTrees.BIBTree import union
        return union

    def intersection(self):
        from BTrees.BIBTree import intersection
        return intersection

    def mkbucket(self, *args):
        from BTrees.BIBTree import BIBucket as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.BIBTree import BIBTree
        from BTrees.BIBTree import BIBucket
        from BTrees.BIBTree import BITreeSet
        from BTrees.BIBTree import BISet
        return BIBucket, BIBTree, itemsToSet(BISet), itemsToSet(BITreeSet)


class TestWeightedBIPy(Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.BIBTree import weightedUnionPy
        return weightedUnionPy

    def weightedIntersection(self):
        from BTrees.BIBTree import weightedIntersectionPy
        return weightedIntersectionPy

    def union(self):
        from BTrees.BIBTree import unionPy
        return unionPy

    def intersection(self):
        from BTrees.BIBTree import intersectionPy
        return intersectionPy

    def mkbucket(self, *args):
        from BTrees.BIBTree import BIBucketPy as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.BIBTree import BIBTreePy
        from BTrees.BIBTree import BIBucketPy
        from BTrees.BIBTree import BITreeSetPy
        from BTrees.BIBTree import BISetPy
        return (BIBucketPy, BIBTreePy,
                itemsToSet(BISetPy), itemsToSet(BITreeSetPy))


class BIBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BIBTree import BIBTree
        return BIBTree


class BIBTreeConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BIBTree import BIBTreePy
        return BIBTreePy


class BIBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BIBTree import BIBucket
        return BIBucket


class BIBucketConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BIBTree import BIBucketPy
        return BIBucketPy


class BITreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BIBTree import BITreeSet
        return BITreeSet


class BITreeSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BIBTree import BITreeSetPy
        return BITreeSetPy


class BISetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BIBTree import BISet
        return BISet


class BISetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BIBTree import BISetPy
        return BISetPy


class BIModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'BI'

    def _getModule(self):
        import BTrees
        return BTrees.BIBTree
    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IByteIntegerBTreeModule



def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(BIBTreeInternalKeyTest),
        unittest.makeSuite(BIBTreePyInternalKeyTest),
        unittest.makeSuite(BITreeSetInternalKeyTest),
        unittest.makeSuite(BITreeSetPyInternalKeyTest),
        unittest.makeSuite(BIBucketTest),
        unittest.makeSuite(BIBucketPyTest),
        unittest.makeSuite(BITreeSetTest),
        unittest.makeSuite(BITreeSetPyTest),
        unittest.makeSuite(BISetTest),
        unittest.makeSuite(BISetPyTest),
        unittest.makeSuite(BIBTreeTest),
        unittest.makeSuite(BIBTreeTestPy),
        unittest.makeSuite(TestBIBTrees),
        unittest.makeSuite(TestBIBTreesPy),
        unittest.makeSuite(TestBISets),
        unittest.makeSuite(TestBISetsPy),
        unittest.makeSuite(TestBITreeSets),
        unittest.makeSuite(TestBITreeSetsPy),
        unittest.makeSuite(TestBIMultiUnion),
        unittest.makeSuite(TestBIMultiUnionPy),
        unittest.makeSuite(PureBI),
        unittest.makeSuite(PureBIPy),
        unittest.makeSuite(TestWeightedBI),
        unittest.makeSuite(TestWeightedBIPy),
        unittest.makeSuite(BIBTreeConflictTests),
        unittest.makeSuite(BIBTreeConflictTestsPy),
        unittest.makeSuite(BIBucketConflictTests),
        unittest.makeSuite(BIBucketConflictTestsPy),
        unittest.makeSuite(BITreeSetConflictTests),
        unittest.makeSuite(BITreeSetConflictTestsPy),
        unittest.makeSuite(BISetConflictTests),
        unittest.makeSuite(BISetConflictTestsPy),
        unittest.makeSuite(BIModuleTest),
    ))
