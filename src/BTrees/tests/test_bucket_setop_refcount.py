##############################################################################
#
# Copyright (c) 2026 Zope Foundation and Contributors.
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
"""
Regression test for a reference leak in the C implementation of the
Bucket ``-``, ``|`` and ``&`` operators.

``bucket_sub``, ``bucket_or`` and ``bucket_and`` (in
``BTrees/BucketTemplate.c``) each build a fresh two element argument
tuple with ``Py_BuildValue("OO", self, other)`` and hand it to a
module level helper, but never release their own reference to that
tuple afterwards. Because the tuple holds strong references to both
operands, every call to one of these operators used to leak a
reference to ``self`` and ``other``, keeping both objects alive
forever and inflating their reference counts without bound.

This only exercises the C extension: the pure Python implementation
builds no such tuple, so there's nothing to regress there.
"""
import sys
import unittest

from BTrees._compat import PYPY
from BTrees.tests.common import skipOnPurePython


@skipOnPurePython
@unittest.skipIf(PYPY, "Reference counts are not deterministic on PyPy")
class BucketSetOpRefCountTests(unittest.TestCase):

    def _check_module(self, mod):
        Bucket = mod.Bucket
        # Plain integer keys/values so the same data works for the
        # object, integer and float bucket families alike.
        a = Bucket({1: 10, 2: 20})
        b = Bucket({2: 20, 3: 30})

        for op in (
            lambda x, y: x - y,
            lambda x, y: x | y,
            lambda x, y: x & y,
        ):
            before_a = sys.getrefcount(a)
            before_b = sys.getrefcount(b)
            for _ in range(1000):
                op(a, b)
            self.assertEqual(sys.getrefcount(a), before_a)
            self.assertEqual(sys.getrefcount(b), before_b)

    def test_OOBTree(self):
        from BTrees import OOBTree
        self._check_module(OOBTree)

    def test_IIBTree(self):
        from BTrees import IIBTree
        self._check_module(IIBTree)

    def test_IOBTree(self):
        from BTrees import IOBTree
        self._check_module(IOBTree)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
