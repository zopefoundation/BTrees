##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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


class fsBucketBase(object):

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def _makeBytesItems(self):
        from .._compat import _ascii
        return[(_ascii(c*2), _ascii(c*6)) for c in 'abcdef']

    def test_toString(self):
        bucket = self._makeOne(self._makeBytesItems())
        self.assertEqual(bucket.toString(),
                         b'aabbccddeeffaaaaaabbbbbbccccccddddddeeeeeeffffff')

    def test_fromString(self):
        before = self._makeOne(self._makeBytesItems())
        after = before.fromString(before.toString())
        self.assertEqual(before.__getstate__(), after.__getstate__())

    def test_fromString_empty(self):
        before = self._makeOne(self._makeBytesItems())
        after = before.fromString(b'')
        self.assertEqual(after.__getstate__(), ((),))

    def test_fromString_invalid_length(self):
        bucket = self._makeOne(self._makeBytesItems())
        self.assertRaises(ValueError, bucket.fromString, b'xxx')


class fsBucketTests(unittest.TestCase, fsBucketBase):

    def _getTargetClass(self):
        from BTrees.fsBTree import fsBucket
        return fsBucket


class fsBucketPyTests(unittest.TestCase, fsBucketBase):

    def _getTargetClass(self):
        from BTrees.fsBTree import fsBucketPy
        return fsBucketPy


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(fsBucketTests),
        unittest.makeSuite(fsBucketPyTests),
    ))
