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
from .common import InternalKeysSetTest
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

# pylint: disable=no-name-in-module,arguments-differ

class QFBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QFBTree import QFBTree
        return QFBTree


class QFBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QFBTree import QFBTreePy
        return QFBTreePy


class QFTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QFBTree import QFTreeSet
        return QFTreeSet


class QFTreeSetPyInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QFBTree import QFTreeSetPy
        return QFTreeSetPy


class QFBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QFBTree import QFBucket
        return QFBucket


class QFBucketPyTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QFBTree import QFBucketPy
        return QFBucketPy


class QFTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QFBTree import QFTreeSet
        return QFTreeSet


class QFTreeSetPyTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QFBTree import QFTreeSetPy
        return QFTreeSetPy


class QFSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QFBTree import QFSet
        return QFSet


class QFSetPyTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QFBTree import QFSetPy
        return QFSetPy


class QFBTreeTest(BTreeTests, TestLongIntKeys, unittest.TestCase):

    def _makeOne(self):
        from BTrees.QFBTree import QFBTree
        return QFBTree()

    def getTwoValues(self):
        return 0.5, 1.5


class QFBTreePyTest(BTreeTests, TestLongIntKeys, unittest.TestCase):

    def _makeOne(self):
        from BTrees.QFBTree import QFBTreePy
        return QFBTreePy()

    def getTwoValues(self):
        return 0.5, 1.5


class TestQFMultiUnion(UnsignedKeysMixin, MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.QFBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.QFBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.QFBTree import QFSetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.QFBTree import QFTreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.QFBTree import QFBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.QFBTree import QFBTreePy as mkbtree
        return mkbtree(*args)


class TestQFMultiUnionPy(UnsignedKeysMixin, MultiUnion, unittest.TestCase):

    def multiunion(self, *args):
        from BTrees.QFBTree import multiunionPy
        return multiunionPy(*args)

    def union(self, *args):
        from BTrees.QFBTree import unionPy
        return unionPy(*args)

    def mkset(self, *args):
        from BTrees.QFBTree import QFSetPy as mkset
        return mkset(*args)

    def mktreeset(self, *args):
        from BTrees.QFBTree import QFTreeSetPy as mktreeset
        return mktreeset(*args)

    def mkbucket(self, *args):
        from BTrees.QFBTree import QFBucketPy as mkbucket
        return mkbucket(*args)

    def mkbtree(self, *args):
        from BTrees.QFBTree import QFBTreePy as mkbtree
        return mkbtree(*args)


class PureQF(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.QFBTree import union
        return union(*args)

    def intersection(self, *args):
        from BTrees.QFBTree import intersection
        return intersection(*args)

    def difference(self, *args):
        from BTrees.QFBTree import difference
        return difference(*args)

    def builders(self):
        from BTrees.QFBTree import QFBTree
        from BTrees.QFBTree import QFBucket
        from BTrees.QFBTree import QFTreeSet
        from BTrees.QFBTree import QFSet
        return QFSet, QFTreeSet, makeBuilder(QFBTree), makeBuilder(QFBucket)


class PureQFPy(SetResult, unittest.TestCase):

    def union(self, *args):
        from BTrees.QFBTree import unionPy
        return unionPy(*args)

    def intersection(self, *args):
        from BTrees.QFBTree import intersectionPy
        return intersectionPy(*args)

    def difference(self, *args):
        from BTrees.QFBTree import differencePy
        return differencePy(*args)

    def builders(self):
        from BTrees.QFBTree import QFBTreePy
        from BTrees.QFBTree import QFBucketPy
        from BTrees.QFBTree import QFTreeSetPy
        from BTrees.QFBTree import QFSetPy
        return (QFSetPy, QFTreeSetPy,
                makeBuilder(QFBTreePy), makeBuilder(QFBucketPy))


class QFBTreeConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QFBTree import QFBTree
        return QFBTree


class QFBTreeConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QFBTree import QFBTreePy
        return QFBTreePy


class QFBucketConflictTests(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QFBTree import QFBucket
        return QFBucket


class QFBucketConflictTestsPy(MappingConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QFBTree import QFBucketPy
        return QFBucketPy


class QFTreeSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QFBTree import QFTreeSet
        return QFTreeSet


class QFTreeSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QFBTree import QFTreeSetPy
        return QFTreeSetPy


class QFSetConflictTests(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QFBTree import QFSet
        return QFSet


class QFSetConflictTestsPy(SetConflictTestBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.QFBTree import QFSetPy
        return QFSetPy


class QFModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'QF'

    def _getModule(self):
        import BTrees
        return BTrees.QFBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IUnsignedFloatBTreeModule


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(QFBTreeInternalKeyTest),
        unittest.makeSuite(QFBTreePyInternalKeyTest),
        unittest.makeSuite(QFTreeSetInternalKeyTest),
        unittest.makeSuite(QFTreeSetPyInternalKeyTest),
        unittest.makeSuite(QFBucketTest),
        unittest.makeSuite(QFBucketPyTest),
        unittest.makeSuite(QFTreeSetTest),
        unittest.makeSuite(QFTreeSetPyTest),
        unittest.makeSuite(QFSetTest),
        unittest.makeSuite(QFSetPyTest),
        unittest.makeSuite(QFBTreeTest),
        unittest.makeSuite(QFBTreePyTest),
        unittest.makeSuite(TestQFMultiUnion),
        unittest.makeSuite(TestQFMultiUnionPy),
        unittest.makeSuite(PureQF),
        unittest.makeSuite(PureQFPy),
        unittest.makeSuite(QFBTreeConflictTests),
        unittest.makeSuite(QFBTreeConflictTestsPy),
        unittest.makeSuite(QFBucketConflictTests),
        unittest.makeSuite(QFBucketConflictTestsPy),
        unittest.makeSuite(QFTreeSetConflictTests),
        unittest.makeSuite(QFTreeSetConflictTestsPy),
        unittest.makeSuite(QFSetConflictTests),
        unittest.makeSuite(QFSetConflictTestsPy),
        unittest.makeSuite(QFModuleTest),
    ))
