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
to_2_bytes = _datatypes.f()
to_6_bytes = _datatypes.s()

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
        self.assertRaises(TypeError, to_int, 2**64)

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
        self.assertRaises(TypeError, to_long, 2**64)

    def test_to_long_w_invalid(self):
        self.assertRaises(TypeError, to_long, ())

    def test_to_2_bytes_w_ok(self):
        self.assertEqual(to_2_bytes(b'ab'), b'ab')

    def test_to_2_bytes_w_invalid_length(self):
        self.assertRaises(TypeError, to_2_bytes, b'a')
        self.assertRaises(TypeError, to_2_bytes, b'abcd')

    def test_to_6_bytes_w_ok(self):
        self.assertEqual(to_6_bytes(b'abcdef'), b'abcdef')

    def test_to_6_bytes_w_invalid_length(self):
        self.assertRaises(TypeError, to_6_bytes, b'a')
        self.assertRaises(TypeError, to_6_bytes, b'abcd')

    def test_coerce_to_6_bytes(self):
        # correct input is passed through
        self.assertEqual(to_6_bytes.coerce(b'abcdef'), b'abcdef')

        # small positive integers are converted
        self.assertEqual(to_6_bytes.coerce(1), b'\x00\x00\x00\x00\x00\x01')

        # negative values are disallowed
        self.assertRaises(TypeError, to_6_bytes.coerce, -1)

        # values outside the bigger than 64-bits are disallowed
        self.assertRaises(TypeError, to_6_bytes.coerce, 2 ** 64 + 1)
