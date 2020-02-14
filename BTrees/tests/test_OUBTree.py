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
from .common import TypeTest
from .common import Weighted
from .common import itemsToSet
from .common import makeBuilder
from .common import UnsignedValuesMixin


class OUBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OUBTree import OUBTree
        return OUBTree


class OUBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OUBTree import OUBTreePy
        return OUBTreePy


class OUBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OUBTree import OUBucket
        return OUBucket


class OUBucketPyTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OUBTree import OUBucketPy
        return OUBucketPy


class OUTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OUBTree import OUTreeSet
        return OUTreeSet


class OUTreeSetPyTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OUBTree import OUTreeSetPy
        return OUTreeSetPy


class OUSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OUBTree import OUSet
        return OUSet


class OUSetPyTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OUBTree import OUSetPy
        return OUSetPy


class OUBTreeTest(BTreeTests, unittest.TestCase):

    def _makeOne(self):
        from BTrees.OUBTree import OUBTree
        return OUBTree()


class OUBTreePyTest(BTreeTests, unittest.TestCase):
    def _makeOne(self):
        from BTrees.OUBTree import OUBTreePy
        return OUBTreePy()


class _TestOUBTreesBase(TypeTest):

    def _stringraises(self):
        self._makeOne()[1] = 'c'

    def _floatraises(self):
        self._makeOne()[1] = 1.4

    def _noneraises(self):
        self._makeOne()[1] = None

    def testEmptyFirstBucketReportedByGuido(self):
        from .._compat import xrange
        b = self._makeOne()
        for i in xrange(29972): # reduce to 29971 and it works
            b[i] = i
        for i in xrange(30): # reduce to 29 and it works
            del b[i]
            b[i+40000] = i

        self.assertEqual(b.keys()[0], 30)


class TestOUBTrees(_TestOUBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.OUBTree import OUBTree
        return OUBTree()


class TestOUBTreesPy(_TestOUBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.OUBTree import OUBTreePy
        return OUBTreePy()


class PureOU(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.OUBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.OUBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.OUBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.OUBTree import OUBTree
        from BTrees.OUBTree import OUBucket
        from BTrees.OUBTree import OUTreeSet
        from BTrees.OUBTree import OUSet
        return OUSet, OUTreeSet, makeBuilder(OUBTree), makeBuilder(OUBucket)


class PureOUPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.OUBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.OUBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.OUBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.OUBTree import OUBTreePy
        from BTrees.OUBTree import OUBucketPy
        from BTrees.OUBTree import OUTreeSetPy
        from BTrees.OUBTree import OUSetPy
        return (OUSetPy, OUTreeSetPy,
                makeBuilder(OUBTreePy), makeBuilder(OUBucketPy))


class TestWeightedOU(UnsignedValuesMixin, Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.OUBTree import weightedUnion
        return weightedUnion

    def weightedIntersection(self):
        from BTrees.OUBTree import weightedIntersection
        return weightedIntersection

    def union(self):
        from BTrees.OUBTree import union
        return union

    def intersection(self):
        from BTrees.OUBTree import intersection
        return intersection

    def mkbucket(self, *args):
        from BTrees.OUBTree import OUBucket as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.OUBTree import OUBTree
        from BTrees.OUBTree import OUBucket
        from BTrees.OUBTree import OUTreeSet
        from BTrees.OUBTree import OUSet
        return OUBucket, OUBTree, itemsToSet(OUSet), itemsToSet(OUTreeSet)


class TestWeightedOUPy(Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.OUBTree import weightedUnionPy
        return weightedUnionPy

    def weightedIntersection(self):
        from BTrees.OUBTree import weightedIntersectionPy
        return weightedIntersectionPy

    def union(self):
        from BTrees.OUBTree import unionPy
        return unionPy

    def intersection(self):
        from BTrees.OUBTree import intersectionPy
        return intersectionPy

    def mkbucket(self, *args):
        from BTrees.OUBTree import OUBucketPy as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.OUBTree import OUBTreePy
        from BTrees.OUBTree import OUBucketPy
        from BTrees.OUBTree import OUTreeSetPy
        from BTrees.OUBTree import OUSetPy
        return (OUBucketPy, OUBTreePy,
                itemsToSet(OUSetPy), itemsToSet(OUTreeSetPy))


class OUBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OUBTree import OUBucket
        return OUBucket


class OUBucketConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OUBTree import OUBucketPy
        return OUBucketPy


class OUSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OUBTree import OUSet
        return OUSet


class OUSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OUBTree import OUSetPy
        return OUSetPy


class OUBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OUBTree import OUBTree
        return OUBTree


class OUBTreeConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OUBTree import OUBTreePy
        return OUBTreePy


class OUTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OUBTree import OUTreeSet
        return OUTreeSet


class OUTreeSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OUBTree import OUTreeSetPy
        return OUTreeSetPy


class OUModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'OU'

    def _getModule(self):
        import BTrees
        return BTrees.OUBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IObjectUnsignedBTreeModule

    def test_multiunion_not_present(self):
        try:
            from BTrees.OUBTree import multiunion
        except ImportError:
            pass
        else:
            self.fail("OUBTree shouldn't have multiunion")
