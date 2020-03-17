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
from BTrees import _datatypes

to_ob = _datatypes.Any()
to_int = _datatypes.I()
to_float = _datatypes.F()
to_long = _datatypes.L()
to_bytes = _datatypes.Bytes

class TestDatatypes(unittest.TestCase):
    def test_to_ob(self):
        for thing in "abc", 0, 1.3, (), frozenset((1, 2)), object():
            self.assertTrue(to_ob(thing) is thing)

    def test_to_int_w_int(self):
        self.assertEqual(to_int(3), 3)

    def test_to_int_w_long_in_range(self):
        try:
            self.assertEqual(to_int(long(3)), 3)
        except NameError: #Python3
            pass

    def test_to_int_w_overflow(self):
        self.assertRaises(OverflowError, to_int, 2**64)

    def test_to_int_w_invalid(self):
        self.assertRaises(TypeError, to_int, ())

    def test_to_float_w_float(self):
        self.assertEqual(to_float(3.14159), 3.14159)

    def test_to_float_w_int(self):
        self.assertEqual(to_float(3), 3.0)

    def test_to_float_w_invalid(self):
        self.assertRaises(TypeError, to_float, ())

    def test_to_long_w_int(self):
        self.assertEqual(to_long(3), 3)

    def test_to_long_w_long_in_range(self):
        try:
            self.assertEqual(to_long(long(3)), 3)
        except NameError: #Python3
            pass

    def test_to_long_w_overflow(self):
        self.assertRaises(OverflowError, to_long, 2**64)

    def test_to_long_w_invalid(self):
        self.assertRaises(TypeError, to_long, ())

    def test_to_bytes_w_ok(self):
        conv = to_bytes(3)
        self.assertEqual(conv(b'abc'), b'abc')

    def test_to_bytes_w_invalid_length(self):
        conv = to_bytes(3)
        self.assertRaises(TypeError, conv, b'ab')
        self.assertRaises(TypeError, conv, b'abcd')
