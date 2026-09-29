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
Set and TreeSet in-place ``&=`` operator.

``set_iand`` (in ``BTrees/SetTemplate.c``) and ``TreeSet_iand`` (in
``BTrees/TreeSetTemplate.c``) each allocate a temporary list before
checking whether the right hand operand is iterable. When it isn't,
both functions used to return ``Py_NotImplemented`` directly, skipping
the ``err:`` cleanup label that would otherwise release that temporary
list. Every ``Set &= non_iterable`` or ``TreeSet &= non_iterable``
therefore leaked one empty list.

This only exercises the C extension: the pure Python implementation
never builds any such temporary list, so there's nothing to regress
there.
"""
import gc
import unittest

from BTrees._compat import PYPY
from BTrees.tests.common import skipOnPurePython


@skipOnPurePython
@unittest.skipIf(PYPY, "Reference counts are not deterministic on PyPy")
class SetAndTreeSetIAndRefCountTests(unittest.TestCase):

    def _count_empty_lists(self):
        gc.collect()
        return sum(
            1 for o in gc.get_objects()
            if type(o) is list and len(o) == 0
        )

    def _check(self, cls, member):
        s = cls([member])
        before = self._count_empty_lists()
        for _ in range(1000):
            # 42 is never iterable, which forces PyObject_GetIter() to
            # fail and the NotImplemented fallback path to run.
            try:
                s &= 42
            except TypeError:
                pass
        after = self._count_empty_lists()
        self.assertEqual(after, before)

    def test_OOSet(self):
        from BTrees.OOBTree import OOSet
        self._check(OOSet, 'a')

    def test_OOTreeSet(self):
        from BTrees.OOBTree import OOTreeSet
        self._check(OOTreeSet, 'a')

    def test_IISet(self):
        from BTrees.IIBTree import IISet
        self._check(IISet, 1)

    def test_IITreeSet(self):
        from BTrees.IIBTree import IITreeSet
        self._check(IITreeSet, 1)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
