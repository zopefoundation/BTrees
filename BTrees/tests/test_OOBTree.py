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
from .common import NormalSetTests
from .common import SetResult
from .common import makeBuilder


class OOBTreeInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OOBTree import OOBTreePy
        return OOBTreePy

class OOBTreePyInternalKeyTest(InternalKeysMappingTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OOBTree import OOBTree
        return OOBTree


class OOTreeSetInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OOBTree import OOTreeSet
        return OOTreeSet


class OOTreeSetPyInternalKeyTest(InternalKeysSetTest, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OOBTree import OOTreeSetPy
        return OOTreeSetPy


class OOBucketTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OOBTree import OOBucket
        return OOBucket


class OOBucketPyTest(MappingBase, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OOBTree import OOBucketPy
        return OOBucketPy


class OOTreeSetTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OOBTree import OOTreeSet
        return OOTreeSet


class OOTreeSetPyTest(NormalSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OOBTree import OOTreeSetPy
        return OOTreeSetPy


class OOSetTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OOBTree import OOSet
        return OOSet


class OOSetPyTest(ExtendedSetTests, unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.OOBTree import OOSetPy
        return OOSetPy



class OOBTreeTest(BTreeTests, unittest.TestCase):

    def _makeOne(self):
        from BTrees.OOBTree import OOBTree
        return OOBTree()

    def testRejectDefaultComparison(self):
        # Check that passing int keys w default comparison fails.
        # Only applies to new-style class instances. Old-style
        # instances are too hard to introspect.

        # This is white box because we know that the check is being
        # used in a function that's used in lots of places.
        # Otherwise, there are many permutations that would have to be
        # checked.
        t = self._makeOne()

        class C(object):
            pass

        self.assertRaises(TypeError, lambda : t.__setitem__(C(), 1))

        class C(object):
            def __cmp__(*args):
                return 1

        c = C()
        t[c] = 1

        t.clear()

        class C(object):
            def __lt__(*args):
                return 1

        c = C()
        t[c] = 1

        t.clear()


#class OOBTreePyTest(OOBTreeTest):
#
# Right now, we can't match the C extension's test / prohibition of the
# default 'object' comparison semantics.
class OOBTreePyTest(BTreeTests, unittest.TestCase):

    def _makeOne(self):
        from BTrees.OOBTree import OOBTreePy
        return OOBTreePy()


class OOModuleTest(ModuleTest, unittest.TestCase):

    prefix = 'OO'

    def _getModule(self):
        import BTrees
        return BTrees.OOBTree

    def _getInterface(self):
        import BTrees.Interfaces
        return BTrees.Interfaces.IObjectObjectBTreeModule


class PureOO(SetResult, unittest.TestCase):
    def union(self, *args):
        from BTrees.OOBTree import union
        return union(*args)
    def intersection(self, *args):
        from BTrees.OOBTree import intersection
        return intersection(*args)
    def difference(self, *args):
        from BTrees.OOBTree import difference
        return difference(*args)
    def builders(self):
        from BTrees.OOBTree import OOBTree
        from BTrees.OOBTree import OOBucket
        from BTrees.OOBTree import OOTreeSet
        from BTrees.OOBTree import OOSet
        return OOSet, OOTreeSet, makeBuilder(OOBTree), makeBuilder(OOBucket)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(OOBTreeInternalKeyTest),
        unittest.makeSuite(OOBTreePyInternalKeyTest),
        unittest.makeSuite(OOTreeSetInternalKeyTest),
        unittest.makeSuite(OOTreeSetPyInternalKeyTest),
        unittest.makeSuite(OOBucketTest),
        unittest.makeSuite(OOBucketPyTest),
        unittest.makeSuite(OOTreeSetTest),
        unittest.makeSuite(OOTreeSetPyTest),
        unittest.makeSuite(OOSetTest),
        unittest.makeSuite(OOSetPyTest),
        unittest.makeSuite(OOModuleTest),
        unittest.makeSuite(OOBTreeTest),
        unittest.makeSuite(OOBTreePyTest),
        unittest.makeSuite(OOModuleTest),

        unittest.makeSuite(PureOO),
    ))
