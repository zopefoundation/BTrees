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
from .common import InternalKeysMappingTest
from .common import InternalKeysSetTest
from .common import MappingBase
from .common import MappingConflictTestBase
from .common import ModuleTest
from .common import NormalSetTests
from .common import SetConflictTestBase
from .common import SetResult
from .common import TestLongIntValues
from .common import Weighted
from .common import itemsToSet
from .common import makeBuilder


class OLBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLBTree
        return OLBTree


class OLTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLTreeSet
        return OLTreeSet


class OLBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLBucket
        return OLBucket


class OLTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLTreeSet
        return OLTreeSet


class OLSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLSet
        return OLSet


class OLBTreeTest(BTreeTests, TestLongIntValues, unittest.TestCase):

    def _makeOne(self):
        from BTrees.OLBTree import OLBTree
        return OLBTree()

    def getTwoKeys(self):
        return object(), object()


class PureOL(SetResult, unittest.TestCase):
    def union(self, *args):
        from BTrees.OLBTree import union
        return union(*args)
    def intersection(self, *args):
        from BTrees.OLBTree import intersection
        return intersection(*args)
    def difference(self, *args):
        from BTrees.OLBTree import difference
        return difference(*args)
    def builders(self):
        from BTrees.OLBTree import OLBTree
        from BTrees.OLBTree import OLBucket
        from BTrees.OLBTree import OLTreeSet
        from BTrees.OLBTree import OLSet
        return OLSet, OLTreeSet, makeBuilder(OLBTree), makeBuilder(OLBucket)


class TestWeightedOL(Weighted, unittest.TestCase):
    def weightedUnion(self):
        from BTrees.OLBTree import weightedUnion
        return weightedUnion
    def weightedIntersection(self):
        from BTrees.OLBTree import weightedIntersection
        return weightedIntersection
    def union(self):
        from BTrees.OLBTree import union
        return union
    def intersection(self):
        from BTrees.OLBTree import intersection
        return intersection
    def mkbucket(self, *args):
        from BTrees.OLBTree import OLBucket as mkbucket
        return mkbucket(*args)
    def builders(self):
        from BTrees.OLBTree import OLBTree
        from BTrees.OLBTree import OLBucket
        from BTrees.OLBTree import OLTreeSet
        from BTrees.OLBTree import OLSet
        return OLBucket, OLBTree, itemsToSet(OLSet), itemsToSet(OLTreeSet)


class OLBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLBucket
        return OLBucket


class OLSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLSet
        return OLSet


class OLBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLBTree
        return OLBTree


class OLTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLTreeSet
        return OLTreeSet


class OLModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'OL'

    def _getModule(self):
        import BTrees
        return BTrees.OLBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IObjectIntegerBTreeModule

    def test_multiunion_not_present(self):
        try:
            from BTrees.OLBTree import multiunion
        except ImportError:
            pass
        else:
            self.fail("OLBTree shouldn't have multiunion")


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(OLBTreeInternalKeyTest),
        unittest.makeSuite(OLTreeSetInternalKeyTest),
        unittest.makeSuite(OLBucketTest),
        unittest.makeSuite(OLTreeSetTest),
        unittest.makeSuite(OLSetTest),
        unittest.makeSuite(OLBTreeTest),
        unittest.makeSuite(PureOL),
        unittest.makeSuite(TestWeightedOL),
        unittest.makeSuite(OLBucketConflictTests),
        unittest.makeSuite(OLSetConflictTests),
        unittest.makeSuite(OLBTreeConflictTests),
        unittest.makeSuite(OLTreeSetConflictTests),
        unittest.makeSuite(OLModuleTest),
    ))
