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
from .common import InternalKeysMappingTest
from .common import UnsignedKeysMappingBase as MappingBase
from .common import UnsignedKeysMappingConflictTestBase as MappingConflictTestBase
from .common import ModuleTest
from .common import MultiUnion
from .common import UnsignedNormalSetTests as NormalSetTests
from .common import UnsignedSetConflictTestBase as SetConflictTestBase
from .common import SetResult
from .common import makeBuilder
from .common import UnsignedKeysMixin


# pylint:disable=no-name-in-module,arguments-differ

class UFBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UFBTree import UFBTree
        return UFBTree


class UFBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UFBTree import UFBTreePy
        return UFBTreePy


class UFBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UFBTree import UFBucket
        return UFBucket


class UFBucketPyTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UFBTree import UFBucketPy
        return UFBucketPy


class UFTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UFBTree import UFTreeSet
        return UFTreeSet


class UFTreeSetPyTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UFBTree import UFTreeSetPy
        return UFTreeSetPy


class UFSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UFBTree import UFSet
        return UFSet


class UFSetPyTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UFBTree import UFSetPy
        return UFSetPy


class UFBTreeTest(BTreeTests, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UFBTree import UFBTree
        return UFBTree()


class UFBTreePyTest(BTreeTests, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UFBTree import UFBTreePy
        return UFBTreePy()


class _TestUFBTreesBase(object):

    def testNonIntegerKeyRaises(self):
        self.assertRaises(TypeError, self._stringraiseskey)
        self.assertRaises(TypeError, self._floatraiseskey)
        self.assertRaises(TypeError, self._noneraiseskey)

    def testNonNumericValueRaises(self):
        self.assertRaises(TypeError, self._stringraisesvalue)
        self.assertRaises(TypeError, self._noneraisesvalue)
        self._makeOne()[1] = 1
        self._makeOne()[1] = 1.0

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


class TestUFBTrees(_TestUFBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UFBTree import UFBTree
        return UFBTree()


class TestUFBTreesPy(_TestUFBTreesBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.UFBTree import UFBTreePy
        return UFBTreePy()


class TestUFMultiUnion(UnsignedKeysMixin, MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.UFBTree import multiunion
        return multiunion(*args)

    def union(self, *args):
        from BTrees.UFBTree import union
        return union(*args)

    def mkset(self, *args):
        from BTrees.UFBTree import UFSet as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.UFBTree import UFTreeSet as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.UFBTree import UFBucket as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.UFBTree import UFBTree as mkbtree
        return mkbtree(*args)


class TestUFMultiUnionPy(UnsignedKeysMixin, MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.UFBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.UFBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.UFBTree import UFSetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.UFBTree import UFTreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.UFBTree import UFBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.UFBTree import UFBTreePy as mkbtree
        return mkbtree(*args)


class PureUF(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.UFBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.UFBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.UFBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.UFBTree import UFBTree
        from BTrees.UFBTree import UFBucket
        from BTrees.UFBTree import UFTreeSet
        from BTrees.UFBTree import UFSet
        return UFSet, UFTreeSet, makeBuilder(UFBTree), makeBuilder(UFBucket)


class PureUFPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.UFBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.UFBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.UFBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.UFBTree import UFBTreePy
        from BTrees.UFBTree import UFBucketPy
        from BTrees.UFBTree import UFTreeSetPy
        from BTrees.UFBTree import UFSetPy
        return (UFSetPy, UFTreeSetPy,
                makeBuilder(UFBTreePy), makeBuilder(UFBucketPy))


class UFBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UFBTree import UFBTree
        return UFBTree


class UFBTreePyConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UFBTree import UFBTreePy
        return UFBTreePy


class UFBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UFBTree import UFBucket
        return UFBucket


class UFBucketPyConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UFBTree import UFBucketPy
        return UFBucketPy


class UFTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UFBTree import UFTreeSet
        return UFTreeSet


class UFTreeSetPyConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UFBTree import UFTreeSetPy
        return UFTreeSetPy


class UFSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UFBTree import UFSet
        return UFSet


class UFSetPyConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.UFBTree import UFSetPy
        return UFSetPy


class UFModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'UF'

    def _getModule(self):
        import BTrees
        return BTrees.UFBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IUnsignedFloatBTreeModule
