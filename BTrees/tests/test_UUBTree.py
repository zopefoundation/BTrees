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

from .common import UnsignedBTreeTests as BTreeTests
from .common import UnsignedExtendedSetTests as ExtendedSetTests
from .common import I_SetsBase
from .common import InternalKeysMappingTest
from .common import InternalKeysSetTest
from .common import UnsignedMappingBase as MappingBase
from .common import UnsignedMappingConflictTestBase as MappingConflictTestBase
from .common import ModuleTest
from .common import MultiUnion
from .common import UnsignedNormalSetTests as NormalSetTests
from .common import UnsignedSetConflictTestBase as SetConflictTestBase
from .common import SetResult
from .common import TestLongIntKeys
from .common import TestLongIntValues
from .common import Weighted
from .common import itemsToSet
from .common import makeBuilder
from .common import UnsignedMixin
from .common import UnsignedError
from BTrees.UUBTree import using64bits #XXX Ugly, but unavoidable


class UUBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UUBTree import UUBTree
        return UUBTree


class UUBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UUBTree import UUBTreePy
        return UUBTreePy


class UUTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UUBTree import UUTreeSet
        return UUTreeSet


class UUTreeSetPyInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UUBTree import UUTreeSetPy
        return UUTreeSetPy


class UUBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UUBTree import UUBucket
        return UUBucket


class UUBucketPyTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UUBTree import UUBucketPy
        return UUBucketPy


class UUTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UUBTree import UUTreeSet
        return UUTreeSet


class UUTreeSetPyTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UUBTree import UUTreeSetPy
        return UUTreeSetPy


class UUSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UUBTree import UUSet
        return UUSet


class UUSetPyTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UUBTree import UUSetPy
        return UUSetPy


class _UUBTreeTestBase(BTreeTests):

    def testUUBTreeOverflow(self):
        good = set()
        b = self._makeOne()

        def trial(i):
            i = int(i)
            try:
                b[i] = 0
            except UnsignedError:
                with self.assertRaises(UnsignedError):
                    b[0] = i
            else:
                good.add(i)
                b[0] = i
                self.assertEqual(b[0], i)

        for i in range((1<<31) - 3, (1<<31) + 3):
            __traceback_info__ = i
            trial(i)
            trial(-i)

        del b[0]
        self.assertEqual(sorted(good), sorted(b))


