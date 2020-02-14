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
from .common import TestLongIntKeys
from .common import makeBuilder
from .common import UnsignedKeysMixin

# pylint:disable=no-name-in-module,arguments-differ

class QOBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QOBTree import QOBTree
        return QOBTree


class QOBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QOBTree import QOBTreePy
        return QOBTreePy


class QOBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QOBTree import QOBucket
        return QOBucket


class QOBucketPyTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QOBTree import QOBucketPy
        return QOBucketPy


class QOTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QOBTree import QOTreeSet
        return QOTreeSet


class QOTreeSetPyTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QOBTree import QOTreeSetPy
        return QOTreeSetPy


class QOSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QOBTree import QOSet
        return QOSet


class QOSetPyTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QOBTree import QOSetPy
        return QOSetPy


class QOBTreeTest(BTreeTests, TestLongIntKeys, unittest.TestCase):

    def _makeOne(self):
        from BTrees.QOBTree import QOBTree
        return QOBTree()


class QOBTreePyTest(BTreeTests, TestLongIntKeys, unittest.TestCase):

    def _makeOne(self):
        from BTrees.QOBTree import QOBTreePy
        return QOBTreePy()


class TestQOSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.QOBTree import QOSet
        return QOSet()


class TestQOSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.QOBTree import QOSetPy
        return QOSetPy()


class TestQOTreeSets(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.QOBTree import QOTreeSet
        return QOTreeSet()


class TestQOTreeSetsPy(I_SetsBase, unittest.TestCase):

    def _makeOne(self):
        from BTrees.QOBTree import QOTreeSetPy
        return QOTreeSetPy()


class TestQOMultiUnion(UnsignedKeysMixin, MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.QOBTree import multiunion
        return multiunion(*args)

    def union(self, *args):
        from BTrees.QOBTree import union
        return union(*args)

    def mkset(self, *args):
        from BTrees.QOBTree import QOSet as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.QOBTree import QOTreeSet as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.QOBTree import QOBucket as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.QOBTree import QOBTree as mkbtree
        return mkbtree(*args)


class TestQOMultiUnionPy(UnsignedKeysMixin, MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.QOBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.QOBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.QOBTree import QOSetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.QOBTree import QOTreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.QOBTree import QOBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.QOBTree import QOBTreePy as mkbtree
        return mkbtree(*args)


class PureQO(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.QOBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.QOBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.QOBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.QOBTree import QOBTree
        from BTrees.QOBTree import QOBucket
        from BTrees.QOBTree import QOTreeSet
        from BTrees.QOBTree import QOSet
        return QOSet, QOTreeSet, makeBuilder(QOBTree), makeBuilder(QOBucket)


class PureQOPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.QOBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.QOBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.QOBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.QOBTree import QOBTreePy
        from BTrees.QOBTree import QOBucketPy
        from BTrees.QOBTree import QOTreeSetPy
        from BTrees.QOBTree import QOSetPy
        return (QOSetPy, QOTreeSetPy,
                makeBuilder(QOBTreePy), makeBuilder(QOBucketPy))


class QOBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QOBTree import QOBTree
        return QOBTree


class QOBTreeConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QOBTree import QOBTreePy
        return QOBTreePy


class QOBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QOBTree import QOBucket
        return QOBucket


class QOBucketConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QOBTree import QOBucketPy
        return QOBucketPy


class QOTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QOBTree import QOTreeSet
        return QOTreeSet


class QOTreeSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QOBTree import QOTreeSetPy
        return QOTreeSetPy


class QOSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QOBTree import QOSet
        return QOSet


class QOSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QOBTree import QOSetPy
        return QOSetPy


class QOModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'QO'

    def _getModule(self):
        import BTrees
        return BTrees.QOBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IUnsignedObjectBTreeModule

    def test_weightedUnion_not_present(self):
        try:
            from BTrees.QOBTree import weightedUnion
        except ImportError:
            pass
        else:
            self.fail("QOBTree shouldn't have weightedUnion")

    def test_weightedIntersection_not_present(self):
        try:
            from BTrees.QOBTree import weightedIntersection
        except ImportError:
            pass
        else:
            self.fail("QOBTree shouldn't have weightedIntersection")
