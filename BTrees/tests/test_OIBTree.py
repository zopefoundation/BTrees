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
from BTrees.tests.common import TestLongIntValues
from BTrees.tests.common import TypeTest
from BTrees.IIBTree import using64bits #XXX Ugly, but necessary


class OIBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OIBTree import OIBTree
        return OIBTree


class OITreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OIBTree import OITreeSet
        return OITreeSet


class OIBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OIBTree import OIBucket
        return OIBucket


class OITreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OIBTree import OITreeSet
        return OITreeSet


class OISetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OIBTree import OISet
        return OISet


class OIModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'OI'

    def _getModule(self):
        import BTrees
        return BTrees.OIBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IObjectIntegerBTreeModule


class OIBTreeTest(BTreeTests, unittest.TestCase):

    def _makeOne(self):
        from BTrees.OIBTree import OIBTree
        return OIBTree()


class OIBTreeTest(BTreeTests, unittest.TestCase):
    def _makeOne(self):
        from BTrees.OIBTree import OIBTree
        return OIBTree()


if using64bits:

    class OIBTreeTest(BTreeTests, TestLongIntValues, unittest.TestCase):
        def _makeOne(self):
            from BTrees.OIBTree import OIBTree
            return OIBTree()
        def getTwoKeys(self):
            return object(), object()

class TestOIBTrees(TypeTest, unittest.TestCase):
    def _makeOne(self):
        from BTrees.OIBTree import OIBTree
        return OIBTree()

    def _stringraises(self):
        self._makeOne()[1] = 'c'

    def _floatraises(self):
        self._makeOne()[1] = 1.4

    def _noneraises(self):
        self._makeOne()[1] = None

    def testEmptyFirstBucketReportedByGuido(self):
        b = self._makeOne()
        for i in xrange(29972): # reduce to 29971 and it works
            b[i] = i
        for i in xrange(30): # reduce to 29 and it works
            del b[i]
            b[i+40000] = i

        self.assertEqual(b.keys()[0], 30)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(OIBTreeInternalKeyTest),
        unittest.makeSuite(OITreeSetInternalKeyTest),
        unittest.makeSuite(OIBucketTest),
        unittest.makeSuite(OITreeSetTest),
        unittest.makeSuite(OISetTest),
        unittest.makeSuite(OIModuleTest),
        unittest.makeSuite(OIBTreeTest),
        unittest.makeSuite(TestOIBTrees),
    ))
