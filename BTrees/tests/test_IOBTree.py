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
from .common import TypeTest
from .common import TestLongIntKeys
from .common import makeBuilder
from BTrees.IIBTree import using64bits #XXX Ugly, but unavoidable


class IOBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOBTree
        return IOBTree


class IOBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOBTreePy
        return IOBTreePy


class IOTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOTreeSet
        return IOTreeSet


class IOTreeSetPyInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOTreeSetPy
        return IOTreeSetPy


class IOBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOBucket
        return IOBucket


class IOBucketPyTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOBucketPy
        return IOBucketPy


class IOTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOTreeSet
        return IOTreeSet


class IOTreeSetPyTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOTreeSetPy
        return IOTreeSetPy


class IOSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOSet
        return IOSet


class IOSetPyTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOSetPy
        return IOSetPy


class IOBTreeTest(BTreeTests, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IOBTree import IOBTree
        return IOBTree()


class IOBTreePyTest(BTreeTests, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IOBTree import IOBTreePy
        return IOBTreePy()


if using64bits:


    class IOBTreeTest(BTreeTests, TestLongIntKeys, unittest.TestCase):

        def _makeOne(self):
            from BTrees.IOBTree import IOBTree
            return IOBTree()


    class IOBTreePyTest(BTreeTests, TestLongIntKeys, unittest.TestCase):

        def _makeOne(self):
            from BTrees.IOBTree import IOBTreePy
            return IOBTreePy()


class _TestIOBTreesBase(TypeTest):

    def _stringraises(self):
        self._makeOne()['c'] = 1

    def _floatraises(self):
        self._makeOne()[2.5] = 1

    def _noneraises(self):
        self._makeOne()[None] = 1


class TestIOBTrees(_TestIOBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IOBTree import IOBTree
        return IOBTree()


class TestIOBTreesPy(_TestIOBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IOBTree import IOBTreePy
        return IOBTreePy()


class TestIOSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IOBTree import IOSet
        return IOSet()


class TestIOSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IOBTree import IOSetPy
        return IOSetPy()


class TestIOTreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IOBTree import IOTreeSet
        return IOTreeSet()


class TestIOTreeSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IOBTree import IOTreeSetPy
        return IOTreeSetPy()


class PureIO(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.IOBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.IOBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.IOBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.IOBTree import IOBTree
        from BTrees.IOBTree import IOBucket
        from BTrees.IOBTree import IOTreeSet
        from BTrees.IOBTree import IOSet
        return IOSet, IOTreeSet, makeBuilder(IOBTree), makeBuilder(IOBucket)


class PureIOPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.IOBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.IOBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.IOBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.IOBTree import IOBTreePy
        from BTrees.IOBTree import IOBucketPy
        from BTrees.IOBTree import IOTreeSetPy
        from BTrees.IOBTree import IOSetPy
        return (IOSetPy, IOTreeSetPy,
                makeBuilder(IOBTreePy), makeBuilder(IOBucketPy))


class TestIOMultiUnion(MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.IOBTree import multiunion
        return multiunion(*args)

    def union(self, *args):
        from BTrees.IOBTree import union
        return union(*args)

    def mkset(self, *args):
        from BTrees.IOBTree import IOSet as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.IOBTree import IOTreeSet as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.IOBTree import IOBucket as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.IOBTree import IOBTree as mkbtree
        return mkbtree(*args)


class TestIOMultiUnionPy(MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.IOBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.IOBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.IOBTree import IOSetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.IOBTree import IOTreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.IOBTree import IOBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.IOBTree import IOBTreePy as mkbtree
        return mkbtree(*args)


class IOBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOBTree
        return IOBTree


class IOBTreeConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOBTreePy
        return IOBTreePy


class IOBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOBucket
        return IOBucket


class IOBucketConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOBucketPy
        return IOBucketPy


class IOTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOTreeSet
        return IOTreeSet


class IOTreeSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOTreeSetPy
        return IOTreeSetPy


class IOSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOSet
        return IOSet


class IOSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOSetPy
        return IOSetPy


class IOModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'IO'

    def _getModule(self):
        import BTrees
        return BTrees.IOBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IIntegerObjectBTreeModule

    def test_weightedUnion_not_present(self):
        try:
            from BTrees.IOBTree import weightedUnion
        except ImportError:
            pass
        else:
            self.fail("IOBTree shouldn't have weightedUnion")

    def test_weightedIntersection_not_present(self):
        try:
            from BTrees.IOBTree import weightedIntersection
        except ImportError:
            pass
        else:
            self.fail("IOBTree shouldn't have weightedIntersection")


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(IOBTreeInternalKeyTest),
        unittest.makeSuite(IOBTreePyInternalKeyTest),
        unittest.makeSuite(IOTreeSetInternalKeyTest),
        unittest.makeSuite(IOTreeSetPyInternalKeyTest),
        unittest.makeSuite(IOBucketTest),
        unittest.makeSuite(IOBucketPyTest),
        unittest.makeSuite(IOTreeSetTest),
        unittest.makeSuite(IOTreeSetPyTest),
        unittest.makeSuite(IOSetTest),
        unittest.makeSuite(IOSetPyTest),
        unittest.makeSuite(IOBTreeTest),
        unittest.makeSuite(IOBTreePyTest),
        unittest.makeSuite(TestIOBTrees),
        unittest.makeSuite(TestIOBTreesPy),
        unittest.makeSuite(TestIOSets),
        unittest.makeSuite(TestIOSetsPy),
        unittest.makeSuite(TestIOTreeSets),
        unittest.makeSuite(TestIOTreeSetsPy),
        unittest.makeSuite(TestIOMultiUnion),
        unittest.makeSuite(TestIOMultiUnionPy),
        unittest.makeSuite(PureIO),
        unittest.makeSuite(PureIOPy),
        unittest.makeSuite(IOBTreeConflictTests),
        unittest.makeSuite(IOBTreeConflictTestsPy),
        unittest.makeSuite(IOBucketConflictTests),
        unittest.makeSuite(IOBucketConflictTestsPy),
        unittest.makeSuite(IOTreeSetConflictTests),
        unittest.makeSuite(IOTreeSetConflictTestsPy),
        unittest.makeSuite(IOSetConflictTests),
        unittest.makeSuite(IOSetConflictTestsPy),
        unittest.makeSuite(IOModuleTest),
    ))
