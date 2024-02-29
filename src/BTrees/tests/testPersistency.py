##############################################################################
#
# Copyright (c) 2020 Zope Foundation and Contributors.
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

from unittest import TestCase

from ..OOBTree import OOBTree
from .common import ZODBAccess
from .common import _skip_wo_ZODB


BUCKET_SIZE = OOBTree.max_leaf_size


class TestPersistency(ZODBAccess, TestCase):
    @_skip_wo_ZODB
    def test_empty_bucket_persistency(self):
        from transaction import commit
        root = self._getRoot()
        try:
            # tree with 3 buckets (internal implementation details)
            tree = OOBTree(
                {i: i for i in range(3 * BUCKET_SIZE // 2 + 2)})
            root["tree"] = tree
            commit()
            # almost clear the second bucket keeping the last element
            for i in range(BUCKET_SIZE // 2, BUCKET_SIZE - 1):
                del tree[i]
            commit()
            del tree[BUCKET_SIZE - 1]  # remove the last element
            commit()
            tree._check()
            tree._p_deactivate()
            tree._check()  # fails in case of bad persistency
        finally:
            self._closeRoot(root)
