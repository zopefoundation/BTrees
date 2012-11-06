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


class LLBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLBTree
        return LLBTree


class LLTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLTreeSet
        return LLTreeSet


class LLBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLBucket
        return LLBucket


class LLTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLTreeSet
        return LLTreeSet


class LLSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLSet
        return LLSet


class LLSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.LLBTree import LLSet
        return LLSet


class LLModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'LL'

    def _getModule(self):
        import BTrees
        return BTrees.LLBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IIntegerIntegerBTreeModule


class LLBTreeTest(BTreeTests, TestLongIntKeys, TestLongIntValues,
                  unittest.TestCase):

    def _makeOne(self):
        from BTrees.LLBTree import LLBTree
        return LLBTree()
    def getTwoValues(self):
        return 1, 2


class TestLLSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LLBTree import LLSet
        return LLSet()


class TestLLTreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.LLBTree import LLTreeSet
        return LLTreeSet()


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(LLBTreeInternalKeyTest),
        unittest.makeSuite(LLTreeSetInternalKeyTest),
        unittest.makeSuite(LLBucketTest),
        unittest.makeSuite(LLTreeSetTest),
        unittest.makeSuite(LLSetTest),
        unittest.makeSuite(LLModuleTest),
        unittest.makeSuite(LLBTreeTest),
        unittest.makeSuite(TestLLSets),
        unittest.makeSuite(TestLLTreeSets),
    ))
