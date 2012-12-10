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


class LLBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLBTree
        return LLBTree


class LLBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLBTreePy
        return LLBTreePy


class LLTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLTreeSet
        return LLTreeSet


class LLTreeSetPyInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLTreeSetPy
        return LLTreeSetPy


class LLBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLBucket
        return LLBucket


class LLBucketTestPy(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLBucketPy
        return LLBucketPy


class LLTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLTreeSet
        return LLTreeSet


class LLTreeSetTestPy(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLTreeSetPy
        return LLTreeSetPy


class LLSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLSet
        return LLSet


class LLSetTestPy(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLSetPy
        return LLSetPy


class LLBTreeTest(BTreeTests, TestLongIntKeys, TestLongIntValues,
                  unittest.TestCase):

    def _makeOne(self):
        from BTrees.LLBTree import LLBTree
        return LLBTree()
    def getTwoValues(self):
        return 1, 2


class LLBTreeTestPy(BTreeTests, TestLongIntKeys, TestLongIntValues,
                  unittest.TestCase):

    def _makeOne(self):
        from BTrees.LLBTree import LLBTreePy
        return LLBTreePy()
    def getTwoValues(self):
        return 1, 2


class TestLLSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LLBTree import LLSet
        return LLSet()


class TestLLSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LLBTree import LLSetPy
        return LLSetPy()


class TestLLTreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LLBTree import LLTreeSet
        return LLTreeSet()


class TestLLTreeSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LLBTree import LLTreeSetPy
        return LLTreeSetPy()


class PureLL(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.LLBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.LLBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.LLBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.LLBTree import LLBTree
        from BTrees.LLBTree import LLBucket
        from BTrees.LLBTree import LLTreeSet
        from BTrees.LLBTree import LLSet
        return LLSet, LLTreeSet, makeBuilder(LLBTree), makeBuilder(LLBucket)


class PureLLPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.LLBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.LLBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.LLBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.LLBTree import LLBTreePy
        from BTrees.LLBTree import LLBucketPy
        from BTrees.LLBTree import LLTreeSetPy
        from BTrees.LLBTree import LLSetPy
        return (LLSetPy, LLTreeSetPy,
                makeBuilder(LLBTreePy), makeBuilder(LLBucketPy))


class TestLLMultiUnion(MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.LLBTree import multiunion
        return multiunion(*args)

    def union(self, *args):
        from BTrees.LLBTree import union
        return union(*args)

    def mkset(self, *args):
        from BTrees.LLBTree import LLSet as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.LLBTree import LLTreeSet as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.LLBTree import LLBucket as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.LLBTree import LLBTree as mkbtree
        return mkbtree(*args)


class TestLLMultiUnionPy(MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.LLBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.LLBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.LLBTree import LLSetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.LLBTree import LLTreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.LLBTree import LLBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.LLBTree import LLBTreePy as mkbtree
        return mkbtree(*args)


class TestWeightedLL(Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.LLBTree import weightedUnion
        return weightedUnion

    def weightedIntersection(self):
        from BTrees.LLBTree import weightedIntersection
        return weightedIntersection

    def union(self):
        from BTrees.LLBTree import union
        return union

    def intersection(self):
        from BTrees.LLBTree import intersection
        return intersection

    def mkbucket(self, *args):
        from BTrees.LLBTree import LLBucket as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.LLBTree import LLBTree
        from BTrees.LLBTree import LLBucket
        from BTrees.LLBTree import LLTreeSet
        from BTrees.LLBTree import LLSet
        return LLBucket, LLBTree, itemsToSet(LLSet), itemsToSet(LLTreeSet)


class TestWeightedLLPy(Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.LLBTree import weightedUnionPy
        return weightedUnionPy

    def weightedIntersection(self):
        from BTrees.LLBTree import weightedIntersectionPy
        return weightedIntersectionPy

    def union(self):
        from BTrees.LLBTree import unionPy
        return unionPy

    def intersection(self):
        from BTrees.LLBTree import intersectionPy
        return intersectionPy

    def mkbucket(self, *args):
        from BTrees.LLBTree import LLBucketPy as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.LLBTree import LLBTreePy
        from BTrees.LLBTree import LLBucketPy
        from BTrees.LLBTree import LLTreeSetPy
        from BTrees.LLBTree import LLSetPy
        return (LLBucketPy, LLBTreePy,
                itemsToSet(LLSetPy), itemsToSet(LLTreeSetPy))


class LLBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLBTree
        return LLBTree


class LLBTreeConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLBTreePy
        return LLBTreePy


class LLBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLBucket
        return LLBucket


class LLBucketConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLBucketPy
        return LLBucketPy


class LLTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLTreeSet
        return LLTreeSet


class LLTreeSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLTreeSetPy
        return LLTreeSetPy


class LLSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLSet
        return LLSet


class LLSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLSetPy
        return LLSetPy


class LLModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'LL'

    def _getModule(self):
        import BTrees
        return BTrees.LLBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IIntegerIntegerBTreeModule


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(LLBTreeInternalKeyTest),
        unittest.makeSuite(LLBTreeInternalKeyTest),
        unittest.makeSuite(LLTreeSetInternalKeyTest),
        unittest.makeSuite(LLTreeSetInternalKeyTest),
        unittest.makeSuite(LLBucketTest),
        unittest.makeSuite(LLBucketTest),
        unittest.makeSuite(LLTreeSetTest),
        unittest.makeSuite(LLTreeSetTest),
        unittest.makeSuite(LLSetTest),
        unittest.makeSuite(LLSetTest),
        unittest.makeSuite(LLBTreeTest),
        unittest.makeSuite(LLBTreeTest),
        unittest.makeSuite(TestLLSets),
        unittest.makeSuite(TestLLSets),
        unittest.makeSuite(TestLLTreeSets),
        unittest.makeSuite(TestLLTreeSets),
        unittest.makeSuite(TestLLMultiUnion),
        unittest.makeSuite(TestLLMultiUnion),
        unittest.makeSuite(PureLL),
        unittest.makeSuite(PureLL),
        unittest.makeSuite(TestWeightedLL),
        unittest.makeSuite(TestWeightedLL),
        unittest.makeSuite(LLBTreeConflictTests),
        unittest.makeSuite(LLBTreeConflictTests),
        unittest.makeSuite(LLBucketConflictTests),
        unittest.makeSuite(LLBucketConflictTests),
        unittest.makeSuite(LLTreeSetConflictTests),
        unittest.makeSuite(LLTreeSetConflictTests),
        unittest.makeSuite(LLSetConflictTests),
        unittest.makeSuite(LLSetConflictTests),
        unittest.makeSuite(LLModuleTest),
    ))
