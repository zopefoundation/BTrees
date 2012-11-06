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
from BTrees.tests.common import I_SetsBase
from BTrees.tests.common import InternalKeysMappingTest
from BTrees.tests.common import InternalKeysSetTest
from BTrees.tests.common import MappingBase
from BTrees.tests.common import ModuleTest
from BTrees.tests.common import NormalSetTests
from BTrees.tests.common import TestLongIntKeys
from BTrees.tests.common import TestLongIntValues
from BTrees.IIBTree import using64bits #XXX Ugly, but unavoidable

 
class IIBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IIBTree
        return IIBTree


class IITreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IITreeSet
        return IITreeSet


class IIBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IIBucket
        return IIBucket


class IITreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IITreeSet
        return IITreeSet


class IISetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IIBTree import IISet
        return IISet


class IIModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'II'

    def _getModule(self):
        import BTrees
        return BTrees.IIBTree
    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IIntegerIntegerBTreeModule


class IIBTreeTest(BTreeTests, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IIBTree import IIBTree
        return IIBTree()

    def testIIBTreeOverflow(self):
        good = set()
        b = self._makeOne()

        def trial(i):
            i = int(i)
            try:
                b[i] = 0
            except TypeError:
                self.assertRaises(TypeError, b.__setitem__, 0, i)
            else:
                good.add(i)
                b[0] = i
                self.assertEqual(b[0], i)

        for i in range((1<<31) - 3, (1<<31) + 3):
            trial(i)
            trial(-i)

        del b[0]
        self.assertEqual(sorted(good), sorted(b))


if using64bits:

    class IIBTreeTest(BTreeTests, TestLongIntKeys, TestLongIntValues,
                      unittest.TestCase):
        def _makeOne(self):
            from BTrees.IIBTree import IIBTree
            return IIBTree()
        def getTwoValues(self):
            return 1, 2


class TestIIBTrees(unittest.TestCase):

    def _makeOne(self):
        from BTrees.IIBTree import IIBTree
        return IIBTree()

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


class TestIISets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IIBTree import IISet
        return IISet()


class TestIITreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IIBTree import IITreeSet
        return IITreeSet()



def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(IIBTreeInternalKeyTest),
        unittest.makeSuite(IITreeSetInternalKeyTest),
        unittest.makeSuite(IIBucketTest),
        unittest.makeSuite(IITreeSetTest),
        unittest.makeSuite(IISetTest),
        unittest.makeSuite(IIModuleTest),
        unittest.makeSuite(IIBTreeTest),
        unittest.makeSuite(TestIIBTrees),
        unittest.makeSuite(TestIISets),
        unittest.makeSuite(TestIITreeSets),
    ))
