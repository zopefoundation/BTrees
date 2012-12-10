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
from .common import makeBuilder


class LOBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOBTree
        return LOBTree


class LOBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOBTreePy
        return LOBTreePy


class LOTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOTreeSet
        return LOTreeSet


class LOTreeSetPyInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOTreeSetPy
        return LOTreeSetPy


class LOBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOBucket
        return LOBucket


class LOBucketPyTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOBucketPy
        return LOBucketPy


class LOTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOTreeSet
        return LOTreeSet


class LOTreeSetPyTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOTreeSetPy
        return LOTreeSetPy


class LOSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOSet
        return LOSet


class LOSetPyTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOSetPy
        return LOSetPy


class LOBTreeTest(BTreeTests, TestLongIntKeys, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LOBTree import LOBTree
        return LOBTree()


class LOBTreePyTest(BTreeTests, TestLongIntKeys, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LOBTree import LOBTreePy
        return LOBTreePy()


class TestLOSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LOBTree import LOSet
        return LOSet()


class TestLOSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LOBTree import LOSetPy
        return LOSetPy()


class TestLOTreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LOBTree import LOTreeSet
        return LOTreeSet()


class TestLOTreeSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LOBTree import LOTreeSetPy
        return LOTreeSetPy()


class TestLOMultiUnion(MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.LOBTree import multiunion
        return multiunion(*args)

    def union(self, *args):
        from BTrees.LOBTree import union
        return union(*args)

    def mkset(self, *args):
        from BTrees.LOBTree import LOSet as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.LOBTree import LOTreeSet as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.LOBTree import LOBucket as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.LOBTree import LOBTree as mkbtree
        return mkbtree(*args)


class TestLOMultiUnionPy(MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.LOBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.LOBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.LOBTree import LOSetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.LOBTree import LOTreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.LOBTree import LOBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.LOBTree import LOBTreePy as mkbtree
        return mkbtree(*args)


class PureLO(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.LOBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.LOBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.LOBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.LOBTree import LOBTree
        from BTrees.LOBTree import LOBucket
        from BTrees.LOBTree import LOTreeSet
        from BTrees.LOBTree import LOSet
        return LOSet, LOTreeSet, makeBuilder(LOBTree), makeBuilder(LOBucket)


class PureLOPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.LOBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.LOBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.LOBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.LOBTree import LOBTreePy
        from BTrees.LOBTree import LOBucketPy
        from BTrees.LOBTree import LOTreeSetPy
        from BTrees.LOBTree import LOSetPy
        return (LOSetPy, LOTreeSetPy,
                makeBuilder(LOBTreePy), makeBuilder(LOBucketPy))


class LOBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOBTree
        return LOBTree


class LOBTreeConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOBTreePy
        return LOBTreePy


class LOBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOBucket
        return LOBucket


class LOBucketConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOBucketPy
        return LOBucketPy


class LOTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOTreeSet
        return LOTreeSet


class LOTreeSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOTreeSetPy
        return LOTreeSetPy


class LOSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOSet
        return LOSet


class LOSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOSetPy
        return LOSetPy


class LOModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'LO'

    def _getModule(self):
        import BTrees
        return BTrees.LOBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IIntegerObjectBTreeModule

    def test_weightedUnion_not_present(self):
        try:
            from BTrees.LOBTree import weightedUnion
        except ImportError:
            pass
        else:
            self.fail("LOBTree shouldn't have weightedUnion")

    def test_weightedIntersection_not_present(self):
        try:
            from BTrees.LOBTree import weightedIntersection
        except ImportError:
            pass
        else:
            self.fail("LOBTree shouldn't have weightedIntersection")


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(LOBTreeInternalKeyTest),
        unittest.makeSuite(LOBTreePyInternalKeyTest),
        unittest.makeSuite(LOTreeSetInternalKeyTest),
        unittest.makeSuite(LOTreeSetPyInternalKeyTest),
        unittest.makeSuite(LOBucketTest),
        unittest.makeSuite(LOBucketPyTest),
        unittest.makeSuite(LOTreeSetTest),
        unittest.makeSuite(LOTreeSetPyTest),
        unittest.makeSuite(LOSetTest),
        unittest.makeSuite(LOSetPyTest),
        unittest.makeSuite(LOBTreeTest),
        unittest.makeSuite(LOBTreePyTest),
        unittest.makeSuite(TestLOSets),
        unittest.makeSuite(TestLOSetsPy),
        unittest.makeSuite(TestLOTreeSets),
        unittest.makeSuite(TestLOTreeSetsPy),
        unittest.makeSuite(TestLOMultiUnion),
        unittest.makeSuite(TestLOMultiUnionPy),
        unittest.makeSuite(PureLO),
        unittest.makeSuite(PureLOPy),
        unittest.makeSuite(LOBTreeConflictTests),
        unittest.makeSuite(LOBTreeConflictTestsPy),
        unittest.makeSuite(LOBucketConflictTests),
        unittest.makeSuite(LOBucketConflictTestsPy),
        unittest.makeSuite(LOTreeSetConflictTests),
        unittest.makeSuite(LOTreeSetConflictTestsPy),
        unittest.makeSuite(LOSetConflictTests),
        unittest.makeSuite(LOSetConflictTestsPy),
        unittest.makeSuite(LOModuleTest),
    ))
