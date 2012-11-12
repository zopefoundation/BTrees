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
from BTrees.IIBTree import using64bits #XXX Ugly, but unavoidable


class IFBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IFBTree import IFBTree
        return IFBTree


class IFTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IFBTree import IFTreeSet
        return IFTreeSet


class IFBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IFBTree import IFBucket
        return IFBucket


class IFTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IFBTree import IFTreeSet
        return IFTreeSet

class IFSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IFBTree import IFSet
        return IFSet


class IFBTreeTest(BTreeTests, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IFBTree import IFBTree
        return IFBTree()

if using64bits:

    class IFBTreeTest(BTreeTests, TestLongIntKeys, unittest.TestCase):
        def _makeOne(self):
            from BTrees.IFBTree import IFBTree
            return IFBTree()
        def getTwoValues(self):
            return 0.5, 1.5


class TestIFBTrees(unittest.TestCase):

    def _makeOne(self):
        from BTrees.IFBTree import IFBTree
        return IFBTree()

    def testNonIntegerKeyRaises(self):
        self.assertRaises(TypeError, self._stringraiseskey)
        self.assertRaises(TypeError, self._floatraiseskey)
        self.assertRaises(TypeError, self._noneraiseskey)

    def testNonNumericValueRaises(self):
        self.assertRaises(TypeError, self._stringraisesvalue)
        self.assertRaises(TypeError, self._noneraisesvalue)
        self._makeOne()[1] = 1
        self._makeOne()[1] = 1.0

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

class TestIFMultiUnion(MultiUnion, unittest.TestCase):
    def multiunion(self, *args):
        from BTrees.IFBTree import multiunion
        return multiunion(*args)
    def union(self, *args):
        from BTrees.IFBTree import union
        return union(*args)
    def mkset(self, *args):
        from BTrees.IFBTree import IFSet as mkset
        return mkset(*args)
    def mktreeset(self, *args):
        from BTrees.IFBTree import IFTreeSet as mktreeset
        return mktreeset(*args)
    def mkbucket(self, *args):
        from BTrees.IFBTree import IFBucket as mkbucket
        return mkbucket(*args)
    def mkbtree(self, *args):
        from BTrees.IFBTree import IFBTree as mkbtree
        return mkbtree(*args)

class PureIF(SetResult, unittest.TestCase):
    def union(self, *args):
        from BTrees.IFBTree import union
        return union(*args)
    def intersection(self, *args):
        from BTrees.IFBTree import intersection
        return intersection(*args)
    def difference(self, *args):
        from BTrees.IFBTree import difference
        return difference(*args)
    def builders(self):
        from BTrees.IFBTree import IFBTree
        from BTrees.IFBTree import IFBucket
        from BTrees.IFBTree import IFTreeSet
        from BTrees.IFBTree import IFSet
        return IFSet, IFTreeSet, makeBuilder(IFBTree), makeBuilder(IFBucket)


class IFBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IFBTree import IFBTree
        return IFBTree


class IFBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IFBTree import IFBucket
        return IFBucket


class IFTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IFBTree import IFTreeSet
        return IFTreeSet


class IFSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IFBTree import IFSet
        return IFSet


class IFModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'IF'

    def _getModule(self):
        import BTrees
        return BTrees.IFBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IIntegerFloatBTreeModule

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(IFBTreeInternalKeyTest),
        unittest.makeSuite(IFTreeSetInternalKeyTest),
        unittest.makeSuite(IFBucketTest),
        unittest.makeSuite(IFTreeSetTest),
        unittest.makeSuite(IFSetTest),
        unittest.makeSuite(IFModuleTest),
        unittest.makeSuite(IFBTreeTest),
        unittest.makeSuite(TestIFBTrees),
        unittest.makeSuite(TestIFMultiUnion),
        unittest.makeSuite(PureIF),
        unittest.makeSuite(IFBTreeConflictTests),
        unittest.makeSuite(IFBucketConflictTests),
        unittest.makeSuite(IFTreeSetConflictTests),
        unittest.makeSuite(IFSetConflictTests),
    ))
