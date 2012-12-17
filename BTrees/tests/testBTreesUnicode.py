##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
from .common import _skip_under_Py3k

# When an OOBtree contains unicode strings as keys,
# it is neccessary accessing non-unicode strings are
# either ascii strings or encoded as unicoded using the
# corresponding encoding

encoding = 'ISO-8859-1'

class TestBTreesUnicode(unittest.TestCase):
    """ test unicode"""

    def setUp(self):
        #setup an OOBTree with some unicode strings
        from BTrees.OOBTree import OOBTree
        from BTrees._compat import _bytes
        from BTrees._compat import _u

        self.s = _u(b'dreit\xe4gigen', 'latin1')

        self.data = [(b'alien', 1),
                     (b'k\xf6nnten', 2),
                     (b'fox', 3),
                     (b'future', 4),
                     (b'quick', 5),
                     (b'zerst\xf6rt', 6),
                     (_u(b'dreit\xe4gigen','latin1'), 7),
                    ]

        self.tree = OOBTree()
        for k, v in self.data:
            if isinstance(k, _bytes):
                k = _u(k, 'latin1')
            self.tree[k] = v

    @_skip_under_Py3k
    def testAllKeys(self):
        # check every item of the tree
        from BTrees._compat import _u
        from BTrees._compat import _bytes
        for k, v in self.data:
            if isinstance(k, _bytes):
                k = _u(k, encoding)
            self.assertTrue(k in self.tree)
            self.assertEqual(self.tree[k], v)

    @_skip_under_Py3k
    def testUnicodeKeys(self):
        # try to access unicode keys in tree
        k, v = self.data[-1]
        self.assertEqual(k, self.s)
        self.assertEqual(self.tree[k], v)
        self.assertEqual(self.tree[self.s], v)

    @_skip_under_Py3k
    def testAsciiKeys(self):
        # try to access some "plain ASCII" keys in the tree
        for k, v in self.data[0], self.data[2]:
            self.assertTrue(isinstance(k, str))
            self.assertEqual(self.tree[k], v)

def test_suite():
    return unittest.makeSuite(TestBTreesUnicode)
