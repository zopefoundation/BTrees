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
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test errors during comparison of BTree keys."""

import unittest


STR = "A string with hi-bit-set characters: \700\701"
UNICODE = u"A unicode string"


class CompareTest(unittest.TestCase):

    def setUp(self):
        # These defaults only make sense if the default encoding
        # prevents STR from being promoted to Unicode.
        self.assertRaises(UnicodeError, unicode, STR)

    def _makeBucket(self):
        from BTrees.OOBTree import OOBucket
        return OOBucket()

    def _makeSet(self):
        from BTrees.OOBTree import OOSet
        return OOSet()

    def assertUE(self, callable, *args):
        self.assertRaises(UnicodeError, callable, *args)

    def testBucketGet(self):
        import warnings
        b = self._makeBucket()
        with warnings.catch_warnings(True) as _warnlog:
            b[STR] = 1
            self.assertUE(b.get, UNICODE)
        self.assertEqual(len(_warnlog), 1)

    def testSetGet(self):
        s = self._makeSet()
        s.insert(STR)
        self.assertUE(s.remove, UNICODE)

    def testBucketSet(self):
        b = self._makeBucket()
        b[STR] = 1
        self.assertUE(b.__setitem__, UNICODE, 1)

    def testSetSet(self):
        s = self._makeSet()
        s.insert(STR)
        self.assertUE(s.insert, UNICODE)

    def testBucketMinKey(self):
        b = self._makeBucket()
        b[STR] = 1
        self.assertUE(b.minKey, UNICODE)

    def testSetMinKey(self):
        s = self._makeSet()
        s.insert(STR)
        self.assertUE(s.minKey, UNICODE)

def test_suite():
    return unittest.makeSuite(CompareTest)
