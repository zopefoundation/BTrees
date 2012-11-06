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


class OLBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLBTree
        return OLBTree


class OLTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLTreeSet
        return OLTreeSet


class OLBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLBucket
        return OLBucket


class OLTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLTreeSet
        return OLTreeSet


class OLSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OLBTree import OLSet
        return OLSet


class OLModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'OL'

    def _getModule(self):
        import BTrees
        return BTrees.OLBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IObjectIntegerBTreeModule


class OLBTreeTest(BTreeTests, TestLongIntValues, unittest.TestCase):

    def _makeOne(self):
        from BTrees.OLBTree import OLBTree
        return OLBTree()

    def getTwoKeys(self):
        return object(), object()


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(OLBTreeInternalKeyTest),
        unittest.makeSuite(OLTreeSetInternalKeyTest),
        unittest.makeSuite(OLBucketTest),
        unittest.makeSuite(OLTreeSetTest),
        unittest.makeSuite(OLSetTest),
        unittest.makeSuite(OLModuleTest),
        unittest.makeSuite(OLBTreeTest),
    ))
