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
from .common import _skip_on_32_bits


class OLBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLBTree
        return OLBTree


class OLBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLBTreePy
        return OLBTreePy


class OLTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLTreeSet
        return OLTreeSet


class OLTreeSetPyInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLTreeSetPy
        return OLTreeSetPy


class OLBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLBucket
        return OLBucket


class OLBucketPyTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLBucketPy
        return OLBucketPy


class OLTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLTreeSet
        return OLTreeSet


class OLTreeSetPyTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLTreeSetPy
        return OLTreeSetPy


class OLSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLSet
        return OLSet


class OLSetPyTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLSetPy
        return OLSetPy


class OLBTreeTest(BTreeTests, TestLongIntValues, unittest.TestCase):

    def _makeOne(self):
        from BTrees.OLBTree import OLBTree
        return OLBTree()

    def getTwoKeys(self):
        return "abc", "def"

    @_skip_on_32_bits
    def test_extremes(self):
        from BTrees.tests.common import SMALLEST_64_BITS
        from BTrees.tests.common import SMALLEST_POSITIVE_65_BITS
        from BTrees.tests.common import LARGEST_64_BITS
        from BTrees.tests.common import LARGEST_NEGATIVE_65_BITS
        btree = self._makeOne()
        btree['ZERO'] = 0
        btree['SMALLEST_64_BITS'] = SMALLEST_64_BITS
        btree['LARGEST_64_BITS'] = LARGEST_64_BITS
        self.assertRaises((ValueError, OverflowError), btree.__setitem__,
            'SMALLEST_POSITIVE_65_BITS', SMALLEST_POSITIVE_65_BITS)
        self.assertRaises((ValueError, OverflowError), btree.__setitem__,
            'LARGEST_NEGATIVE_65_BITS', LARGEST_NEGATIVE_65_BITS)


class OLBTreePyTest(BTreeTests, TestLongIntValues, unittest.TestCase):

    def _makeOne(self):
        from BTrees.OLBTree import OLBTreePy
        return OLBTreePy()

    def getTwoKeys(self):
        return "abc", "def"


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


class PureOLPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.OLBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.OLBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.OLBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.OLBTree import OLBTreePy
        from BTrees.OLBTree import OLBucketPy
        from BTrees.OLBTree import OLTreeSetPy
        from BTrees.OLBTree import OLSetPy
        return (OLSetPy, OLTreeSetPy,
                makeBuilder(OLBTreePy), makeBuilder(OLBucketPy))


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


class TestWeightedOLPy(Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.OLBTree import weightedUnionPy
        return weightedUnionPy

    def weightedIntersection(self):
        from BTrees.OLBTree import weightedIntersectionPy
        return weightedIntersectionPy

    def union(self):
        from BTrees.OLBTree import unionPy
        return unionPy

    def intersection(self):
        from BTrees.OLBTree import intersectionPy
        return intersectionPy

    def mkbucket(self, *args):
        from BTrees.OLBTree import OLBucketPy as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.OLBTree import OLBTreePy
        from BTrees.OLBTree import OLBucketPy
        from BTrees.OLBTree import OLTreeSetPy
        from BTrees.OLBTree import OLSetPy
        return (OLBucketPy, OLBTreePy,
                itemsToSet(OLSetPy), itemsToSet(OLTreeSetPy))


class OLBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLBucket
        return OLBucket


class OLBucketPyConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLBucketPy
        return OLBucketPy


class OLSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLSet
        return OLSet


class OLSetPyConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLSetPy
        return OLSetPy


class OLBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLBTree
        return OLBTree


class OLBTreePyConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLBTreePy
        return OLBTreePy


class OLTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLTreeSet
        return OLTreeSet


class OLTreeSetPyConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLTreeSetPy
        return OLTreeSetPy


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
        unittest.makeSuite(OLBTreePyInternalKeyTest),
        unittest.makeSuite(OLTreeSetInternalKeyTest),
        unittest.makeSuite(OLTreeSetPyInternalKeyTest),
        unittest.makeSuite(OLBucketTest),
        unittest.makeSuite(OLBucketPyTest),
        unittest.makeSuite(OLTreeSetTest),
        unittest.makeSuite(OLTreeSetPyTest),
        unittest.makeSuite(OLSetTest),
        unittest.makeSuite(OLSetPyTest),
        unittest.makeSuite(OLBTreeTest),
        unittest.makeSuite(OLBTreePyTest),
        unittest.makeSuite(PureOL),
        unittest.makeSuite(PureOLPy),
        unittest.makeSuite(TestWeightedOL),
        unittest.makeSuite(TestWeightedOLPy),
        unittest.makeSuite(OLBucketConflictTests),
        unittest.makeSuite(OLBucketPyConflictTests),
        unittest.makeSuite(OLSetConflictTests),
        unittest.makeSuite(OLSetPyConflictTests),
        unittest.makeSuite(OLBTreeConflictTests),
        unittest.makeSuite(OLBTreePyConflictTests),
        unittest.makeSuite(OLTreeSetConflictTests),
        unittest.makeSuite(OLTreeSetPyConflictTests),
        unittest.makeSuite(OLModuleTest),
    ))
