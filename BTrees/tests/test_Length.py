##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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


_marker = object()

class LengthTestCase(unittest.TestCase):

    def _getTargetClass(self):
        from BTrees.Length import Length
        return Length

    def _makeOne(self, value=_marker):
        if value is _marker:
            return self._getTargetClass()()
        return self._getTargetClass()(value)

    def test_ctor_default(self):
        length = self._makeOne()
        self.assertEqual(length.value, 0)

    def test_ctor_explict(self):
        length = self._makeOne(42)
        self.assertEqual(length.value, 42)

    def test___getstate___(self):
        length = self._makeOne(42)
        self.assertEqual(length.__getstate__(), 42)

    def test___setstate__(self):
        length = self._makeOne()
        length.__setstate__(42)
        self.assertEqual(length.value, 42)

    def test_set(self):
        length = self._makeOne()
        length.set(42)
        self.assertEqual(length.value, 42)

    def test__p_resolveConflict(self):
        length = self._makeOne()
        self.assertEqual(length._p_resolveConflict(5, 7, 9), 11)

    def test_change_w_positive_delta(self):
        length = self._makeOne()
        length.change(3)
        self.assertEqual(length.value, 3)

    def test_change_w_negative_delta(self):
        length = self._makeOne()
        length.change(-3)
        self.assertEqual(length.value, -3)

    def test_change_overflows_to_long(self):
        import sys
        try:
            length = self._makeOne(sys.maxint)
        except AttributeError: #pragma NO COVER Py3k
            return
        else: #pragma NO COVER Py2
            self.assertEqual(length(), sys.maxint)
            self.assertTrue(type(length()) is int)
            length.change(+1)
            self.assertEqual(length(), sys.maxint + 1)
            self.assertTrue(type(length()) is long)

    def test_change_underflows_to_long(self):
        import sys
        try:
            minint = (-sys.maxint) - 1
        except AttributeError: #pragma NO COVER Py3k
            return
        else: #pragma NO COVER Py2
            length = self._makeOne(minint)
            self.assertEqual(length(), minint)
            self.assertTrue(type(length()) is int)
            length.change(-1)
            self.assertEqual(length(), minint - 1)
            self.assertTrue(type(length()) is long)

    def test___call___no_args(self):
        length = self._makeOne(42)
        self.assertEqual(length(), 42)

    def test___call___w_args(self):
        length = self._makeOne(42)
        self.assertEqual(length(0, None, (), [], {}), 42)

    def test_lp_516653(self):
        # Test for https://bugs.launchpad.net/zodb/+bug/516653
        import copy
        length = self._makeOne()
        other = copy.copy(length)
        self.assertEqual(other(), 0)


def test_suite():
    return unittest.makeSuite(LengthTestCase)
