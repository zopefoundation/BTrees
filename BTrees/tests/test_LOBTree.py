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
    ))
