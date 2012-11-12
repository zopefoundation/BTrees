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



class Test_BucketBase(unittest.TestCase):

    def _getTargetClass(self):
        from .._base import _BucketBase
        return _BucketBase

    def assertRaises(self, e_type, checked, *args, **kw):
        try:
            checked(*args, **kw)
        except e_type as e:
            return e
        self.fail("Didn't raise: %s" % e_type.__name__)

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        bucket = self._makeOne()
        self.assertEqual(bucket._keys, [])
        self.assertEqual(bucket._next, None)
        self.assertEqual(len(bucket), 0)
        self.assertEqual(bucket.size, 0)

    def test__deleteNextBucket_none(self):
        bucket = self._makeOne()
        bucket._deleteNextBucket() # no raise
        self.assertTrue(bucket._next is None)

    def test__deleteNextBucket_one(self):
        bucket1 = self._makeOne()
        bucket2 = bucket1._next = self._makeOne()
        bucket1._deleteNextBucket() # no raise
        self.assertTrue(bucket1._next is None)

    def test__deleteNextBucket_two(self):
        bucket1 = self._makeOne()
        bucket2 = bucket1._next = self._makeOne()
        bucket3 = bucket2._next = self._makeOne()
        bucket1._deleteNextBucket() # no raise
        self.assertTrue(bucket1._next is bucket3)

    def test__search_empty(self):
        bucket = self._makeOne()
        self.assertEqual(bucket._search('nonesuch'), -1)

    def test__search_nonempty_miss(self):
        bucket = self._makeOne()
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._search('candy'), -3)

    def test__search_nonempty_hit(self):
        bucket = self._makeOne()
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._search('charlie'), 2)

    def test_minKey_empty(self):
        bucket = self._makeOne()
        self.assertRaises(IndexError, bucket.minKey)

    def test_minKey_no_bound(self):
        bucket = self._makeOne()
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.minKey(), 'alpha')

    def test_minKey_w_bound_hit(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.minKey('bravo'), 'bravo')

    def test_minKey_w_bound_miss(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.minKey('candy'), 'charlie')

    def test_minKey_w_bound_fail(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertRaises(ValueError, bucket.minKey, 'foxtrot')

    def test_maxKey_empty(self):
        bucket = self._makeOne()
        self.assertRaises(IndexError, bucket.maxKey)

    def test_maxKey_no_bound(self):
        bucket = self._makeOne()
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.maxKey(), 'echo')

    def test_maxKey_w_bound_hit(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.maxKey('bravo'), 'bravo')

    def test_maxKey_w_bound_miss(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.maxKey('candy'), 'bravo')

    def test_maxKey_w_bound_fail(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertRaises(ValueError, bucket.maxKey, 'abacus')

    def test__range_defaults_empty(self):
        bucket = self._makeOne()
        self.assertEqual(bucket._range(), (0, 0))

    def test__range_defaults_filled(self):
        bucket = self._makeOne()
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._range(), (0, 5))

    def test__range_defaults_exclude_min(self):
        bucket = self._makeOne()
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._range(excludemin=True), (1, 5))

    def test__range_defaults_exclude_max(self):
        bucket = self._makeOne()
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._range(excludemax=True), (0, 4))

    def test__range_w_min_hit(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._range(min='bravo'), (1, 5))

    def test__range_w_min_miss(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._range(min='candy'), (2, 5))

    def test__range_w_min_hit_w_exclude_min(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._range(min='bravo', excludemin=True), (2, 5))

    def test__range_w_min_miss_w_exclude_min(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        # 'excludemin' doesn't fire on miss
        self.assertEqual(bucket._range(min='candy', excludemin=True), (2, 5))

    def test__range_w_max_hit(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._range(max='delta'), (0, 4))

    def test__range_w_max_miss(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._range(max='dandy'), (0, 3))

    def test__range_w_max_hit_w_exclude_max(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._range(max='delta', excludemax=True), (0, 3))

    def test__range_w_max_miss_w_exclude_max(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        # 'excludemax' doesn't fire on miss
        self.assertEqual(bucket._range(max='dandy', excludemax=True), (0, 3))

    def test_keys_defaults_empty(self):
        bucket = self._makeOne()
        self.assertEqual(bucket.keys(), [])

    def test_keys_defaults_filled(self):
        bucket = self._makeOne()
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.keys(), KEYS[0: 5])

    def test_keys_defaults_exclude_min(self):
        bucket = self._makeOne()
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.keys(excludemin=True), KEYS[1: 5])

    def test_keys_defaults_exclude_max(self):
        bucket = self._makeOne()
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.keys(excludemax=True), KEYS[0: 4])

    def test_keys_w_min_hit(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.keys(min='bravo'), KEYS[1: 5])

    def test_keys_w_min_miss(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.keys(min='candy'), KEYS[2: 5])

    def test_keys_w_min_hit_w_exclude_min(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.keys(min='bravo', excludemin=True), KEYS[2: 5])

    def test_keys_w_min_miss_w_exclude_min(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        # 'excludemin' doesn't fire on miss
        self.assertEqual(bucket.keys(min='candy', excludemin=True), KEYS[2: 5])

    def test_keys_w_max_hit(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.keys(max='delta'), KEYS[0: 4])

    def test_keys_w_max_miss(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.keys(max='dandy'), KEYS[0: 3])

    def test_keys_w_max_hit_w_exclude_max(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.keys(max='delta', excludemax=True), KEYS[0: 3])

    def test_keys_w_max_miss_w_exclude_max(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        # 'excludemax' doesn't fire on miss
        self.assertEqual(bucket.keys(max='dandy', excludemax=True), KEYS[0: 3])

    def test_iterkeys_defaults_empty(self):
        bucket = self._makeOne()
        self.assertEqual(list(bucket.iterkeys()), [])

    def test_iterkeys_defaults_filled(self):
        bucket = self._makeOne()
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(list(bucket.iterkeys()), KEYS[0: 5])

    def test_iterkeys_defaults_exclude_min(self):
        bucket = self._makeOne()
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(list(bucket.iterkeys(excludemin=True)), KEYS[1: 5])

    def test_iterkeys_defaults_exclude_max(self):
        bucket = self._makeOne()
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(list(bucket.iterkeys(excludemax=True)), KEYS[0: 4])

    def test_iterkeys_w_min_hit(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(list(bucket.iterkeys(min='bravo')), KEYS[1: 5])

    def test_iterkeys_w_min_miss(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(list(bucket.iterkeys(min='candy')), KEYS[2: 5])

    def test_iterkeys_w_min_hit_w_exclude_min(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(list(bucket.iterkeys(min='bravo', excludemin=True)),
                         KEYS[2: 5])

    def test_iterkeys_w_min_miss_w_exclude_min(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        # 'excludemin' doesn't fire on miss
        self.assertEqual(list(bucket.iterkeys(min='candy', excludemin=True)),
                         KEYS[2: 5])

    def test_iterkeys_w_max_hit(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(list(bucket.iterkeys(max='delta')), KEYS[0: 4])

    def test_iterkeys_w_max_miss(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(list(bucket.iterkeys(max='dandy')), KEYS[0: 3])

    def test_iterkeys_w_max_hit_w_exclude_max(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(list(bucket.keys(max='delta', excludemax=True)),
                         KEYS[0: 3])

    def test_iterkeys_w_max_miss_w_exclude_max(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        # 'excludemax' doesn't fire on miss
        self.assertEqual(list(bucket.iterkeys(max='dandy', excludemax=True)),
                         KEYS[0: 3])

    def test___iter___empty(self):
        bucket = self._makeOne()
        self.assertEqual([x for x in bucket], [])

    def test___iter___filled(self):
        bucket = self._makeOne()
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual([x for x in bucket], KEYS[0: 5])

    def test___contains___empty(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        self.assertFalse('nonesuch' in bucket)

    def test___contains___filled_miss(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertFalse('nonesuch' in bucket)

    def test___contains___filled_hit(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        for key in KEYS:
            self.assertTrue(key in bucket)

    def _with_setstate(self):
        class _WithSetState(self._getTargetClass()):
            def __setstate__(self, state):
                self._keys, self._next = state
        return _WithSetState()

    def test__p_resolveConflict_new_next(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._with_setstate()
        N_NEW = object()
        s_old = ([], None)
        s_com = ([], N_NEW)
        s_new = ([], None)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 0)

    def test__p_resolveConflict_committed_next(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._with_setstate()
        N_NEW = object()
        s_old = ([], None)
        s_com = ([], None)
        s_new = ([], N_NEW)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 0)

    def test__p_resolveConflict_empty_committed(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._with_setstate()
        s_old = ([], None)
        s_com = ([], None)
        s_new = (['a'], None)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 12)

    def test__p_resolveConflict_empty_new(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._with_setstate()
        s_old = ([], None)
        s_com = (['a'], None)
        s_new = ([], None)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 12)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_BucketBase),
    ))
