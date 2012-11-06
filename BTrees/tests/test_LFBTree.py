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


class LFBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFBTree
        return LFBTree


class LFTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFTreeSet
        return LFTreeSet


class LFBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFBucket
        return LFBucket


class LFTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFTreeSet
        return LFTreeSet


class LFSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LFBTree import LFSet
        return LFSet


class LFModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'LF'

    def _getModule(self):
        import BTrees
        return BTrees.LFBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IIntegerFloatBTreeModule


class LFBTreeTest(BTreeTests, TestLongIntKeys, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LFBTree import LFBTree
        return LFBTree()

    def getTwoValues(self):
        return 0.5, 1.5


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(LFBTreeInternalKeyTest),
        unittest.makeSuite(LFTreeSetInternalKeyTest),
        unittest.makeSuite(LFBucketTest),
        unittest.makeSuite(LFTreeSetTest),
        unittest.makeSuite(LFSetTest),
        unittest.makeSuite(LFModuleTest),
        unittest.makeSuite(LFBTreeTest),
    ))
