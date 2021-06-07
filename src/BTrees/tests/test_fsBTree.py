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

from BTrees import fsBTree
from ._test_builder import update_module

class fsBucketTests(unittest.TestCase):

    def _getTargetClass(self):
        return fsBTree.fsBucket

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



class fsBucketPyTests(fsBucketTests):

    def _getTargetClass(self):
        return fsBTree.fsBucketPy

class fsTreeTests(unittest.TestCase):

    def _check_sizes(self, cls):
        self.assertEqual(cls.max_leaf_size, 500)
        self.assertEqual(cls.max_internal_size, 500)

    def test_BTree_sizes(self):
        self._check_sizes(fsBTree.BTree)
        self._check_sizes(fsBTree.BTreePy)

    def test_TreeSet_sizes(self):
        self._check_sizes(fsBTree.TreeSet)
        self._check_sizes(fsBTree.TreeSetPy)

update_module(globals(), fsBTree)
