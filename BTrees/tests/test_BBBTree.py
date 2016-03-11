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
from BTrees.BBBTree import using64bits #XXX Ugly, but unavoidable

 
class BBBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BBBTree import BBBTree
        return BBBTree

 
class BBBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BBBTree import BBBTreePy
        return BBBTreePy


class BBTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BBBTree import BBTreeSet
        return BBTreeSet


class BBTreeSetPyInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BBBTree import BBTreeSetPy
        return BBTreeSetPy


class BBBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BBBTree import BBBucket
        return BBBucket


class BBBucketPyTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BBBTree import BBBucketPy
        return BBBucketPy


class BBTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BBBTree import BBTreeSet
        return BBTreeSet


class BBTreeSetPyTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BBBTree import BBTreeSetPy
        return BBTreeSetPy


class BBSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BBBTree import BBSet
        return BBSet


class BBSetPyTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BBBTree import BBSetPy
        return BBSetPy


class _BBBTreeTestBase(BTreeTests):

    def testBBBTreeOverflow(self):
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


class BBBTreeTest(_BBBTreeTestBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.BBBTree import BBBTree
        return BBBTree()


class BBBTreeTestPy(_BBBTreeTestBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.BBBTree import BBBTreePy
        return BBBTreePy()


if using64bits:

    class BBBTreeTest(BTreeTests, TestLongIntKeys, TestLongIntValues,
                      unittest.TestCase):

        def _makeOne(self):
            from BTrees.BBBTree import BBBTree
            return BBBTree()

        def getTwoValues(self):
            return 1, 2

    class BBBTreeTest(BTreeTests, TestLongIntKeys, TestLongIntValues,
                      unittest.TestCase):

        def _makeOne(self):
            from BTrees.BBBTree import BBBTreePy
            return BBBTreePy()

        def getTwoValues(self):
            return 1, 2


class _TestBBBTreesBase(object):

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


class TestBBBTrees(_TestBBBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.BBBTree import BBBTree
        return BBBTree()


class TestBBBTreesPy(_TestBBBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.BBBTree import BBBTreePy
        return BBBTreePy()


class TestBBSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.BBBTree import BBSet
        return BBSet()


class TestBBSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.BBBTree import BBSetPy
        return BBSetPy()


class TestBBTreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.BBBTree import BBTreeSet
        return BBTreeSet()


class TestBBTreeSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.BBBTree import BBTreeSetPy
        return BBTreeSetPy()


class PureBB(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.BBBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.BBBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.BBBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.BBBTree import BBBTree
        from BTrees.BBBTree import BBBucket
        from BTrees.BBBTree import BBTreeSet
        from BTrees.BBBTree import BBSet
        return BBSet, BBTreeSet, makeBuilder(BBBTree), makeBuilder(BBBucket)


class PureBBPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.BBBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.BBBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.BBBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.BBBTree import BBBTreePy
        from BTrees.BBBTree import BBBucketPy
        from BTrees.BBBTree import BBTreeSetPy
        from BTrees.BBBTree import BBSetPy
        return (BBSetPy, BBTreeSetPy,
                makeBuilder(BBBTreePy), makeBuilder(BBBucketPy))


class TestBBMultiUnion(MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.BBBTree import multiunion
        return multiunion(*args)

    def union(self, *args):
        from BTrees.BBBTree import union
        return union(*args)

    def mkset(self, *args):
        from BTrees.BBBTree import BBSet as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.BBBTree import BBTreeSet as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.BBBTree import BBBucket as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.BBBTree import BBBTree as mkbtree
        return mkbtree(*args)


class TestBBMultiUnionPy(MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.BBBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.BBBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.BBBTree import BBSetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.BBBTree import BBTreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.BBBTree import BBBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.BBBTree import BBBTreePy as mkbtree
        return mkbtree(*args)


class TestWeightedBB(Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.BBBTree import weightedUnion
        return weightedUnion

    def weightedIntersection(self):
        from BTrees.BBBTree import weightedIntersection
        return weightedIntersection

    def union(self):
        from BTrees.BBBTree import union
        return union

    def intersection(self):
        from BTrees.BBBTree import intersection
        return intersection

    def mkbucket(self, *args):
        from BTrees.BBBTree import BBBucket as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.BBBTree import BBBTree
        from BTrees.BBBTree import BBBucket
        from BTrees.BBBTree import BBTreeSet
        from BTrees.BBBTree import BBSet
        return BBBucket, BBBTree, itemsToSet(BBSet), itemsToSet(BBTreeSet)


class TestWeightedBBPy(Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.BBBTree import weightedUnionPy
        return weightedUnionPy

    def weightedIntersection(self):
        from BTrees.BBBTree import weightedIntersectionPy
        return weightedIntersectionPy

    def union(self):
        from BTrees.BBBTree import unionPy
        return unionPy

    def intersection(self):
        from BTrees.BBBTree import intersectionPy
        return intersectionPy

    def mkbucket(self, *args):
        from BTrees.BBBTree import BBBucketPy as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.BBBTree import BBBTreePy
        from BTrees.BBBTree import BBBucketPy
        from BTrees.BBBTree import BBTreeSetPy
        from BTrees.BBBTree import BBSetPy
        return (BBBucketPy, BBBTreePy,
                itemsToSet(BBSetPy), itemsToSet(BBTreeSetPy))


class BBBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BBBTree import BBBTree
        return BBBTree


class BBBTreeConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BBBTree import BBBTreePy
        return BBBTreePy


class BBBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BBBTree import BBBucket
        return BBBucket


class BBBucketConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BBBTree import BBBucketPy
        return BBBucketPy


class BBTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BBBTree import BBTreeSet
        return BBTreeSet


class BBTreeSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BBBTree import BBTreeSetPy
        return BBTreeSetPy


class BBSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BBBTree import BBSet
        return BBSet


class BBSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.BBBTree import BBSetPy
        return BBSetPy


class BBModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'BB'

    def _getModule(self):
        import BTrees
        return BTrees.BBBTree
    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IByteByteBTreeModule



def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(BBBTreeInternalKeyTest),
        unittest.makeSuite(BBBTreePyInternalKeyTest),
        unittest.makeSuite(BBTreeSetInternalKeyTest),
        unittest.makeSuite(BBTreeSetPyInternalKeyTest),
        unittest.makeSuite(BBBucketTest),
        unittest.makeSuite(BBBucketPyTest),
        unittest.makeSuite(BBTreeSetTest),
        unittest.makeSuite(BBTreeSetPyTest),
        unittest.makeSuite(BBSetTest),
        unittest.makeSuite(BBSetPyTest),
        unittest.makeSuite(BBBTreeTest),
        unittest.makeSuite(BBBTreeTestPy),
        unittest.makeSuite(TestBBBTrees),
        unittest.makeSuite(TestBBBTreesPy),
        unittest.makeSuite(TestBBSets),
        unittest.makeSuite(TestBBSetsPy),
        unittest.makeSuite(TestBBTreeSets),
        unittest.makeSuite(TestBBTreeSetsPy),
        unittest.makeSuite(TestBBMultiUnion),
        unittest.makeSuite(TestBBMultiUnionPy),
        unittest.makeSuite(PureBB),
        unittest.makeSuite(PureBBPy),
        unittest.makeSuite(TestWeightedBB),
        unittest.makeSuite(TestWeightedBBPy),
        unittest.makeSuite(BBBTreeConflictTests),
        unittest.makeSuite(BBBTreeConflictTestsPy),
        unittest.makeSuite(BBBucketConflictTests),
        unittest.makeSuite(BBBucketConflictTestsPy),
        unittest.makeSuite(BBTreeSetConflictTests),
        unittest.makeSuite(BBTreeSetConflictTestsPy),
        unittest.makeSuite(BBSetConflictTests),
        unittest.makeSuite(BBSetConflictTestsPy),
        unittest.makeSuite(BBModuleTest),
    ))
