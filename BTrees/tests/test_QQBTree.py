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


# pylint:disable=no-name-in-module,arguments-differ

class QQBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QQBTree import QQBTree
        return QQBTree


class QQBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QQBTree import QQBTreePy
        return QQBTreePy


class QQTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QQBTree import QQTreeSet
        return QQTreeSet


class QQTreeSetPyInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QQBTree import QQTreeSetPy
        return QQTreeSetPy


class QQBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QQBTree import QQBucket
        return QQBucket


class QQBucketTestPy(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QQBTree import QQBucketPy
        return QQBucketPy


class QQTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QQBTree import QQTreeSet
        return QQTreeSet


class QQTreeSetTestPy(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QQBTree import QQTreeSetPy
        return QQTreeSetPy


class QQSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QQBTree import QQSet
        return QQSet


class QQSetTestPy(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QQBTree import QQSetPy
        return QQSetPy


class QQBTreeTest(BTreeTests, TestLongIntKeys, TestLongIntValues,
                  unittest.TestCase):

    def _makeOne(self):
        from BTrees.QQBTree import QQBTree
        return QQBTree()
    def getTwoValues(self):
        return 1, 2


class QQBTreeTestPy(BTreeTests, TestLongIntKeys, TestLongIntValues,
                    unittest.TestCase):

    def _makeOne(self):
        from BTrees.QQBTree import QQBTreePy
        return QQBTreePy()
    def getTwoValues(self):
        return 1, 2


class TestQQSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.QQBTree import QQSet
        return QQSet()


class TestQQSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.QQBTree import QQSetPy
        return QQSetPy()


class TestQQTreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.QQBTree import QQTreeSet
        return QQTreeSet()


class TestQQTreeSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.QQBTree import QQTreeSetPy
        return QQTreeSetPy()


class PureQQ(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.QQBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.QQBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.QQBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.QQBTree import QQBTree
        from BTrees.QQBTree import QQBucket
        from BTrees.QQBTree import QQTreeSet
        from BTrees.QQBTree import QQSet
        return QQSet, QQTreeSet, makeBuilder(QQBTree), makeBuilder(QQBucket)


class PureQQPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.QQBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.QQBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.QQBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.QQBTree import QQBTreePy
        from BTrees.QQBTree import QQBucketPy
        from BTrees.QQBTree import QQTreeSetPy
        from BTrees.QQBTree import QQSetPy
        return (QQSetPy, QQTreeSetPy,
                makeBuilder(QQBTreePy), makeBuilder(QQBucketPy))


class TestQQMultiUnion(UnsignedMixin, MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.QQBTree import multiunion
        return multiunion(*args)

    def union(self, *args):
        from BTrees.QQBTree import union
        return union(*args)

    def mkset(self, *args):
        from BTrees.QQBTree import QQSet as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.QQBTree import QQTreeSet as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.QQBTree import QQBucket as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.QQBTree import QQBTree as mkbtree
        return mkbtree(*args)


class TestQQMultiUnionPy(UnsignedMixin, MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.QQBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.QQBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.QQBTree import QQSetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.QQBTree import QQTreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.QQBTree import QQBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.QQBTree import QQBTreePy as mkbtree
        return mkbtree(*args)


class TestWeightedQQ(UnsignedMixin, Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.QQBTree import weightedUnion
        return weightedUnion

    def weightedIntersection(self):
        from BTrees.QQBTree import weightedIntersection
        return weightedIntersection

    def union(self):
        from BTrees.QQBTree import union
        return union

    def intersection(self):
        from BTrees.QQBTree import intersection
        return intersection

    def mkbucket(self, *args):
        from BTrees.QQBTree import QQBucket as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.QQBTree import QQBTree
        from BTrees.QQBTree import QQBucket
        from BTrees.QQBTree import QQTreeSet
        from BTrees.QQBTree import QQSet
        return QQBucket, QQBTree, itemsToSet(QQSet), itemsToSet(QQTreeSet)


class TestWeightedQQPy(UnsignedMixin, Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.QQBTree import weightedUnionPy
        return weightedUnionPy

    def weightedIntersection(self):
        from BTrees.QQBTree import weightedIntersectionPy
        return weightedIntersectionPy

    def union(self):
        from BTrees.QQBTree import unionPy
        return unionPy

    def intersection(self):
        from BTrees.QQBTree import intersectionPy
        return intersectionPy

    def mkbucket(self, *args):
        from BTrees.QQBTree import QQBucketPy as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.QQBTree import QQBTreePy
        from BTrees.QQBTree import QQBucketPy
        from BTrees.QQBTree import QQTreeSetPy
        from BTrees.QQBTree import QQSetPy
        return (QQBucketPy, QQBTreePy,
                itemsToSet(QQSetPy), itemsToSet(QQTreeSetPy))


class QQBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QQBTree import QQBTree
        return QQBTree


class QQBTreeConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QQBTree import QQBTreePy
        return QQBTreePy


class QQBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QQBTree import QQBucket
        return QQBucket


class QQBucketConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QQBTree import QQBucketPy
        return QQBucketPy


class QQTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QQBTree import QQTreeSet
        return QQTreeSet


class QQTreeSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QQBTree import QQTreeSetPy
        return QQTreeSetPy


class QQSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QQBTree import QQSet
        return QQSet


class QQSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QQBTree import QQSetPy
        return QQSetPy


class QQModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'QQ'

    def _getModule(self):
        import BTrees
        return BTrees.QQBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IUnsignedUnsignedBTreeModule


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(QQBTreeInternalKeyTest),
        unittest.makeSuite(QQBTreeInternalKeyTest),
        unittest.makeSuite(QQTreeSetInternalKeyTest),
        unittest.makeSuite(QQTreeSetInternalKeyTest),
        unittest.makeSuite(QQBucketTest),
        unittest.makeSuite(QQBucketTest),
        unittest.makeSuite(QQTreeSetTest),
        unittest.makeSuite(QQTreeSetTest),
        unittest.makeSuite(QQSetTest),
        unittest.makeSuite(QQSetTest),
        unittest.makeSuite(QQBTreeTest),
        unittest.makeSuite(QQBTreeTest),
        unittest.makeSuite(TestQQSets),
        unittest.makeSuite(TestQQSets),
        unittest.makeSuite(TestQQTreeSets),
        unittest.makeSuite(TestQQTreeSets),
        unittest.makeSuite(TestQQMultiUnion),
        unittest.makeSuite(TestQQMultiUnion),
        unittest.makeSuite(PureQQ),
        unittest.makeSuite(PureQQ),
        unittest.makeSuite(TestWeightedQQ),
        unittest.makeSuite(TestWeightedQQPy),
        unittest.makeSuite(QQBTreeConflictTests),
        unittest.makeSuite(QQBTreeConflictTests),
        unittest.makeSuite(QQBucketConflictTests),
        unittest.makeSuite(QQBucketConflictTests),
        unittest.makeSuite(QQTreeSetConflictTests),
        unittest.makeSuite(QQTreeSetConflictTests),
        unittest.makeSuite(QQSetConflictTests),
        unittest.makeSuite(QQSetConflictTests),
        unittest.makeSuite(QQModuleTest),
    ))
