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

from .common import I_SetsBase
from .common import TestLongIntValues
from .common import Weighted
from .common import itemsToSet

from .common import UnsignedKeysBTreeTests as BTreeTests
from .common import UnsignedExtendedSetTests as ExtendedSetTests
from .common import InternalKeysMappingTest
from .common import InternalKeysSetTest
from .common import UnsignedKeysMappingBase as MappingBase
from .common import UnsignedKeysMappingConflictTestBase as MappingConflictTestBase
from .common import ModuleTest
from .common import MultiUnion
from .common import UnsignedNormalSetTests as NormalSetTests
from .common import UnsignedSetConflictTestBase as SetConflictTestBase
from .common import SetResult
from .common import TestLongIntKeys
from .common import makeBuilder
from .common import UnsignedKeysMixin

# pylint: disable=no-name-in-module,arguments-differ

class QLBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QLBTree import QLBTree
        return QLBTree


class QLBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QLBTree import QLBTreePy
        return QLBTreePy


class QLTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QLBTree import QLTreeSet
        return QLTreeSet


class QLTreeSetPyInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QLBTree import QLTreeSetPy
        return QLTreeSetPy


class QLBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QLBTree import QLBucket
        return QLBucket


class QLBucketTestPy(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QLBTree import QLBucketPy
        return QLBucketPy


class QLTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QLBTree import QLTreeSet
        return QLTreeSet


class QLTreeSetTestPy(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QLBTree import QLTreeSetPy
        return QLTreeSetPy


class QLSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QLBTree import QLSet
        return QLSet


class QLSetTestPy(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QLBTree import QLSetPy
        return QLSetPy


class QLBTreeTest(BTreeTests, TestLongIntKeys, TestLongIntValues,
                  unittest.TestCase):

    def _makeOne(self):
        from BTrees.QLBTree import QLBTree
        return QLBTree()
    def getTwoValues(self):
        return 1, 2


class QLBTreeTestPy(BTreeTests, TestLongIntKeys, TestLongIntValues,
                    unittest.TestCase):

    def _makeOne(self):
        from BTrees.QLBTree import QLBTreePy
        return QLBTreePy()
    def getTwoValues(self):
        return 1, 2


class TestQLSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.QLBTree import QLSet
        return QLSet()


class TestQLSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.QLBTree import QLSetPy
        return QLSetPy()


class TestQLTreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.QLBTree import QLTreeSet
        return QLTreeSet()


class TestQLTreeSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.QLBTree import QLTreeSetPy
        return QLTreeSetPy()


class PureQL(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.QLBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.QLBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.QLBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.QLBTree import QLBTree
        from BTrees.QLBTree import QLBucket
        from BTrees.QLBTree import QLTreeSet
        from BTrees.QLBTree import QLSet
        return QLSet, QLTreeSet, makeBuilder(QLBTree), makeBuilder(QLBucket)


class PureQLPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.QLBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.QLBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.QLBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.QLBTree import QLBTreePy
        from BTrees.QLBTree import QLBucketPy
        from BTrees.QLBTree import QLTreeSetPy
        from BTrees.QLBTree import QLSetPy
        return (QLSetPy, QLTreeSetPy,
                makeBuilder(QLBTreePy), makeBuilder(QLBucketPy))


class TestQLMultiUnion(UnsignedKeysMixin, MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.QLBTree import multiunion
        return multiunion(*args)

    def union(self, *args):
        from BTrees.QLBTree import union
        return union(*args)

    def mkset(self, *args):
        from BTrees.QLBTree import QLSet as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.QLBTree import QLTreeSet as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.QLBTree import QLBucket as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.QLBTree import QLBTree as mkbtree
        return mkbtree(*args)


class TestQLMultiUnionPy(UnsignedKeysMixin, MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.QLBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.QLBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.QLBTree import QLSetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.QLBTree import QLTreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.QLBTree import QLBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.QLBTree import QLBTreePy as mkbtree
        return mkbtree(*args)


class TestWeightedQL(UnsignedKeysMixin, Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.QLBTree import weightedUnion
        return weightedUnion

    def weightedIntersection(self):
        from BTrees.QLBTree import weightedIntersection
        return weightedIntersection

    def union(self):
        from BTrees.QLBTree import union
        return union

    def intersection(self):
        from BTrees.QLBTree import intersection
        return intersection

    def mkbucket(self, *args):
        from BTrees.QLBTree import QLBucket as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.QLBTree import QLBTree
        from BTrees.QLBTree import QLBucket
        from BTrees.QLBTree import QLTreeSet
        from BTrees.QLBTree import QLSet
        return QLBucket, QLBTree, itemsToSet(QLSet), itemsToSet(QLTreeSet)


class TestWeightedQLPy(UnsignedKeysMixin, Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.QLBTree import weightedUnionPy
        return weightedUnionPy

    def weightedIntersection(self):
        from BTrees.QLBTree import weightedIntersectionPy
        return weightedIntersectionPy

    def union(self):
        from BTrees.QLBTree import unionPy
        return unionPy

    def intersection(self):
        from BTrees.QLBTree import intersectionPy
        return intersectionPy

    def mkbucket(self, *args):
        from BTrees.QLBTree import QLBucketPy as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.QLBTree import QLBTreePy
        from BTrees.QLBTree import QLBucketPy
        from BTrees.QLBTree import QLTreeSetPy
        from BTrees.QLBTree import QLSetPy
        return (QLBucketPy, QLBTreePy,
                itemsToSet(QLSetPy), itemsToSet(QLTreeSetPy))


class QLBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QLBTree import QLBTree
        return QLBTree


class QLBTreeConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QLBTree import QLBTreePy
        return QLBTreePy


class QLBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QLBTree import QLBucket
        return QLBucket


class QLBucketConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QLBTree import QLBucketPy
        return QLBucketPy


class QLTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QLBTree import QLTreeSet
        return QLTreeSet


class QLTreeSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QLBTree import QLTreeSetPy
        return QLTreeSetPy


class QLSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QLBTree import QLSet
        return QLSet


class QLSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QLBTree import QLSetPy
        return QLSetPy


class QLModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'QL'

    def _getModule(self):
        import BTrees
        return BTrees.QLBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IUnsignedIntegerBTreeModule


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(QLBTreeInternalKeyTest),
        unittest.makeSuite(QLBTreeInternalKeyTest),
        unittest.makeSuite(QLTreeSetInternalKeyTest),
        unittest.makeSuite(QLTreeSetInternalKeyTest),
        unittest.makeSuite(QLBucketTest),
        unittest.makeSuite(QLBucketTest),
        unittest.makeSuite(QLTreeSetTest),
        unittest.makeSuite(QLTreeSetTest),
        unittest.makeSuite(QLSetTest),
        unittest.makeSuite(QLSetTest),
        unittest.makeSuite(QLBTreeTest),
        unittest.makeSuite(QLBTreeTest),
        unittest.makeSuite(TestQLSets),
        unittest.makeSuite(TestQLSets),
        unittest.makeSuite(TestQLTreeSets),
        unittest.makeSuite(TestQLTreeSets),
        unittest.makeSuite(TestQLMultiUnion),
        unittest.makeSuite(TestQLMultiUnion),
        unittest.makeSuite(PureQL),
        unittest.makeSuite(PureQL),
        unittest.makeSuite(TestWeightedQL),
        unittest.makeSuite(TestWeightedQL),
        unittest.makeSuite(QLBTreeConflictTests),
        unittest.makeSuite(QLBTreeConflictTests),
        unittest.makeSuite(QLBucketConflictTests),
        unittest.makeSuite(QLBucketConflictTests),
        unittest.makeSuite(QLTreeSetConflictTests),
        unittest.makeSuite(QLTreeSetConflictTests),
        unittest.makeSuite(QLSetConflictTests),
        unittest.makeSuite(QLSetConflictTests),
        unittest.makeSuite(QLModuleTest),
    ))
