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
from BTrees.tests.common import TypeTest
from BTrees.tests.common import TestLongIntKeys
from BTrees.IIBTree import using64bits #XXX Ugly, but unavoidable


class IOBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOBTree
        return IOBTree


class IOTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOTreeSet
        return IOTreeSet


class IOBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOBucket
        return IOBucket


class IOTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOTreeSet
        return IOTreeSet


class IOSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.IOBTree import IOSet
        return IOSet


class IOModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'IO'

    def _getModule(self):
        import BTrees
        return BTrees.IOBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IIntegerObjectBTreeModule


class IOBTreeTest(BTreeTests, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IOBTree import IOBTree
        return IOBTree()

if using64bits:

    class IOBTreeTest(BTreeTests, TestLongIntKeys, unittest.TestCase):
        def _makeOne(self):
            from BTrees.IOBTree import IOBTree
            return IOBTree()


class TestIOBTrees(TypeTest, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IOBTree import IOBTree
        return IOBTree()

    def _stringraises(self):
        self._makeOne()['c'] = 1

    def _floatraises(self):
        self._makeOne()[2.5] = 1

    def _noneraises(self):
        self._makeOne()[None] = 1


class TestIOSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IOBTree import IOSet
        return IOSet()


class TestIOTreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.IOBTree import IOTreeSet
        return IOTreeSet()


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(IOBTreeInternalKeyTest),
        unittest.makeSuite(IOTreeSetInternalKeyTest),
        unittest.makeSuite(IOBucketTest),
        unittest.makeSuite(IOTreeSetTest),
        unittest.makeSuite(IOSetTest),
        unittest.makeSuite(IOModuleTest),
        unittest.makeSuite(IOBTreeTest),
        unittest.makeSuite(TestIOBTrees),
        unittest.makeSuite(TestIOSets),
        unittest.makeSuite(TestIOTreeSets),
    ))
