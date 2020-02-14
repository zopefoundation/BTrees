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
from .common import UnsignedValuesMappingBase as MappingBase
from .common import UnsignedValuesMappingConflictTestBase as MappingConflictTestBase
from .common import ModuleTest
from .common import MultiUnion
from .common import NormalSetTests
from .common import SetConflictTestBase
from .common import SetResult
from .common import Weighted
from .common import itemsToSet
from .common import makeBuilder
from .common import UnsignedValuesMixin
from .common import UnsignedError


# pylint:disable=no-name-in-module,arguments-differ

class IUBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IUBTree import IUBTree
        return IUBTree


class IUBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IUBTree import IUBTreePy
        return IUBTreePy


class IUBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IUBTree import IUBucket
        return IUBucket


class IUBucketPyTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IUBTree import IUBucketPy
        return IUBucketPy


class IUTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IUBTree import IUTreeSet
        return IUTreeSet


class IUTreeSetPyTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IUBTree import IUTreeSetPy
        return IUTreeSetPy


class IUSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IUBTree import IUSet
        return IUSet


class IUSetPyTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IUBTree import IUSetPy
        return IUSetPy


class _IUBTreeTestBase(BTreeTests):

    def testIUBTreeOverflow(self):
        good = set()
        b = self._makeOne()

        def trial(i):
            i = int(i)
            try:
                b[i] = i
            except UnsignedError:
                pass
            else:
                good.add(i)
                b[0] = i
                self.assertEqual(b[0], i)

        for i in range((1<<31) - 3, (1<<31) + 3):
            trial(i)
            trial(-i)

        del b[0]
        self.assertEqual(sorted(good), sorted(b))


class IUBTreeTest(_IUBTreeTestBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IUBTree import IUBTree
        return IUBTree()


class IUBTreeTestPy(_IUBTreeTestBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IUBTree import IUBTreePy
        return IUBTreePy()


class _TestIUBTreesBase(object):

    def testNonIntegerKeyRaises(self):
        self.assertRaises(TypeError, self._stringraiseskey)
        self.assertRaises(TypeError, self._floatraiseskey)
        self.assertRaises(TypeError, self._noneraiseskey)

    def testNonIntegerValueRaises(self):
        self.assertRaises(TypeError, self._stringraisesvalue)
        self.assertRaises(TypeError, self._floatraisesvalue)
        self.assertRaises(TypeError, self._noneraisesvalue)

    def _stringraiseskey(self):
        self._makeOne()['c'] = 1

    def _floatraiseskey(self):
        self._makeOne()[2.5] = 1

    def _noneraiseskey(self):
        self._makeOne()[None] = 1

    def _stringraisesvalue(self):
        self._makeOne()[1] = 'c'

    def _floatraisesvalue(self):
        self._makeOne()[1] = 1.4

    def _noneraisesvalue(self):
        self._makeOne()[1] = None


class TestIUBTrees(_TestIUBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IUBTree import IUBTree
        return IUBTree()


class TestIUBTreesPy(_TestIUBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IUBTree import IUBTreePy
        return IUBTreePy()


class TestIUSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IUBTree import IUSet
        return IUSet()


class TestIUSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IUBTree import IUSetPy
        return IUSetPy()


class TestIUTreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IUBTree import IUTreeSet
        return IUTreeSet()


class TestIUTreeSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IUBTree import IUTreeSetPy
        return IUTreeSetPy()


class PureIU(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.IUBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.IUBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.IUBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.IUBTree import IUBTree
        from BTrees.IUBTree import IUBucket
        from BTrees.IUBTree import IUTreeSet
        from BTrees.IUBTree import IUSet
        return IUSet, IUTreeSet, makeBuilder(IUBTree), makeBuilder(IUBucket)


class PureIUPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.IUBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.IUBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.IUBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.IUBTree import IUBTreePy
        from BTrees.IUBTree import IUBucketPy
        from BTrees.IUBTree import IUTreeSetPy
        from BTrees.IUBTree import IUSetPy
        return (IUSetPy, IUTreeSetPy,
                makeBuilder(IUBTreePy), makeBuilder(IUBucketPy))


class TestIUMultiUnion(UnsignedValuesMixin, MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.IUBTree import multiunion
        return multiunion(*args)

    def union(self, *args):
        from BTrees.IUBTree import union
        return union(*args)

    def mkset(self, *args):
        from BTrees.IUBTree import IUSet as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.IUBTree import IUTreeSet as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.IUBTree import IUBucket as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.IUBTree import IUBTree as mkbtree
        return mkbtree(*args)


class TestIUMultiUnionPy(UnsignedValuesMixin, MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.IUBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.IUBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.IUBTree import IUSetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.IUBTree import IUTreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.IUBTree import IUBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.IUBTree import IUBTreePy as mkbtree
        return mkbtree(*args)


class TestWeightedIU(UnsignedValuesMixin, Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.IUBTree import weightedUnion
        return weightedUnion

    def weightedIntersection(self):
        from BTrees.IUBTree import weightedIntersection
        return weightedIntersection

    def union(self):
        from BTrees.IUBTree import union
        return union

    def intersection(self):
        from BTrees.IUBTree import intersection
        return intersection

    def mkbucket(self, *args):
        from BTrees.IUBTree import IUBucket as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.IUBTree import IUBTree
        from BTrees.IUBTree import IUBucket
        from BTrees.IUBTree import IUTreeSet
        from BTrees.IUBTree import IUSet
        return IUBucket, IUBTree, itemsToSet(IUSet), itemsToSet(IUTreeSet)


class TestWeightedIUPy(UnsignedValuesMixin, Weighted, unittest.TestCase):

    def weightedUnion(self):
        from BTrees.IUBTree import weightedUnionPy
        return weightedUnionPy

    def weightedIntersection(self):
        from BTrees.IUBTree import weightedIntersectionPy
        return weightedIntersectionPy

    def union(self):
        from BTrees.IUBTree import unionPy
        return unionPy

    def intersection(self):
        from BTrees.IUBTree import intersectionPy
        return intersectionPy

    def mkbucket(self, *args):
        from BTrees.IUBTree import IUBucketPy as mkbucket
        return mkbucket(*args)

    def builders(self):
        from BTrees.IUBTree import IUBTreePy
        from BTrees.IUBTree import IUBucketPy
        from BTrees.IUBTree import IUTreeSetPy
        from BTrees.IUBTree import IUSetPy
        return (IUBucketPy, IUBTreePy,
                itemsToSet(IUSetPy), itemsToSet(IUTreeSetPy))


class IUBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IUBTree import IUBTree
        return IUBTree


class IUBTreeConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IUBTree import IUBTreePy
        return IUBTreePy


class IUBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IUBTree import IUBucket
        return IUBucket


class IUBucketConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IUBTree import IUBucketPy
        return IUBucketPy


class IUTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IUBTree import IUTreeSet
        return IUTreeSet


class IUTreeSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IUBTree import IUTreeSetPy
        return IUTreeSetPy


class IUSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IUBTree import IUSet
        return IUSet


class IUSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IUBTree import IUSetPy
        return IUSetPy


class IUModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'IU'

    def _getModule(self):
        import BTrees
        return BTrees.IUBTree
    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IIntegerUnsignedBTreeModule