class UUBTreeTest(_UUBTreeTestBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UUBTree import UUBTree
        return UUBTree()


class UUBTreeTestPy(_UUBTreeTestBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UUBTree import UUBTreePy
        return UUBTreePy()


if using64bits:

    class UUBTreeTest(BTreeTests, TestLongIntKeys, TestLongIntValues,
                      unittest.TestCase):

        def _makeOne(self):
            from BTrees.UUBTree import UUBTree
            return UUBTree()

        def getTwoValues(self):
            return 1, 2

    class UUBTreeTestPy(BTreeTests, TestLongIntKeys, TestLongIntValues,
                        unittest.TestCase):

        def _makeOne(self):
            from BTrees.UUBTree import UUBTreePy
            return UUBTreePy()

        def getTwoValues(self):
            return 1, 2


class _TestUUBTreesBase(object):

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


class TestUUBTrees(_TestUUBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UUBTree import UUBTree
        return UUBTree()


class TestUUBTreesPy(_TestUUBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UUBTree import UUBTreePy
        return UUBTreePy()


class TestUUSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UUBTree import UUSet
        return UUSet()


class TestUUSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UUBTree import UUSetPy
        return UUSetPy()


class TestUUTreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UUBTree import UUTreeSet
        return UUTreeSet()


class TestUUTreeSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UUBTree import UUTreeSetPy
        return UUTreeSetPy()


class PureUU(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.UUBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.UUBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.UUBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.UUBTree import UUBTree
        from BTrees.UUBTree import UUBucket
        from BTrees.UUBTree import UUTreeSet
        from BTrees.UUBTree import UUSet
        return UUSet, UUTreeSet, makeBuilder(UUBTree), makeBuilder(UUBucket)


class PureUUPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.UUBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.UUBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.UUBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.UUBTree import UUBTreePy
        from BTrees.UUBTree import UUBucketPy
        from BTrees.UUBTree import UUTreeSetPy
        from BTrees.UUBTree import UUSetPy
        return (UUSetPy, UUTreeSetPy,
                makeBuilder(UUBTreePy), makeBuilder(UUBucketPy))


class TestUUMultiUnion(UnsignedMixin, MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.UUBTree import multiunion
        return multiunion(*args)

    def union(self, *args):
        from BTrees.UUBTree import union
        return union(*args)

    def mkset(self, *args):
        from BTrees.UUBTree import UUSet as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.UUBTree import UUTreeSet as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.UUBTree import UUBucket as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.UUBTree import UUBTree as mkbtree
        return mkbtree(*args)


class TestUUMultiUnionPy(UnsignedMixin, MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.UUBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.UUBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.UUBTree import UUSetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.UUBTree import UUTreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.UUBTree import UUBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.UUBTree import UUBTreePy as mkbtree
        return mkbtree(*args)


class TestWeightedUU(UnsignedMixin, Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.UUBTree import weightedUnion
        return weightedUnion

    def weightedIntersection(self):
        from BTrees.UUBTree import weightedIntersection
        return weightedIntersection

    def union(self):
        from BTrees.UUBTree import union
        return union

    def intersection(self):
        from BTrees.UUBTree import intersection
        return intersection

    def mkbucket(self, *args):
        from BTrees.UUBTree import UUBucket as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.UUBTree import UUBTree
        from BTrees.UUBTree import UUBucket
        from BTrees.UUBTree import UUTreeSet
        from BTrees.UUBTree import UUSet
        return UUBucket, UUBTree, itemsToSet(UUSet), itemsToSet(UUTreeSet)


class TestWeightedUUPy(UnsignedMixin, Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.UUBTree import weightedUnionPy
        return weightedUnionPy

    def weightedIntersection(self):
        from BTrees.UUBTree import weightedIntersectionPy
        return weightedIntersectionPy

    def union(self):
        from BTrees.UUBTree import unionPy
        return unionPy

    def intersection(self):
        from BTrees.UUBTree import intersectionPy
        return intersectionPy

    def mkbucket(self, *args):
        from BTrees.UUBTree import UUBucketPy as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.UUBTree import UUBTreePy
        from BTrees.UUBTree import UUBucketPy
        from BTrees.UUBTree import UUTreeSetPy
        from BTrees.UUBTree import UUSetPy
        return (UUBucketPy, UUBTreePy,
                itemsToSet(UUSetPy), itemsToSet(UUTreeSetPy))


class UUBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UUBTree import UUBTree
        return UUBTree


class UUBTreeConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UUBTree import UUBTreePy
        return UUBTreePy


class UUBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UUBTree import UUBucket
        return UUBucket


class UUBucketConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UUBTree import UUBucketPy
        return UUBucketPy


class UUTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UUBTree import UUTreeSet
        return UUTreeSet


class UUTreeSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UUBTree import UUTreeSetPy
        return UUTreeSetPy


class UUSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UUBTree import UUSet
        return UUSet


class UUSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UUBTree import UUSetPy
        return UUSetPy


class UUModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'UU'

    def _getModule(self):
        import BTrees
        return BTrees.UUBTree
    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IUnsignedUnsignedBTreeModule



def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(UUBTreeInternalKeyTest),
        unittest.makeSuite(UUBTreePyInternalKeyTest),
        unittest.makeSuite(UUTreeSetInternalKeyTest),
        unittest.makeSuite(UUTreeSetPyInternalKeyTest),
        unittest.makeSuite(UUBucketTest),
        unittest.makeSuite(UUBucketPyTest),
        unittest.makeSuite(UUTreeSetTest),
        unittest.makeSuite(UUTreeSetPyTest),
        unittest.makeSuite(UUSetTest),
        unittest.makeSuite(UUSetPyTest),
        unittest.makeSuite(UUBTreeTest),
        unittest.makeSuite(UUBTreeTestPy),
        unittest.makeSuite(TestUUBTrees),
        unittest.makeSuite(TestUUBTreesPy),
        unittest.makeSuite(TestUUSets),
        unittest.makeSuite(TestUUSetsPy),
        unittest.makeSuite(TestUUTreeSets),
        unittest.makeSuite(TestUUTreeSetsPy),
        unittest.makeSuite(TestUUMultiUnion),
        unittest.makeSuite(TestUUMultiUnionPy),
        unittest.makeSuite(PureUU),
        unittest.makeSuite(PureUUPy),
        unittest.makeSuite(TestWeightedUU),
        unittest.makeSuite(TestWeightedUUPy),
        unittest.makeSuite(UUBTreeConflictTests),
        unittest.makeSuite(UUBTreeConflictTestsPy),
        unittest.makeSuite(UUBucketConflictTests),
        unittest.makeSuite(UUBucketConflictTestsPy),
        unittest.makeSuite(UUTreeSetConflictTests),
        unittest.makeSuite(UUTreeSetConflictTestsPy),
        unittest.makeSuite(UUSetConflictTests),
        unittest.makeSuite(UUSetConflictTestsPy),
        unittest.makeSuite(UUModuleTest),
    ))
