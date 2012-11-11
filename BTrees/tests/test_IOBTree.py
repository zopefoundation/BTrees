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
from .common import I_SetsBase
from .common import InternalKeysMappingTest
from .common import InternalKeysSetTest
from .common import MappingBase
from .common import ModuleTest
from .common import MultiUnion
from .common import NormalSetTests
from .common import SetResult
from .common import TypeTest
from .common import TestLongIntKeys
from .common import makeBuilder
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

class PureIO(SetResult, unittest.TestCase):
    def union(self, *args):
        from BTrees.IOBTree import union
        return union(*args)
    def intersection(self, *args):
        from BTrees.IOBTree import intersection
        return intersection(*args)
    def difference(self, *args):
        from BTrees.IOBTree import difference
        return difference(*args)
    def builders(self):
        from BTrees.IOBTree import IOBTree
        from BTrees.IOBTree import IOBucket
        from BTrees.IOBTree import IOTreeSet
        from BTrees.IOBTree import IOSet
        return IOSet, IOTreeSet, makeBuilder(IOBTree), makeBuilder(IOBucket)

class TestIOMultiUnion(MultiUnion, unittest.TestCase):
    def multiunion(self, *args):
        from BTrees.IOBTree import multiunion
        return multiunion(*args)
    def union(self, *args):
        from BTrees.IOBTree import union
        return union(*args)
    def mkset(self, *args):
        from BTrees.IOBTree import IOSet as mkset
        return mkset(*args)
    def mktreeset(self, *args):
        from BTrees.IOBTree import IOTreeSet as mktreeset
        return mktreeset(*args)
    def mkbucket(self, *args):
        from BTrees.IOBTree import IOBucket as mkbucket
        return mkbucket(*args)
    def mkbtree(self, *args):
        from BTrees.IOBTree import IOBTree as mkbtree
        return mkbtree(*args)


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
        unittest.makeSuite(TestIOMultiUnion),
        unittest.makeSuite(PureIO),
    ))
