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
from .common import ModuleTest
from .common import MultiUnion
from .common import NormalSetTests
from .common import SetResult
from .common import TestLongIntKeys
from .common import makeBuilder


class LOBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOBTree
        return LOBTree


class LOTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOTreeSet
        return LOTreeSet


class LOBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOBucket
        return LOBucket


class LOTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOTreeSet
        return LOTreeSet


class LOSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LOBTree import LOSet
        return LOSet


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



class LOBTreeTest(BTreeTests, TestLongIntKeys, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LOBTree import LOBTree
        return LOBTree()


class TestLOSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LOBTree import LOSet
        return LOSet()


class TestLOTreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LOBTree import LOTreeSet
        return LOTreeSet()


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


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(LOBTreeInternalKeyTest),
        unittest.makeSuite(LOTreeSetInternalKeyTest),
        unittest.makeSuite(LOBucketTest),
        unittest.makeSuite(LOTreeSetTest),
        unittest.makeSuite(LOSetTest),
        unittest.makeSuite(LOModuleTest),
        unittest.makeSuite(LOBTreeTest),
        unittest.makeSuite(TestLOSets),
        unittest.makeSuite(TestLOTreeSets),

        unittest.makeSuite(TestLOMultiUnion),
        unittest.makeSuite(PureLO),
    ))
