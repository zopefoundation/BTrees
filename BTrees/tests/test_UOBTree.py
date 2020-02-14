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

from .common import UnsignedKeysBTreeTests as BTreeTests
from .common import UnsignedExtendedSetTests as ExtendedSetTests
from .common import I_SetsBase
from .common import InternalKeysMappingTest
from .common import UnsignedKeysMappingBase as MappingBase
from .common import UnsignedKeysMappingConflictTestBase as MappingConflictTestBase
from .common import ModuleTest
from .common import MultiUnion
from .common import UnsignedNormalSetTests as NormalSetTests
from .common import UnsignedSetConflictTestBase as SetConflictTestBase
from .common import SetResult
from .common import TypeTest
from .common import TestLongIntKeys
from .common import makeBuilder
from .common import UnsignedKeysMixin
from .common import UnsignedError


# pylint:disable=no-name-in-module,arguments-differ

class UOBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UOBTree import UOBTree
        return UOBTree


class UOBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UOBTree import UOBTreePy
        return UOBTreePy


class UOBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UOBTree import UOBucket
        return UOBucket


class UOBucketPyTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UOBTree import UOBucketPy
        return UOBucketPy


class UOTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UOBTree import UOTreeSet
        return UOTreeSet


class UOTreeSetPyTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UOBTree import UOTreeSetPy
        return UOTreeSetPy


class UOSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UOBTree import UOSet
        return UOSet


class UOSetPyTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UOBTree import UOSetPy
        return UOSetPy


class UOBTreeTest(BTreeTests, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UOBTree import UOBTree
        return UOBTree()


class UOBTreePyTest(BTreeTests, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UOBTree import UOBTreePy
        return UOBTreePy()


class _TestUOBTreesBase(TypeTest):

    def _stringraises(self):
        self._makeOne()['c'] = 1

    def _floatraises(self):
        self._makeOne()[2.5] = 1

    def _noneraises(self):
        self._makeOne()[None] = 1

    def testStringAllowedInContains(self):
        self.assertFalse('key' in self._makeOne())

    def testStringKeyRaisesKeyErrorWhenMissing(self):
        self.assertRaises(KeyError, self._makeOne().__getitem__, 'key')

    def testStringKeyReturnsDefaultFromGetWhenMissing(self):
        self.assertEqual(self._makeOne().get('key', 42), 42)

class TestUOBTrees(_TestUOBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UOBTree import UOBTree
        return UOBTree()


class TestUOBTreesPy(_TestUOBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UOBTree import UOBTreePy
        return UOBTreePy()


class TestUOSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UOBTree import UOSet
        return UOSet()


class TestUOSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UOBTree import UOSetPy
        return UOSetPy()


class TestUOTreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UOBTree import UOTreeSet
        return UOTreeSet()


class TestUOTreeSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UOBTree import UOTreeSetPy
        return UOTreeSetPy()


class PureUO(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.UOBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.UOBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.UOBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.UOBTree import UOBTree
        from BTrees.UOBTree import UOBucket
        from BTrees.UOBTree import UOTreeSet
        from BTrees.UOBTree import UOSet
        return UOSet, UOTreeSet, makeBuilder(UOBTree), makeBuilder(UOBucket)


class PureUOPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.UOBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.UOBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.UOBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.UOBTree import UOBTreePy
        from BTrees.UOBTree import UOBucketPy
        from BTrees.UOBTree import UOTreeSetPy
        from BTrees.UOBTree import UOSetPy
        return (UOSetPy, UOTreeSetPy,
                makeBuilder(UOBTreePy), makeBuilder(UOBucketPy))


class TestUOMultiUnion(UnsignedKeysMixin, MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.UOBTree import multiunion
        return multiunion(*args)

    def union(self, *args):
        from BTrees.UOBTree import union
        return union(*args)

    def mkset(self, *args):
        from BTrees.UOBTree import UOSet as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.UOBTree import UOTreeSet as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.UOBTree import UOBucket as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.UOBTree import UOBTree as mkbtree
        return mkbtree(*args)


class TestUOMultiUnionPy(UnsignedKeysMixin, MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.UOBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.UOBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.UOBTree import UOSetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.UOBTree import UOTreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.UOBTree import UOBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.UOBTree import UOBTreePy as mkbtree
        return mkbtree(*args)


class UOBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UOBTree import UOBTree
        return UOBTree


class UOBTreeConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UOBTree import UOBTreePy
        return UOBTreePy


class UOBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UOBTree import UOBucket
        return UOBucket


class UOBucketConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UOBTree import UOBucketPy
        return UOBucketPy


class UOTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UOBTree import UOTreeSet
        return UOTreeSet


class UOTreeSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UOBTree import UOTreeSetPy
        return UOTreeSetPy


class UOSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UOBTree import UOSet
        return UOSet


class UOSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UOBTree import UOSetPy
        return UOSetPy


class UOModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'UO'

    def _getModule(self):
        import BTrees
        return BTrees.UOBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IUnsignedObjectBTreeModule

    def test_weightedUnion_not_present(self):
        try:
            from BTrees.UOBTree import weightedUnion
        except ImportError:
            pass
        else:
            self.fail("UOBTree shouldn't have weightedUnion")

    def test_weightedIntersection_not_present(self):
        try:
            from BTrees.UOBTree import weightedIntersection
        except ImportError:
            pass
        else:
            self.fail("UOBTree shouldn't have weightedIntersection")
