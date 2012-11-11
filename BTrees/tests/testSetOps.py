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

class PureLL(SetResult, unittest.TestCase):
    def union(self, *args):
        from BTrees.LLBTree import union
        return union(*args)
    def intersection(self, *args):
        from BTrees.LLBTree import intersection
        return intersection(*args)
    def difference(self, *args):
        from BTrees.LLBTree import difference
        return difference(*args)
    def builders(self):
        from BTrees.LLBTree import LLBTree
        from BTrees.LLBTree import LLBucket
        from BTrees.LLBTree import LLTreeSet
        from BTrees.LLBTree import LLSet
        return LLSet, LLTreeSet, makeBuilder(LLBTree), makeBuilder(LLBucket)

class PureLO(SetResult, unittest.TestCase):
    def union(self, *args):
        from BTrees.LOBTree import union
        return union(*args)
    def intersection(self, *args):
        from BTrees.LOBTree import intersection
        return intersection(*args)
    def difference(self, *args):
        from BTrees.LOBTree import difference
        return difference(*args)
    def builders(self):
        from BTrees.LOBTree import LOBTree
        from BTrees.LOBTree import LOBucket
        from BTrees.LOBTree import LOTreeSet
        from BTrees.LOBTree import LOSet
        return LOSet, LOTreeSet, makeBuilder(LOBTree), makeBuilder(LOBucket)

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

class TestLLMultiUnion(MultiUnion, unittest.TestCase):
    def multiunion(self, *args):
        from BTrees.LLBTree import multiunion
        return multiunion(*args)
    def union(self, *args):
        from BTrees.LLBTree import union
        return union(*args)
    def mkset(self, *args):
        from BTrees.LLBTree import LLSet as mkset
        return mkset(*args)
    def mktreeset(self, *args):
        from BTrees.LLBTree import LLTreeSet as mktreeset
        return mktreeset(*args)
    def mkbucket(self, *args):
        from BTrees.LLBTree import LLBucket as mkbucket
        return mkbucket(*args)
    def mkbtree(self, *args):
        from BTrees.LLBTree import LLBTree as mkbtree
        return mkbtree(*args)

class TestLOMultiUnion(MultiUnion, unittest.TestCase):
    def multiunion(self, *args):
        from BTrees.LOBTree import multiunion
        return multiunion(*args)
    def union(self, *args):
        from BTrees.LOBTree import union
        return union(*args)
    def mkset(self, *args):
        from BTrees.LOBTree import LOSet as mkset
        return mkset(*args)
    def mktreeset(self, *args):
        from BTrees.LOBTree import LOTreeSet as mktreeset
        return mktreeset(*args)
    def mkbucket(self, *args):
        from BTrees.LOBTree import LOBucket as mkbucket
        return mkbucket(*args)
    def mkbtree(self, *args):
        from BTrees.LOBTree import LOBTree as mkbtree
        return mkbtree(*args)

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

class TestWeightedLL(Weighted, unittest.TestCase):
    def weightedUnion(self):
        from BTrees.LLBTree import weightedUnion
        return weightedUnion
    def weightedIntersection(self):
        from BTrees.LLBTree import weightedIntersection
        return weightedIntersection
    def union(self):
        from BTrees.LLBTree import union
        return union
    def intersection(self):
        from BTrees.LLBTree import intersection
        return intersection
    def mkbucket(self, *args):
        from BTrees.LLBTree import LLBucket as mkbucket
        return mkbucket(*args)
    def builders(self):
        from BTrees.LLBTree import LLBTree
        from BTrees.LLBTree import LLBucket
        from BTrees.LLBTree import LLTreeSet
        from BTrees.LLBTree import LLSet
        return LLBucket, LLBTree, itemsToSet(LLSet), itemsToSet(LLTreeSet)

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

        unittest.makeSuite(TestLLMultiUnion),
        unittest.makeSuite(PureLL),
        unittest.makeSuite(TestWeightedLL),

        unittest.makeSuite(TestLOMultiUnion),
        unittest.makeSuite(PureLO),

        unittest.makeSuite(TestLFMultiUnion),
        unittest.makeSuite(PureLF),

        unittest.makeSuite(PureOO),

        unittest.makeSuite(PureOI),
        unittest.makeSuite(TestWeightedOI),

        unittest.makeSuite(PureOL),
        unittest.makeSuite(TestWeightedOL),

        unittest.makeSuite(TestImports),
    ))
