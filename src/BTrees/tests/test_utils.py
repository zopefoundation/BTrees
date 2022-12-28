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


class Test_non_negative(unittest.TestCase):

    def _callFUT(self, int_val):
        from BTrees.utils import non_negative
        return non_negative(int_val)

    def test_w_big_negative(self):
        self.assertEqual(self._callFUT(-(2**63 - 1)), 1)

    def test_w_negative(self):
        self.assertEqual(self._callFUT(-1), 2**63 - 1)

    def test_w_zero(self):
        self.assertEqual(self._callFUT(0), 0)

    def test_w_positive(self):
        self.assertEqual(self._callFUT(1), 1)


class Test_oid_repr(unittest.TestCase):

    def _callFUT(self, oid):
        from BTrees.utils import oid_repr
        return oid_repr(oid)

    def test_w_non_strings(self):
        self.assertEqual(self._callFUT(None), repr(None))
        self.assertEqual(self._callFUT(()), repr(()))
        self.assertEqual(self._callFUT([]), repr([]))
        self.assertEqual(self._callFUT({}), repr({}))
        self.assertEqual(self._callFUT(0), repr(0))

    def test_w_short_strings(self):
        for length in range(8):
            faux = 'x' * length
            self.assertEqual(self._callFUT(faux), repr(faux))

    def test_w_long_strings(self):
        for length in range(9, 1024):
            faux = 'x' * length
            self.assertEqual(self._callFUT(faux), repr(faux))

    def test_w_zero(self):
        self.assertEqual(self._callFUT(b'\0\0\0\0\0\0\0\0'), b'0x00')

    def test_w_one(self):
        self.assertEqual(self._callFUT(b'\0\0\0\0\0\0\0\1'), b'0x01')

    def test_w_even_length(self):
        self.assertEqual(self._callFUT(b'\0\0\0\0\0\0\xAB\xC4'), b'0xabc4')

    def test_w_odd_length(self):
        self.assertEqual(self._callFUT(b'\0\0\0\0\0\0\x0D\xEF'), b'0x0def')
