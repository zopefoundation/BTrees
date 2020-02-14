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

from .common import UnsignedValuesBTreeTests as BTreeTests
from .common import ExtendedSetTests
from .common import I_SetsBase
from .common import InternalKeysMappingTest
from .common import InternalKeysSetTest
from .common import UnsignedValuesMappingBase as MappingBase
from .common import UnsignedValuesMappingConflictTestBase as MappingConflictTestBase
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
from .common import UnsignedValuesMixin

# pylint:disable=no-name-in-module,arguments-differ

class LQBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LQBTree import LQBTree
        return LQBTree


class LQBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LQBTree import LQBTreePy
        return LQBTreePy


class LQTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LQBTree import LQTreeSet
        return LQTreeSet


class LQTreeSetPyInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LQBTree import LQTreeSetPy
        return LQTreeSetPy


class LQBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LQBTree import LQBucket
        return LQBucket


class LQBucketTestPy(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LQBTree import LQBucketPy
        return LQBucketPy


class LQTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LQBTree import LQTreeSet
        return LQTreeSet


class LQTreeSetTestPy(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LQBTree import LQTreeSetPy
        return LQTreeSetPy


class LQSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LQBTree import LQSet
        return LQSet


class LQSetTestPy(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LQBTree import LQSetPy
        return LQSetPy


class LQBTreeTest(BTreeTests, TestLongIntKeys, TestLongIntValues,
                  unittest.TestCase):

    def _makeOne(self):
        from BTrees.LQBTree import LQBTree
        return LQBTree()
    def getTwoValues(self):
        return 1, 2


class LQBTreeTestPy(BTreeTests, TestLongIntKeys, TestLongIntValues,
                    unittest.TestCase):

    def _makeOne(self):
        from BTrees.LQBTree import LQBTreePy
        return LQBTreePy()
    def getTwoValues(self):
        return 1, 2


class TestLQSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LQBTree import LQSet
        return LQSet()


class TestLQSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LQBTree import LQSetPy
        return LQSetPy()


class TestLQTreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LQBTree import LQTreeSet
        return LQTreeSet()


class TestLQTreeSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LQBTree import LQTreeSetPy
        return LQTreeSetPy()


class PureLQ(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.LQBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.LQBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.LQBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.LQBTree import LQBTree
        from BTrees.LQBTree import LQBucket
        from BTrees.LQBTree import LQTreeSet
        from BTrees.LQBTree import LQSet
        return LQSet, LQTreeSet, makeBuilder(LQBTree), makeBuilder(LQBucket)


class PureLQPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.LQBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.LQBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.LQBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.LQBTree import LQBTreePy
        from BTrees.LQBTree import LQBucketPy
        from BTrees.LQBTree import LQTreeSetPy
        from BTrees.LQBTree import LQSetPy
        return (LQSetPy, LQTreeSetPy,
                makeBuilder(LQBTreePy), makeBuilder(LQBucketPy))


class TestLQMultiUnion(MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.LQBTree import multiunion
        return multiunion(*args)

    def union(self, *args):
        from BTrees.LQBTree import union
        return union(*args)

    def mkset(self, *args):
        from BTrees.LQBTree import LQSet as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.LQBTree import LQTreeSet as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.LQBTree import LQBucket as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.LQBTree import LQBTree as mkbtree
        return mkbtree(*args)


class TestLQMultiUnionPy(MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.LQBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.LQBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.LQBTree import LQSetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.LQBTree import LQTreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.LQBTree import LQBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.LQBTree import LQBTreePy as mkbtree
        return mkbtree(*args)


class TestWeightedLQ(UnsignedValuesMixin, Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.LQBTree import weightedUnion
        return weightedUnion

    def weightedIntersection(self):
        from BTrees.LQBTree import weightedIntersection
        return weightedIntersection

    def union(self):
        from BTrees.LQBTree import union
        return union

    def intersection(self):
        from BTrees.LQBTree import intersection
        return intersection

    def mkbucket(self, *args):
        from BTrees.LQBTree import LQBucket as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.LQBTree import LQBTree
        from BTrees.LQBTree import LQBucket
        from BTrees.LQBTree import LQTreeSet
        from BTrees.LQBTree import LQSet
        return LQBucket, LQBTree, itemsToSet(LQSet), itemsToSet(LQTreeSet)


class TestWeightedLQPy(UnsignedValuesMixin, Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.LQBTree import weightedUnionPy
        return weightedUnionPy

    def weightedIntersection(self):
        from BTrees.LQBTree import weightedIntersectionPy
        return weightedIntersectionPy

    def union(self):
        from BTrees.LQBTree import unionPy
        return unionPy

    def intersection(self):
        from BTrees.LQBTree import intersectionPy
        return intersectionPy

    def mkbucket(self, *args):
        from BTrees.LQBTree import LQBucketPy as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.LQBTree import LQBTreePy
        from BTrees.LQBTree import LQBucketPy
        from BTrees.LQBTree import LQTreeSetPy
        from BTrees.LQBTree import LQSetPy
        return (LQBucketPy, LQBTreePy,
                itemsToSet(LQSetPy), itemsToSet(LQTreeSetPy))


class LQBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LQBTree import LQBTree
        return LQBTree


class LQBTreeConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LQBTree import LQBTreePy
        return LQBTreePy


class LQBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LQBTree import LQBucket
        return LQBucket


class LQBucketConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LQBTree import LQBucketPy
        return LQBucketPy


class LQTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LQBTree import LQTreeSet
        return LQTreeSet


class LQTreeSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LQBTree import LQTreeSetPy
        return LQTreeSetPy


class LQSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LQBTree import LQSet
        return LQSet


class LQSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LQBTree import LQSetPy
        return LQSetPy


class LQModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'LQ'

    def _getModule(self):
        import BTrees
        return BTrees.LQBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IIntegerUnsignedBTreeModule


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(LQBTreeInternalKeyTest),
        unittest.makeSuite(LQBTreeInternalKeyTest),
        unittest.makeSuite(LQTreeSetInternalKeyTest),
        unittest.makeSuite(LQTreeSetInternalKeyTest),
        unittest.makeSuite(LQBucketTest),
        unittest.makeSuite(LQBucketTest),
        unittest.makeSuite(LQTreeSetTest),
        unittest.makeSuite(LQTreeSetTest),
        unittest.makeSuite(LQSetTest),
        unittest.makeSuite(LQSetTest),
        unittest.makeSuite(LQBTreeTest),
        unittest.makeSuite(LQBTreeTest),
        unittest.makeSuite(TestLQSets),
        unittest.makeSuite(TestLQSets),
        unittest.makeSuite(TestLQTreeSets),
        unittest.makeSuite(TestLQTreeSets),
        unittest.makeSuite(TestLQMultiUnion),
        unittest.makeSuite(TestLQMultiUnion),
        unittest.makeSuite(PureLQ),
        unittest.makeSuite(PureLQ),
        unittest.makeSuite(TestWeightedLQ),
        unittest.makeSuite(TestWeightedLQ),
        unittest.makeSuite(LQBTreeConflictTests),
        unittest.makeSuite(LQBTreeConflictTests),
        unittest.makeSuite(LQBucketConflictTests),
        unittest.makeSuite(LQBucketConflictTests),
        unittest.makeSuite(LQTreeSetConflictTests),
        unittest.makeSuite(LQTreeSetConflictTests),
        unittest.makeSuite(LQSetConflictTests),
        unittest.makeSuite(LQSetConflictTests),
        unittest.makeSuite(LQModuleTest),
    ))
