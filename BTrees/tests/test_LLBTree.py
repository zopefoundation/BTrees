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


class LLTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLTreeSet
        return LLTreeSet


class LLBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLBucket
        return LLBucket


class LLTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLTreeSet
        return LLTreeSet


class LLSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLSet
        return LLSet


class LLSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLSet
        return LLSet


class LLBTreeTest(BTreeTests, TestLongIntKeys, TestLongIntValues,
                  unittest.TestCase):

    def _makeOne(self):
        from BTrees.LLBTree import LLBTree
        return LLBTree()
    def getTwoValues(self):
        return 1, 2


class TestLLSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LLBTree import LLSet
        return LLSet()


class TestLLTreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LLBTree import LLTreeSet
        return LLTreeSet()


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


class LLBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLBTree
        return LLBTree


class LLBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLBucket
        return LLBucket


class LLTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLTreeSet
        return LLTreeSet


class LLSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLSet
        return LLSet


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
        unittest.makeSuite(LLTreeSetInternalKeyTest),
        unittest.makeSuite(LLBucketTest),
        unittest.makeSuite(LLTreeSetTest),
        unittest.makeSuite(LLSetTest),
        unittest.makeSuite(LLModuleTest),
        unittest.makeSuite(LLBTreeTest),
        unittest.makeSuite(TestLLSets),
        unittest.makeSuite(TestLLTreeSets),
        unittest.makeSuite(TestLLMultiUnion),
        unittest.makeSuite(PureLL),
        unittest.makeSuite(TestWeightedLL),
        unittest.makeSuite(LLBTreeConflictTests),
        unittest.makeSuite(LLBucketConflictTests),
        unittest.makeSuite(LLTreeSetConflictTests),
        unittest.makeSuite(LLSetConflictTests),
    ))
