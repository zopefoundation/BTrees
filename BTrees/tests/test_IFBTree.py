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

from BTrees.tests.common import BTreeTests
from BTrees.tests.common import ExtendedSetTests
from BTrees.tests.common import InternalKeysMappingTest
from BTrees.tests.common import InternalKeysSetTest
from BTrees.tests.common import MappingBase
from BTrees.tests.common import ModuleTest
from BTrees.tests.common import NormalSetTests
from BTrees.tests.common import TestLongIntKeys
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

class IFModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'IF'

    def _getModule(self):
        import BTrees
        return BTrees.IFBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IIntegerFloatBTreeModule


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
    ))
