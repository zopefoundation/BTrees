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
from BTrees.IBBTree import using64bits #XXX Ugly, but unavoidable

 
class IBBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IBBTree import IBBTree
        return IBBTree

 
class IBBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IBBTree import IBBTreePy
        return IBBTreePy


class IBTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IBBTree import IBTreeSet
        return IBTreeSet


class IBTreeSetPyInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IBBTree import IBTreeSetPy
        return IBTreeSetPy


class IBBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IBBTree import IBBucket
        return IBBucket


class IBBucketPyTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IBBTree import IBBucketPy
        return IBBucketPy


class IBTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IBBTree import IBTreeSet
        return IBTreeSet


class IBTreeSetPyTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IBBTree import IBTreeSetPy
        return IBTreeSetPy


class IBSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IBBTree import IBSet
        return IBSet


class IBSetPyTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IBBTree import IBSetPy
        return IBSetPy


class _IBBTreeTestBase(BTreeTests):

    def testIBBTreeOverflow(self):
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


class IBBTreeTest(_IBBTreeTestBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IBBTree import IBBTree
        return IBBTree()


class IBBTreeTestPy(_IBBTreeTestBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IBBTree import IBBTreePy
        return IBBTreePy()


if using64bits:

    class IBBTreeTest(BTreeTests, TestLongIntKeys, TestLongIntValues,
                      unittest.TestCase):

        def _makeOne(self):
            from BTrees.IBBTree import IBBTree
            return IBBTree()

        def getTwoValues(self):
            return 1, 2

    class IBBTreeTest(BTreeTests, TestLongIntKeys, TestLongIntValues,
                      unittest.TestCase):

        def _makeOne(self):
            from BTrees.IBBTree import IBBTreePy
            return IBBTreePy()

        def getTwoValues(self):
            return 1, 2


class _TestIBBTreesBase(object):

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


class TestIBBTrees(_TestIBBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IBBTree import IBBTree
        return IBBTree()


class TestIBBTreesPy(_TestIBBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IBBTree import IBBTreePy
        return IBBTreePy()


class TestIBSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IBBTree import IBSet
        return IBSet()


class TestIBSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IBBTree import IBSetPy
        return IBSetPy()


class TestIBTreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IBBTree import IBTreeSet
        return IBTreeSet()


class TestIBTreeSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IBBTree import IBTreeSetPy
        return IBTreeSetPy()


class PureIB(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.IBBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.IBBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.IBBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.IBBTree import IBBTree
        from BTrees.IBBTree import IBBucket
        from BTrees.IBBTree import IBTreeSet
        from BTrees.IBBTree import IBSet
        return IBSet, IBTreeSet, makeBuilder(IBBTree), makeBuilder(IBBucket)


class PureIBPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.IBBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.IBBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.IBBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.IBBTree import IBBTreePy
        from BTrees.IBBTree import IBBucketPy
        from BTrees.IBBTree import IBTreeSetPy
        from BTrees.IBBTree import IBSetPy
        return (IBSetPy, IBTreeSetPy,
                makeBuilder(IBBTreePy), makeBuilder(IBBucketPy))


class TestIBMultiUnion(MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.IBBTree import multiunion
        return multiunion(*args)

    def union(self, *args):
        from BTrees.IBBTree import union
        return union(*args)

    def mkset(self, *args):
        from BTrees.IBBTree import IBSet as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.IBBTree import IBTreeSet as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.IBBTree import IBBucket as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.IBBTree import IBBTree as mkbtree
        return mkbtree(*args)


class TestIBMultiUnionPy(MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.IBBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.IBBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.IBBTree import IBSetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.IBBTree import IBTreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.IBBTree import IBBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.IBBTree import IBBTreePy as mkbtree
        return mkbtree(*args)


class TestWeightedIB(Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.IBBTree import weightedUnion
        return weightedUnion

    def weightedIntersection(self):
        from BTrees.IBBTree import weightedIntersection
        return weightedIntersection

    def union(self):
        from BTrees.IBBTree import union
        return union

    def intersection(self):
        from BTrees.IBBTree import intersection
        return intersection

    def mkbucket(self, *args):
        from BTrees.IBBTree import IBBucket as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.IBBTree import IBBTree
        from BTrees.IBBTree import IBBucket
        from BTrees.IBBTree import IBTreeSet
        from BTrees.IBBTree import IBSet
        return IBBucket, IBBTree, itemsToSet(IBSet), itemsToSet(IBTreeSet)


class TestWeightedIBPy(Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.IBBTree import weightedUnionPy
        return weightedUnionPy

    def weightedIntersection(self):
        from BTrees.IBBTree import weightedIntersectionPy
        return weightedIntersectionPy

    def union(self):
        from BTrees.IBBTree import unionPy
        return unionPy

    def intersection(self):
        from BTrees.IBBTree import intersectionPy
        return intersectionPy

    def mkbucket(self, *args):
        from BTrees.IBBTree import IBBucketPy as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.IBBTree import IBBTreePy
        from BTrees.IBBTree import IBBucketPy
        from BTrees.IBBTree import IBTreeSetPy
        from BTrees.IBBTree import IBSetPy
        return (IBBucketPy, IBBTreePy,
                itemsToSet(IBSetPy), itemsToSet(IBTreeSetPy))


class IBBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IBBTree import IBBTree
        return IBBTree


class IBBTreeConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IBBTree import IBBTreePy
        return IBBTreePy


class IBBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IBBTree import IBBucket
        return IBBucket


class IBBucketConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IBBTree import IBBucketPy
        return IBBucketPy


class IBTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IBBTree import IBTreeSet
        return IBTreeSet


class IBTreeSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IBBTree import IBTreeSetPy
        return IBTreeSetPy


class IBSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IBBTree import IBSet
        return IBSet


class IBSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IBBTree import IBSetPy
        return IBSetPy


class IBModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'IB'

    def _getModule(self):
        import BTrees
        return BTrees.IBBTree
    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IIntegerByteBTreeModule



def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(IBBTreeInternalKeyTest),
        unittest.makeSuite(IBBTreePyInternalKeyTest),
        unittest.makeSuite(IBTreeSetInternalKeyTest),
        unittest.makeSuite(IBTreeSetPyInternalKeyTest),
        unittest.makeSuite(IBBucketTest),
        unittest.makeSuite(IBBucketPyTest),
        unittest.makeSuite(IBTreeSetTest),
        unittest.makeSuite(IBTreeSetPyTest),
        unittest.makeSuite(IBSetTest),
        unittest.makeSuite(IBSetPyTest),
        unittest.makeSuite(IBBTreeTest),
        unittest.makeSuite(IBBTreeTestPy),
        unittest.makeSuite(TestIBBTrees),
        unittest.makeSuite(TestIBBTreesPy),
        unittest.makeSuite(TestIBSets),
        unittest.makeSuite(TestIBSetsPy),
        unittest.makeSuite(TestIBTreeSets),
        unittest.makeSuite(TestIBTreeSetsPy),
        unittest.makeSuite(TestIBMultiUnion),
        unittest.makeSuite(TestIBMultiUnionPy),
        unittest.makeSuite(PureIB),
        unittest.makeSuite(PureIBPy),
        unittest.makeSuite(TestWeightedIB),
        unittest.makeSuite(TestWeightedIBPy),
        unittest.makeSuite(IBBTreeConflictTests),
        unittest.makeSuite(IBBTreeConflictTestsPy),
        unittest.makeSuite(IBBucketConflictTests),
        unittest.makeSuite(IBBucketConflictTestsPy),
        unittest.makeSuite(IBTreeSetConflictTests),
        unittest.makeSuite(IBTreeSetConflictTestsPy),
        unittest.makeSuite(IBSetConflictTests),
        unittest.makeSuite(IBSetConflictTestsPy),
        unittest.makeSuite(IBModuleTest),
    ))
