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
from .common import MultiUnion
from .common import NormalSetTests
from .common import SetConflictTestBase
from .common import SetResult
from .common import TestLongIntKeys
from .common import makeBuilder


class LFBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFBTree
        return LFBTree


class LFBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFBTreePy
        return LFBTreePy


class LFTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFTreeSet
        return LFTreeSet


class LFTreeSetPyInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFTreeSetPy
        return LFTreeSetPy


class LFBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFBucket
        return LFBucket


class LFBucketPyTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFBucketPy
        return LFBucketPy


class LFTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFTreeSet
        return LFTreeSet


class LFTreeSetPyTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFTreeSetPy
        return LFTreeSetPy


class LFSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFSet
        return LFSet


class LFSetPyTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFSetPy
        return LFSetPy


class LFBTreeTest(BTreeTests, TestLongIntKeys, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LFBTree import LFBTree
        return LFBTree()

    def getTwoValues(self):
        return 0.5, 1.5


class LFBTreePyTest(BTreeTests, TestLongIntKeys, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LFBTree import LFBTreePy
        return LFBTreePy()

    def getTwoValues(self):
        return 0.5, 1.5


class TestLFMultiUnion(MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.LFBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.LFBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.LFBTree import LFSetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.LFBTree import LFTreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.LFBTree import LFBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.LFBTree import LFBTreePy as mkbtree
        return mkbtree(*args)


class TestLFMultiUnionPy(MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.LFBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.LFBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.LFBTree import LFSetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.LFBTree import LFTreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.LFBTree import LFBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.LFBTree import LFBTreePy as mkbtree
        return mkbtree(*args)


class PureLF(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.LFBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.LFBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.LFBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.LFBTree import LFBTree
        from BTrees.LFBTree import LFBucket
        from BTrees.LFBTree import LFTreeSet
        from BTrees.LFBTree import LFSet
        return LFSet, LFTreeSet, makeBuilder(LFBTree), makeBuilder(LFBucket)


class PureLFPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.LFBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.LFBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.LFBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.LFBTree import LFBTreePy
        from BTrees.LFBTree import LFBucketPy
        from BTrees.LFBTree import LFTreeSetPy
        from BTrees.LFBTree import LFSetPy
        return (LFSetPy, LFTreeSetPy,
                makeBuilder(LFBTreePy), makeBuilder(LFBucketPy))


class LFBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFBTree
        return LFBTree


class LFBTreeConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFBTreePy
        return LFBTreePy


class LFBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFBucket
        return LFBucket


class LFBucketConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFBucketPy
        return LFBucketPy


class LFTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFTreeSet
        return LFTreeSet


class LFTreeSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFTreeSetPy
        return LFTreeSetPy


class LFSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFSet
        return LFSet


class LFSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFSetPy
        return LFSetPy


class LFModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'LF'

    def _getModule(self):
        import BTrees
        return BTrees.LFBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IIntegerFloatBTreeModule


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(LFBTreeInternalKeyTest),
        unittest.makeSuite(LFBTreePyInternalKeyTest),
        unittest.makeSuite(LFTreeSetInternalKeyTest),
        unittest.makeSuite(LFTreeSetPyInternalKeyTest),
        unittest.makeSuite(LFBucketTest),
        unittest.makeSuite(LFBucketPyTest),
        unittest.makeSuite(LFTreeSetTest),
        unittest.makeSuite(LFTreeSetPyTest),
        unittest.makeSuite(LFSetTest),
        unittest.makeSuite(LFSetPyTest),
        unittest.makeSuite(LFBTreeTest),
        unittest.makeSuite(LFBTreePyTest),
        unittest.makeSuite(TestLFMultiUnion),
        unittest.makeSuite(TestLFMultiUnionPy),
        unittest.makeSuite(PureLF),
        unittest.makeSuite(PureLFPy),
        unittest.makeSuite(LFBTreeConflictTests),
        unittest.makeSuite(LFBTreeConflictTestsPy),
        unittest.makeSuite(LFBucketConflictTests),
        unittest.makeSuite(LFBucketConflictTestsPy),
        unittest.makeSuite(LFTreeSetConflictTests),
        unittest.makeSuite(LFTreeSetConflictTestsPy),
        unittest.makeSuite(LFSetConflictTests),
        unittest.makeSuite(LFSetConflictTestsPy),
        unittest.makeSuite(LFModuleTest),
    ))
