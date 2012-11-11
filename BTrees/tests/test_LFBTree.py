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
from .common import ModuleTest
from .common import MultiUnion
from .common import NormalSetTests
from .common import SetResult
from .common import TestLongIntKeys
from .common import makeBuilder


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


class TestLFMultiUnion(MultiUnion, unittest.TestCase):
    def multiunion(self, *args):
        from BTrees.LFBTree import multiunion
        return multiunion(*args)
    def union(self, *args):
        from BTrees.LFBTree import union
        return union(*args)
    def mkset(self, *args):
        from BTrees.LFBTree import LFSet as mkset
        return mkset(*args)
    def mktreeset(self, *args):
        from BTrees.LFBTree import LFTreeSet as mktreeset
        return mktreeset(*args)
    def mkbucket(self, *args):
        from BTrees.LFBTree import LFBucket as mkbucket
        return mkbucket(*args)
    def mkbtree(self, *args):
        from BTrees.LFBTree import LFBTree as mkbtree
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


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(LFBTreeInternalKeyTest),
        unittest.makeSuite(LFTreeSetInternalKeyTest),
        unittest.makeSuite(LFBucketTest),
        unittest.makeSuite(LFTreeSetTest),
        unittest.makeSuite(LFSetTest),
        unittest.makeSuite(LFModuleTest),
        unittest.makeSuite(LFBTreeTest),

        unittest.makeSuite(TestLFMultiUnion),
        unittest.makeSuite(PureLF),
    ))
