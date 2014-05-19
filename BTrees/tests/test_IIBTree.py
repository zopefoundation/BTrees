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
from BTrees.IIBTree import using64bits #XXX Ugly, but unavoidable

 
class IIBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IIBTree
        return IIBTree

 
class IIBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IIBTreePy
        return IIBTreePy


class IITreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IITreeSet
        return IITreeSet


class IITreeSetPyInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IITreeSetPy
        return IITreeSetPy


class IIBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IIBucket
        return IIBucket


class IIBucketPyTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IIBucketPy
        return IIBucketPy


class IITreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IITreeSet
        return IITreeSet


class IITreeSetPyTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IITreeSetPy
        return IITreeSetPy


class IISetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IISet
        return IISet


class IISetPyTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IISetPy
        return IISetPy


class _IIBTreeTestBase(BTreeTests):

    def testIIBTreeOverflow(self):
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


class IIBTreeTest(_IIBTreeTestBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IIBTree import IIBTree
        return IIBTree()


class IIBTreeTestPy(_IIBTreeTestBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IIBTree import IIBTreePy
        return IIBTreePy()


if using64bits:

    class IIBTreeTest(BTreeTests, TestLongIntKeys, TestLongIntValues,
                      unittest.TestCase):

        def _makeOne(self):
            from BTrees.IIBTree import IIBTree
            return IIBTree()

        def getTwoValues(self):
            return 1, 2

    class IIBTreeTest(BTreeTests, TestLongIntKeys, TestLongIntValues,
                      unittest.TestCase):

        def _makeOne(self):
            from BTrees.IIBTree import IIBTreePy
            return IIBTreePy()

        def getTwoValues(self):
            return 1, 2


class _TestIIBTreesBase(object):

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


class TestIIBTrees(_TestIIBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IIBTree import IIBTree
        return IIBTree()


class TestIIBTreesPy(_TestIIBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IIBTree import IIBTreePy
        return IIBTreePy()


class TestIISets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IIBTree import IISet
        return IISet()


class TestIISetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IIBTree import IISetPy
        return IISetPy()


class TestIITreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IIBTree import IITreeSet
        return IITreeSet()


class TestIITreeSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IIBTree import IITreeSetPy
        return IITreeSetPy()


class PureII(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.IIBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.IIBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.IIBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.IIBTree import IIBTree
        from BTrees.IIBTree import IIBucket
        from BTrees.IIBTree import IITreeSet
        from BTrees.IIBTree import IISet
        return IISet, IITreeSet, makeBuilder(IIBTree), makeBuilder(IIBucket)


class PureIIPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.IIBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.IIBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.IIBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.IIBTree import IIBTreePy
        from BTrees.IIBTree import IIBucketPy
        from BTrees.IIBTree import IITreeSetPy
        from BTrees.IIBTree import IISetPy
        return (IISetPy, IITreeSetPy,
                makeBuilder(IIBTreePy), makeBuilder(IIBucketPy))


class TestIIMultiUnion(MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.IIBTree import multiunion
        return multiunion(*args)

    def union(self, *args):
        from BTrees.IIBTree import union
        return union(*args)

    def mkset(self, *args):
        from BTrees.IIBTree import IISet as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.IIBTree import IITreeSet as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.IIBTree import IIBucket as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.IIBTree import IIBTree as mkbtree
        return mkbtree(*args)


class TestIIMultiUnionPy(MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.IIBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.IIBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.IIBTree import IISetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.IIBTree import IITreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.IIBTree import IIBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.IIBTree import IIBTreePy as mkbtree
        return mkbtree(*args)


class TestWeightedII(Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.IIBTree import weightedUnion
        return weightedUnion

    def weightedIntersection(self):
        from BTrees.IIBTree import weightedIntersection
        return weightedIntersection

    def union(self):
        from BTrees.IIBTree import union
        return union

    def intersection(self):
        from BTrees.IIBTree import intersection
        return intersection

    def mkbucket(self, *args):
        from BTrees.IIBTree import IIBucket as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.IIBTree import IIBTree
        from BTrees.IIBTree import IIBucket
        from BTrees.IIBTree import IITreeSet
        from BTrees.IIBTree import IISet
        return IIBucket, IIBTree, itemsToSet(IISet), itemsToSet(IITreeSet)


class TestWeightedIIPy(Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.IIBTree import weightedUnionPy
        return weightedUnionPy

    def weightedIntersection(self):
        from BTrees.IIBTree import weightedIntersectionPy
        return weightedIntersectionPy

    def union(self):
        from BTrees.IIBTree import unionPy
        return unionPy

    def intersection(self):
        from BTrees.IIBTree import intersectionPy
        return intersectionPy

    def mkbucket(self, *args):
        from BTrees.IIBTree import IIBucketPy as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.IIBTree import IIBTreePy
        from BTrees.IIBTree import IIBucketPy
        from BTrees.IIBTree import IITreeSetPy
        from BTrees.IIBTree import IISetPy
        return (IIBucketPy, IIBTreePy,
                itemsToSet(IISetPy), itemsToSet(IITreeSetPy))


class IIBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IIBTree
        return IIBTree


class IIBTreeConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IIBTreePy
        return IIBTreePy


class IIBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IIBucket
        return IIBucket


class IIBucketConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IIBucketPy
        return IIBucketPy


class IITreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IITreeSet
        return IITreeSet


class IITreeSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IITreeSetPy
        return IITreeSetPy


class IISetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IISet
        return IISet


class IISetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IISetPy
        return IISetPy


class IIModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'II'

    def _getModule(self):
        import BTrees
        return BTrees.IIBTree
    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IIntegerIntegerBTreeModule



def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(IIBTreeInternalKeyTest),
        unittest.makeSuite(IIBTreePyInternalKeyTest),
        unittest.makeSuite(IITreeSetInternalKeyTest),
        unittest.makeSuite(IITreeSetPyInternalKeyTest),
        unittest.makeSuite(IIBucketTest),
        unittest.makeSuite(IIBucketPyTest),
        unittest.makeSuite(IITreeSetTest),
        unittest.makeSuite(IITreeSetPyTest),
        unittest.makeSuite(IISetTest),
        unittest.makeSuite(IISetPyTest),
        unittest.makeSuite(IIBTreeTest),
        unittest.makeSuite(IIBTreeTestPy),
        unittest.makeSuite(TestIIBTrees),
        unittest.makeSuite(TestIIBTreesPy),
        unittest.makeSuite(TestIISets),
        unittest.makeSuite(TestIISetsPy),
        unittest.makeSuite(TestIITreeSets),
        unittest.makeSuite(TestIITreeSetsPy),
        unittest.makeSuite(TestIIMultiUnion),
        unittest.makeSuite(TestIIMultiUnionPy),
        unittest.makeSuite(PureII),
        unittest.makeSuite(PureIIPy),
        unittest.makeSuite(TestWeightedII),
        unittest.makeSuite(TestWeightedIIPy),
        unittest.makeSuite(IIBTreeConflictTests),
        unittest.makeSuite(IIBTreeConflictTestsPy),
        unittest.makeSuite(IIBucketConflictTests),
        unittest.makeSuite(IIBucketConflictTestsPy),
        unittest.makeSuite(IITreeSetConflictTests),
        unittest.makeSuite(IITreeSetConflictTestsPy),
        unittest.makeSuite(IISetConflictTests),
        unittest.makeSuite(IISetConflictTestsPy),
        unittest.makeSuite(IIModuleTest),
    ))
