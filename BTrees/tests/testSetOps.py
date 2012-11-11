##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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

from .common import MultiUnion
from .common import SetResult
from .common import Weighted
from .common import itemsToSet
from .common import makeBuilder

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

class PureOI(SetResult, unittest.TestCase):
    def union(self, *args):
        from BTrees.OIBTree import union
        return union(*args)
    def intersection(self, *args):
        from BTrees.OIBTree import intersection
        return intersection(*args)
    def difference(self, *args):
        from BTrees.OIBTree import difference
        return difference(*args)
    def builders(self):
        from BTrees.OIBTree import OIBTree
        from BTrees.OIBTree import OIBucket
        from BTrees.OIBTree import OITreeSet
        from BTrees.OIBTree import OISet
        return OISet, OITreeSet, makeBuilder(OIBTree), makeBuilder(OIBucket)

class PureOL(SetResult, unittest.TestCase):
    def union(self, *args):
        from BTrees.OLBTree import union
        return union(*args)
    def intersection(self, *args):
        from BTrees.OLBTree import intersection
        return intersection(*args)
    def difference(self, *args):
        from BTrees.OLBTree import difference
        return difference(*args)
    def builders(self):
        from BTrees.OLBTree import OLBTree
        from BTrees.OLBTree import OLBucket
        from BTrees.OLBTree import OLTreeSet
        from BTrees.OLBTree import OLSet
        return OLSet, OLTreeSet, makeBuilder(OLBTree), makeBuilder(OLBucket)

# Check that various special module functions are and aren't imported from
# the expected BTree modules.
class TestImports(unittest.TestCase):
    def testWeightedUnion(self):
        from BTrees.IIBTree import weightedUnion
        from BTrees.OIBTree import weightedUnion

        try:
            from BTrees.IOBTree import weightedUnion
        except ImportError:
            pass
        else:
            self.fail("IOBTree shouldn't have weightedUnion")

        from BTrees.LLBTree import weightedUnion
        from BTrees.OLBTree import weightedUnion

        try:
            from BTrees.LOBTree import weightedUnion
        except ImportError:
            pass
        else:
            self.fail("LOBTree shouldn't have weightedUnion")

        try:
            from BTrees.OOBTree import weightedUnion
        except ImportError:
            pass
        else:
            self.fail("OOBTree shouldn't have weightedUnion")

    def testWeightedIntersection(self):
        from BTrees.IIBTree import weightedIntersection
        from BTrees.OIBTree import weightedIntersection

        try:
            from BTrees.IOBTree import weightedIntersection
        except ImportError:
            pass
        else:
            self.fail("IOBTree shouldn't have weightedIntersection")

        from BTrees.LLBTree import weightedIntersection
        from BTrees.OLBTree import weightedIntersection

        try:
            from BTrees.LOBTree import weightedIntersection
        except ImportError:
            pass
        else:
            self.fail("LOBTree shouldn't have weightedIntersection")

        try:
            from BTrees.OOBTree import weightedIntersection
        except ImportError:
            pass
        else:
            self.fail("OOBTree shouldn't have weightedIntersection")

    def testMultiunion(self):
        from BTrees.IIBTree import multiunion
        from BTrees.IOBTree import multiunion

        try:
            from BTrees.OIBTree import multiunion
        except ImportError:
            pass
        else:
            self.fail("OIBTree shouldn't have multiunion")

        from BTrees.LLBTree import multiunion
        from BTrees.LOBTree import multiunion

        try:
            from BTrees.OLBTree import multiunion
        except ImportError:
            pass
        else:
            self.fail("OLBTree shouldn't have multiunion")

        try:
            from BTrees.OOBTree import multiunion
        except ImportError:
            pass
        else:
            self.fail("OOBTree shouldn't have multiunion")

class TestWeightedOI(Weighted, unittest.TestCase):
    def weightedUnion(self):
        from BTrees.OIBTree import weightedUnion
        return weightedUnion
    def weightedIntersection(self):
        from BTrees.OIBTree import weightedIntersection
        return weightedIntersection
    def union(self):
        from BTrees.OIBTree import union
        return union
    def intersection(self):
        from BTrees.OIBTree import intersection
        return intersection
    def mkbucket(self, *args):
        from BTrees.OIBTree import OIBucket as mkbucket
        return mkbucket(*args)
    def builders(self):
        from BTrees.OIBTree import OIBTree
        from BTrees.OIBTree import OIBucket
        from BTrees.OIBTree import OITreeSet
        from BTrees.OIBTree import OISet
        return OIBucket, OIBTree, itemsToSet(OISet), itemsToSet(OITreeSet)

class TestWeightedOL(Weighted, unittest.TestCase):
    def weightedUnion(self):
        from BTrees.OLBTree import weightedUnion
        return weightedUnion
    def weightedIntersection(self):
        from BTrees.OLBTree import weightedIntersection
        return weightedIntersection
    def union(self):
        from BTrees.OLBTree import union
        return union
    def intersection(self):
        from BTrees.OLBTree import intersection
        return intersection
    def mkbucket(self, *args):
        from BTrees.OLBTree import OLBucket as mkbucket
        return mkbucket(*args)
    def builders(self):
        from BTrees.OLBTree import OLBTree
        from BTrees.OLBTree import OLBucket
        from BTrees.OLBTree import OLTreeSet
        from BTrees.OLBTree import OLSet
        return OLBucket, OLBTree, itemsToSet(OLSet), itemsToSet(OLTreeSet)


def test_suite():
    return unittest.TestSuite((

        unittest.makeSuite(PureOO),

        unittest.makeSuite(PureOI),
        unittest.makeSuite(TestWeightedOI),

        unittest.makeSuite(PureOL),
        unittest.makeSuite(TestWeightedOL),

        unittest.makeSuite(TestImports),
    ))
