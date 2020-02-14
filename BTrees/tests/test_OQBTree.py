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
from .common import InternalKeysMappingTest
from .common import UnsignedValuesMappingBase as MappingBase
from .common import UnsignedValuesMappingConflictTestBase as MappingConflictTestBase
from .common import ModuleTest
from .common import NormalSetTests
from .common import SetConflictTestBase
from .common import SetResult
from .common import TestLongIntValues
from .common import Weighted
from .common import itemsToSet
from .common import makeBuilder
from .common import _skip_on_32_bits
from .common import UnsignedValuesMixin

# pylint:disable=no-name-in-module,arguments-differ

class OQBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OQBTree import OQBTree
        return OQBTree


class OQBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OQBTree import OQBTreePy
        return OQBTreePy


class OQBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OQBTree import OQBucket
        return OQBucket


class OQBucketPyTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OQBTree import OQBucketPy
        return OQBucketPy


class OQTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OQBTree import OQTreeSet
        return OQTreeSet


class OQTreeSetPyTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OQBTree import OQTreeSetPy
        return OQTreeSetPy


class OQSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OQBTree import OQSet
        return OQSet


class OQSetPyTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OQBTree import OQSetPy
        return OQSetPy


class OQBTreeTest(BTreeTests, TestLongIntValues, unittest.TestCase):

    def _makeOne(self):
        from BTrees.OQBTree import OQBTree
        return OQBTree()

    def getTwoKeys(self):
        return "abc", "def"

    @_skip_on_32_bits
    def test_extremes(self):
        from BTrees.tests.common import SMALLEST_POSITIVE_65_BITS
        from BTrees.tests.common import LARGEST_64_BITS
        from BTrees.tests.common import LARGEST_NEGATIVE_65_BITS
        btree = self._makeOne()
        btree['ZERO'] = 0
        btree['SMALLEST_64_BITS'] = 0
        btree['LARGEST_64_BITS'] = LARGEST_64_BITS
        btree['SMALLEST_POSITIVE_65_BITS'] = SMALLEST_POSITIVE_65_BITS
        with self.assertRaises((ValueError, OverflowError)):
            btree['TOO_BIG'] = 2**65

        self.assertRaises((ValueError, OverflowError), btree.__setitem__,
                          'LARGEST_NEGATIVE_65_BITS', LARGEST_NEGATIVE_65_BITS)


class OQBTreePyTest(BTreeTests, TestLongIntValues, unittest.TestCase):

    def _makeOne(self):
        from BTrees.OQBTree import OQBTreePy
        return OQBTreePy()

    def getTwoKeys(self):
        return "abc", "def"


class PureOQ(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.OQBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.OQBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.OQBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.OQBTree import OQBTree
        from BTrees.OQBTree import OQBucket
        from BTrees.OQBTree import OQTreeSet
        from BTrees.OQBTree import OQSet
        return OQSet, OQTreeSet, makeBuilder(OQBTree), makeBuilder(OQBucket)


class PureOQPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.OQBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.OQBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.OQBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.OQBTree import OQBTreePy
        from BTrees.OQBTree import OQBucketPy
        from BTrees.OQBTree import OQTreeSetPy
        from BTrees.OQBTree import OQSetPy
        return (OQSetPy, OQTreeSetPy,
                makeBuilder(OQBTreePy), makeBuilder(OQBucketPy))


class TestWeightedOQ(UnsignedValuesMixin, Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.OQBTree import weightedUnion
        return weightedUnion

    def weightedIntersection(self):
        from BTrees.OQBTree import weightedIntersection
        return weightedIntersection

    def union(self):
        from BTrees.OQBTree import union
        return union

    def intersection(self):
        from BTrees.OQBTree import intersection
        return intersection

    def mkbucket(self, *args):
        from BTrees.OQBTree import OQBucket as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.OQBTree import OQBTree
        from BTrees.OQBTree import OQBucket
        from BTrees.OQBTree import OQTreeSet
        from BTrees.OQBTree import OQSet
        return OQBucket, OQBTree, itemsToSet(OQSet), itemsToSet(OQTreeSet)


class TestWeightedOQPy(Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.OQBTree import weightedUnionPy
        return weightedUnionPy

    def weightedIntersection(self):
        from BTrees.OQBTree import weightedIntersectionPy
        return weightedIntersectionPy

    def union(self):
        from BTrees.OQBTree import unionPy
        return unionPy

    def intersection(self):
        from BTrees.OQBTree import intersectionPy
        return intersectionPy

    def mkbucket(self, *args):
        from BTrees.OQBTree import OQBucketPy as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.OQBTree import OQBTreePy
        from BTrees.OQBTree import OQBucketPy
        from BTrees.OQBTree import OQTreeSetPy
        from BTrees.OQBTree import OQSetPy
        return (OQBucketPy, OQBTreePy,
                itemsToSet(OQSetPy), itemsToSet(OQTreeSetPy))


class OQBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OQBTree import OQBucket
        return OQBucket


class OQBucketPyConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OQBTree import OQBucketPy
        return OQBucketPy


class OQSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OQBTree import OQSet
        return OQSet


class OQSetPyConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OQBTree import OQSetPy
        return OQSetPy


class OQBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OQBTree import OQBTree
        return OQBTree


class OQBTreePyConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OQBTree import OQBTreePy
        return OQBTreePy


class OQTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OQBTree import OQTreeSet
        return OQTreeSet


class OQTreeSetPyConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OQBTree import OQTreeSetPy
        return OQTreeSetPy


class OQModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'OQ'

    def _getModule(self):
        import BTrees
        return BTrees.OQBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IObjectUnsignedBTreeModule

    def test_multiunion_not_present(self):
        try:
            from BTrees.OQBTree import multiunion
        except ImportError:
            pass
        else:
            self.fail("OQBTree shouldn't have multiunion")
