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
from .common import TypeTest
from .common import Weighted
from .common import itemsToSet
from .common import makeBuilder
from BTrees.IIBTree import using64bits #XXX Ugly, but necessary


class OIBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OIBTree import OIBTree
        return OIBTree


class OITreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OIBTree import OITreeSet
        return OITreeSet


class OIBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OIBTree import OIBucket
        return OIBucket


class OITreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OIBTree import OITreeSet
        return OITreeSet


class OISetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OIBTree import OISet
        return OISet


class OIBTreeTest(BTreeTests, unittest.TestCase):

    def _makeOne(self):
        from BTrees.OIBTree import OIBTree
        return OIBTree()


class OIBTreeTest(BTreeTests, unittest.TestCase):
    def _makeOne(self):
        from BTrees.OIBTree import OIBTree
        return OIBTree()


if using64bits:

    class OIBTreeTest(BTreeTests, TestLongIntValues, unittest.TestCase):
        def _makeOne(self):
            from BTrees.OIBTree import OIBTree
            return OIBTree()
        def getTwoKeys(self):
            return object(), object()

class TestOIBTrees(TypeTest, unittest.TestCase):
    def _makeOne(self):
        from BTrees.OIBTree import OIBTree
        return OIBTree()

    def _stringraises(self):
        self._makeOne()[1] = 'c'

    def _floatraises(self):
        self._makeOne()[1] = 1.4

    def _noneraises(self):
        self._makeOne()[1] = None

    def testEmptyFirstBucketReportedByGuido(self):
        b = self._makeOne()
        for i in xrange(29972): # reduce to 29971 and it works
            b[i] = i
        for i in xrange(30): # reduce to 29 and it works
            del b[i]
            b[i+40000] = i

        self.assertEqual(b.keys()[0], 30)


class PureOI(SetResult, unittest.TestCase):
    def union(self, *args):
        from BTrees.OIBTree import union
        return union(*args)
    def intersection(self, *args):
        from BTrees.OIBTree import intersection
        return intersection(*args)
    def difference(self, *args):
        from BTrees.OIBTree import difference
        return difference(*args)
    def builders(self):
        from BTrees.OIBTree import OIBTree
        from BTrees.OIBTree import OIBucket
        from BTrees.OIBTree import OITreeSet
        from BTrees.OIBTree import OISet
        return OISet, OITreeSet, makeBuilder(OIBTree), makeBuilder(OIBucket)


class TestWeightedOI(Weighted, unittest.TestCase):
    def weightedUnion(self):
        from BTrees.OIBTree import weightedUnion
        return weightedUnion
    def weightedIntersection(self):
        from BTrees.OIBTree import weightedIntersection
        return weightedIntersection
    def union(self):
        from BTrees.OIBTree import union
        return union
    def intersection(self):
        from BTrees.OIBTree import intersection
        return intersection
    def mkbucket(self, *args):
        from BTrees.OIBTree import OIBucket as mkbucket
        return mkbucket(*args)
    def builders(self):
        from BTrees.OIBTree import OIBTree
        from BTrees.OIBTree import OIBucket
        from BTrees.OIBTree import OITreeSet
        from BTrees.OIBTree import OISet
        return OIBucket, OIBTree, itemsToSet(OISet), itemsToSet(OITreeSet)


class OIBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OIBTree import OIBucket
        return OIBucket


class OISetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OIBTree import OISet
        return OISet


class OIBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OIBTree import OIBTree
        return OIBTree


class OITreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OIBTree import OITreeSet
        return OITreeSet


class OIModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'OI'

    def _getModule(self):
        import BTrees
        return BTrees.OIBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IObjectIntegerBTreeModule

    def test_multiunion_not_present(self):
        try:
            from BTrees.OIBTree import multiunion
        except ImportError:
            pass
        else:
            self.fail("OIBTree shouldn't have multiunion")


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(OIBTreeInternalKeyTest),
        unittest.makeSuite(OITreeSetInternalKeyTest),
        unittest.makeSuite(OIBucketTest),
        unittest.makeSuite(OITreeSetTest),
        unittest.makeSuite(OISetTest),
        unittest.makeSuite(OIBTreeTest),
        unittest.makeSuite(TestOIBTrees),
        unittest.makeSuite(PureOI),
        unittest.makeSuite(TestWeightedOI),
        unittest.makeSuite(OIBucketConflictTests),
        unittest.makeSuite(OISetConflictTests),
        unittest.makeSuite(OIBTreeConflictTests),
        unittest.makeSuite(OITreeSetConflictTests),
        unittest.makeSuite(OIModuleTest),
    ))
