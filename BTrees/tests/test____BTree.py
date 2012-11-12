##############################################################################
#
# Copyright 2012 Zope Foundation and Contributors.
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
import unittest


class _BucketBaseTests(unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.___BTree import _BucketBase
        return _BucketBase

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        bucket = self._makeOne()
        self.assertEqual(bucket._keys, [])
        self.assertEqual(bucket._next, None)
        self.assertEqual(bucket.size, 0)

    def test__deleteNextBucket_none(self):
        bucket = self._makeOne()
        bucket._deleteNextBucket() # no raise
        self.assertTrue(bucket._next is None)

    def test__deleteNextBucket_one(self):
        bucket1 = self._makeOne()
        bucket2 = bucket1._next = self._makeOne()
        bucket1._deleteNextBucket() # no raise
        self.assertTrue(bucket1._next is None)

    def test__deleteNextBucket_two(self):
        bucket1 = self._makeOne()
        bucket2 = bucket1._next = self._makeOne()
        bucket3 = bucket2._next = self._makeOne()
        bucket1._deleteNextBucket() # no raise
        self.assertTrue(bucket1._next is bucket3)

    def test__search_empty(self):
        bucket = self._makeOne()
        self.assertEqual(bucket._search('nonesuch'), -1)

    def test__search_nonempty_miss(self):
        bucket = self._makeOne()
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._search('candy'), -2)

    def test__search_nonempty_hit(self):
        bucket = self._makeOne()
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._search('charlie'), 2)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(_BucketBaseTests),
    ))
