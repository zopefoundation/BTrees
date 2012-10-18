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


def _skip_wo_ZODB(test_method): #pragma NO COVER
    try:
        import ZODB
    except ImportError: # skip this test if ZODB is not available
        def _dummy(*args):
            pass
        return _dummy
    else:
        return test_method


class Base:
    """ Tests common to all types: sets, buckets, and BTrees """

    storage = None

    def tearDown(self):
        import transaction
        transaction.abort()
        if self.storage is not None:
            self.storage.close()
            self.storage.cleanup()

    def _makeOne(self):
        return self._getTargetClass()()

    def openDB(self):
        import os
        from ZODB.FileStorage import FileStorage
        from ZODB.DB import DB
        n = 'fs_tmp__%s' % os.getpid()
        self.storage = FileStorage(n)
        self.db = DB(self.storage)
        return self.db

class MappingBase(Base):
    """ Tests common to mappings (buckets, btrees) """

    def _deletefail(self):
        t = self._makeOne()
        del t[1]

    def _setupConflict(self):

        l=[ -5124, -7377, 2274, 8801, -9901, 7327, 1565, 17, -679,
            3686, -3607, 14, 6419, -5637, 6040, -4556, -8622, 3847, 7191,
            -4067]


        e1=[(-1704, 0), (5420, 1), (-239, 2), (4024, 3), (-6984, 4)]
        e2=[(7745, 0), (4868, 1), (-2548, 2), (-2711, 3), (-3154, 4)]


        base = self._makeOne()
        base.update([(i, i*i) for i in l[:20]])
        b1=base.__class__(base)
        b2=base.__class__(base)
        bm=base.__class__(base)

        items=base.items()

        return  base, b1, b2, bm, e1, e2, items

    def testMergeDelete(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        del b1[items[1][0]]
        del b2[items[5][0]]
        del b1[items[-1][0]]
        del b2[items[-2][0]]
        del bm[items[1][0]]
        del bm[items[5][0]]
        del bm[items[-1][0]]
        del bm[items[-2][0]]
        _test_merge(base, b1, b2, bm, 'merge  delete')

    def testMergeDeleteAndUpdate(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        del b1[items[1][0]]
        b2[items[5][0]]=1
        del b1[items[-1][0]]
        b2[items[-2][0]]=2
        del bm[items[1][0]]
        bm[items[5][0]]=1
        del bm[items[-1][0]]
        bm[items[-2][0]]=2
        _test_merge(base, b1, b2, bm, 'merge update and delete')

    def testMergeUpdate(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        b1[items[0][0]]=1
        b2[items[5][0]]=2
        b1[items[-1][0]]=3
        b2[items[-2][0]]=4
        bm[items[0][0]]=1
        bm[items[5][0]]=2
        bm[items[-1][0]]=3
        bm[items[-2][0]]=4
        _test_merge(base, b1, b2, bm, 'merge update')

    def testFailMergeDelete(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        del b1[items[0][0]]
        del b2[items[0][0]]
        _test_merge(base, b1, b2, bm, 'merge conflicting delete',
                   should_fail=1)

    def testFailMergeUpdate(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        b1[items[0][0]]=1
        b2[items[0][0]]=2
        _test_merge(base, b1, b2, bm, 'merge conflicting update',
                   should_fail=1)

    def testFailMergeDeleteAndUpdate(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        del b1[items[0][0]]
        b2[items[0][0]]=-9
        _test_merge(base, b1, b2, bm, 'merge conflicting update and delete',
                   should_fail=1)

    def testMergeInserts(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        b1[-99999]=-99999
        b1[e1[0][0]]=e1[0][1]
        b2[99999]=99999
        b2[e1[2][0]]=e1[2][1]

        bm[-99999]=-99999
        bm[e1[0][0]]=e1[0][1]
        bm[99999]=99999
        bm[e1[2][0]]=e1[2][1]
        _test_merge(base, b1, b2, bm, 'merge insert')

    def testMergeInsertsFromEmpty(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        base.clear()
        b1.clear()
        b2.clear()
        bm.clear()

        b1.update(e1)
        bm.update(e1)
        b2.update(e2)
        bm.update(e2)

        _test_merge(base, b1, b2, bm, 'merge insert from empty')

    def testFailMergeEmptyAndFill(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        b1.clear()
        bm.clear()
        b2.update(e2)
        bm.update(e2)

        _test_merge(base, b1, b2, bm, 'merge insert from empty', should_fail=1)

    def testMergeEmpty(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        b1.clear()
        bm.clear()

        _test_merge(base, b1, b2, bm, 'empty one and not other', should_fail=1)

    def testFailMergeInsert(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        b1[-99999]=-99999
        b1[e1[0][0]]=e1[0][1]
        b2[99999]=99999
        b2[e1[0][0]]=e1[0][1]
        _test_merge(base, b1, b2, bm, 'merge conflicting inserts',
                   should_fail=1)

class SetTests(Base):
    "Set (as opposed to TreeSet) specific tests."

    def _setupConflict(self):
        l=[ -5124, -7377, 2274, 8801, -9901, 7327, 1565, 17, -679,
            3686, -3607, 14, 6419, -5637, 6040, -4556, -8622, 3847, 7191,
            -4067]

        e1=[-1704, 5420, -239, 4024, -6984]
        e2=[7745, 4868, -2548, -2711, -3154]


        base = self._makeOne()
        base.update(l)
        b1=base.__class__(base)
        b2=base.__class__(base)
        bm=base.__class__(base)

        items=base.keys()

        return  base, b1, b2, bm, e1, e2, items

    def testMergeDelete(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        b1.remove(items[1])
        b2.remove(items[5])
        b1.remove(items[-1])
        b2.remove(items[-2])
        bm.remove(items[1])
        bm.remove(items[5])
        bm.remove(items[-1])
        bm.remove(items[-2])
        _test_merge(base, b1, b2, bm, 'merge  delete')

    def testFailMergeDelete(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        b1.remove(items[0])
        b2.remove(items[0])
        _test_merge(base, b1, b2, bm, 'merge conflicting delete',
                   should_fail=1)

    def testMergeInserts(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        b1.insert(-99999)
        b1.insert(e1[0])
        b2.insert(99999)
        b2.insert(e1[2])

        bm.insert(-99999)
        bm.insert(e1[0])
        bm.insert(99999)
        bm.insert(e1[2])
        _test_merge(base, b1, b2, bm, 'merge insert')

    def testMergeInsertsFromEmpty(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        base.clear()
        b1.clear()
        b2.clear()
        bm.clear()

        b1.update(e1)
        bm.update(e1)
        b2.update(e2)
        bm.update(e2)

        _test_merge(base, b1, b2, bm, 'merge insert from empty')

    def testFailMergeEmptyAndFill(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        b1.clear()
        bm.clear()
        b2.update(e2)
        bm.update(e2)

        _test_merge(base, b1, b2, bm, 'merge insert from empty', should_fail=1)

    def testMergeEmpty(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        b1.clear()
        bm.clear()

        _test_merge(base, b1, b2, bm, 'empty one and not other', should_fail=1)

    def testFailMergeInsert(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        b1.insert(-99999)
        b1.insert(e1[0])
        b2.insert(99999)
        b2.insert(e1[0])
        _test_merge(base, b1, b2, bm, 'merge conflicting inserts',
                   should_fail=1)


def _test_merge(o1, o2, o3, expect, message='failed to merge', should_fail=0):
    from BTrees.Interfaces import BTreesConflictError
    s1 = o1.__getstate__()
    s2 = o2.__getstate__()
    s3 = o3.__getstate__()
    expected = expect.__getstate__()
    if expected is None:
        expected = ((((),),),)

    if should_fail:
        try:
            merged = o1._p_resolveConflict(s1, s2, s3)
        except BTreesConflictError, err:
            pass
        else:
            assert 0, message
    else:
        merged = o1._p_resolveConflict(s1, s2, s3)
        assert merged == expected, message


class OOBTreeTests(MappingBase, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.OOBTree import OOBTree
        return OOBTree

class OOBucketTests(MappingBase, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.OOBTree import OOBucket
        return OOBucket

class OOTreeSetTests(SetTests, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.OOBTree import OOTreeSet
        return OOTreeSet

class OOSetTests(SetTests, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.OOBTree import OOSet
        return OOSet


class IIBTreeTests(MappingBase, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.IIBTree import IIBTree
        return IIBTree

class IIBucketTests(MappingBase, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.IIBTree import IIBucket
        return IIBucket

class IITreeSetTests(SetTests, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.IIBTree import IITreeSet
        return IITreeSet

class IISetTests(SetTests, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.IIBTree import IISet
        return IISet


class IOBTreeTests(MappingBase, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.IOBTree import IOBTree
        return IOBTree

class IOBucketTests(MappingBase, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.IOBTree import IOBucket
        return IOBucket

class IOTreeSetTests(SetTests, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.IOBTree import IOTreeSet
        return IOTreeSet

class IOSetTests(SetTests, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.IOBTree import IOSet
        return IOSet


class OIBTreeTests(MappingBase, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.OIBTree import OIBTree
        return OIBTree

class OIBucketTests(MappingBase, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.OIBTree import OIBucket
        return OIBucket

class OITreeSetTests(SetTests, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.OIBTree import OITreeSet
        return OITreeSet

class OISetTests(SetTests, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.OIBTree import OISet
        return OISet


class IFBTreeTests(MappingBase, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.IFBTree import IFBTree
        return IFBTree

class IFBucketTests(MappingBase, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.IFBTree import IFBucket
        return IFBucket

class IFTreeSetTests(SetTests, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.IFBTree import IFTreeSet
        return IFTreeSet

class IFSetTests(SetTests, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.IFBTree import IFSet
        return IFSet


class LLBTreeTests(MappingBase, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.LLBTree import LLBTree
        return LLBTree

class LLBucketTests(MappingBase, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.LLBTree import LLBucket
        return LLBucket

class LLTreeSetTests(SetTests, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.LLBTree import LLTreeSet
        return LLTreeSet

class LLSetTests(SetTests, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.LLBTree import LLSet
        return LLSet


class LOBTreeTests(MappingBase, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.LOBTree import LOBTree
        return LOBTree

class LOBucketTests(MappingBase, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.LOBTree import LOBucket
        return LOBucket

class LOTreeSetTests(SetTests, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.LOBTree import LOTreeSet
        return LOTreeSet

class LOSetTests(SetTests, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.LOBTree import LOSet
        return LOSet


class OLBTreeTests(MappingBase, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.OLBTree import OLBTree
        return OLBTree

class OLBucketTests(MappingBase, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.OLBTree import OLBucket
        return OLBucket

class OLTreeSetTests(SetTests, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.OLBTree import OLTreeSet
        return OLTreeSet

class OLSetTests(SetTests, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.OLBTree import OLSet
        return OLSet


class LFBTreeTests(MappingBase, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.LFBTree import LFBTree
        return LFBTree

class LFBucketTests(MappingBase, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.LFBTree import LFBucket
        return LFBucket

class LFTreeSetTests(SetTests, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.LFBTree import LFTreeSet
        return LFTreeSet

class LFSetTests(SetTests, unittest.TestCase):
    def _getTargetClass(self):
        from BTrees.LFBTree import LFSet
        return LFSet


class NastyConfictFunctionalTests(Base, unittest.TestCase):
    # Provoke various conflict scenarios using ZODB + transaction

    def _getTargetClass(self):
        from BTrees.OOBTree import OOBTree
        return OOBTree

    @_skip_wo_ZODB
    def testSimpleConflict(self):
        # Invoke conflict resolution by committing a transaction and
        # catching a conflict in the storage.
        import transaction
        self.openDB()

        r1 = self.db.open().root()
        r1["t"] = t = self._makeOne()
        transaction.commit()

        r2 = self.db.open().root()
        copy = r2["t"]
        list(copy)    # unghostify

        self.assertEqual(t._p_serial, copy._p_serial)

        t.update({1:2, 2:3})
        transaction.commit()

        copy.update({3:4})
        transaction.commit()

    # This tests a problem that cropped up while trying to write
    # testBucketSplitConflict (below):  conflict resolution wasn't
    # working at all in non-trivial cases.  Symptoms varied from
    # strange complaints about pickling (despite that the test isn't
    # doing any *directly*), thru SystemErrors from Python and
    # AssertionErrors inside the BTree code.
    @_skip_wo_ZODB
    def testResolutionBlowsUp(self):
        import transaction
        b = self._makeOne()
        for i in range(0, 200, 4):
            b[i] = i
        # bucket 0 has 15 values: 0, 4 .. 56
        # bucket 1 has 15 values: 60, 64 .. 116
        # bucket 2 has 20 values: 120, 124 .. 196
        state = b.__getstate__()
        # Looks like:  ((bucket0, 60, bucket1, 120, bucket2), firstbucket)
        # If these fail, the *preconditions* for running the test aren't
        # satisfied -- the test itself hasn't been run yet.
        self.assertEqual(len(state), 2)
        self.assertEqual(len(state[0]), 5)
        self.assertEqual(state[0][1], 60)
        self.assertEqual(state[0][3], 120)

        # Invoke conflict resolution by committing a transaction.
        self.openDB()

        r1 = self.db.open().root()
        r1["t"] = b
        transaction.commit()

        r2 = self.db.open().root()
        copy = r2["t"]
        # Make sure all of copy is loaded.
        list(copy.values())

        self.assertEqual(b._p_serial, copy._p_serial)

        b.update({1:2, 2:3})
        transaction.commit()

        copy.update({3:4})
        transaction.commit()  # if this doesn't blow up
        list(copy.values())         # and this doesn't either, then fine

    @_skip_wo_ZODB
    def testBucketSplitConflict(self):
        # Tests that a bucket split is viewed as a conflict.
        # It's (almost necessarily) a white-box test, and sensitive to
        # implementation details.
        import transaction
        from ZODB.POSException import ConflictError
        b = orig = self._makeOne()
        for i in range(0, 200, 4):
            b[i] = i
        # bucket 0 has 15 values: 0, 4 .. 56
        # bucket 1 has 15 values: 60, 64 .. 116
        # bucket 2 has 20 values: 120, 124 .. 196
        state = b.__getstate__()
        # Looks like:  ((bucket0, 60, bucket1, 120, bucket2), firstbucket)
        # If these fail, the *preconditions* for running the test aren't
        # satisfied -- the test itself hasn't been run yet.
        self.assertEqual(len(state), 2)
        self.assertEqual(len(state[0]), 5)
        self.assertEqual(state[0][1], 60)
        self.assertEqual(state[0][3], 120)

        # Invoke conflict resolution by committing a transaction.
        self.openDB()

        tm1 = transaction.TransactionManager()
        r1 = self.db.open(transaction_manager=tm1).root()
        r1["t"] = b
        tm1.commit()

        tm2 = transaction.TransactionManager()
        r2 = self.db.open(transaction_manager=tm2).root()
        copy = r2["t"]
        # Make sure all of copy is loaded.
        list(copy.values())

        self.assertEqual(orig._p_serial, copy._p_serial)

        # In one transaction, add 16 new keys to bucket1, to force a bucket
        # split.
        b = orig
        numtoadd = 16
        candidate = 60
        while numtoadd:
            if not b.has_key(candidate):
                b[candidate] = candidate
                numtoadd -= 1
            candidate += 1
        # bucket 0 has 15 values: 0, 4 .. 56
        # bucket 1 has 15 values: 60, 61 .. 74
        # bucket 2 has 16 values: [75, 76 .. 81] + [84, 88 ..116]
        # bucket 3 has 20 values: 120, 124 .. 196
        state = b.__getstate__()
        # Looks like:  ((b0, 60, b1, 75, b2, 120, b3), firstbucket)
        # The next block is still verifying preconditions.
        self.assertEqual(len(state) , 2)
        self.assertEqual(len(state[0]), 7)
        self.assertEqual(state[0][1], 60)
        self.assertEqual(state[0][3], 75)
        self.assertEqual(state[0][5], 120)

        tm1.commit()

        # In the other transaction, add 3 values near the tail end of bucket1.
        # This doesn't cause a split.
        b = copy
        for i in range(112, 116):
            b[i] = i
        # bucket 0 has 15 values: 0, 4 .. 56
        # bucket 1 has 18 values: 60, 64 .. 112, 113, 114, 115, 116
        # bucket 2 has 20 values: 120, 124 .. 196
        state = b.__getstate__()
        # Looks like:  ((bucket0, 60, bucket1, 120, bucket2), firstbucket)
        # The next block is still verifying preconditions.
        self.assertEqual(len(state), 2)
        self.assertEqual(len(state[0]), 5)
        self.assertEqual(state[0][1], 60)
        self.assertEqual(state[0][3], 120)

        self.assertRaises(ConflictError, tm2.commit)

    @_skip_wo_ZODB
    def testEmptyBucketConflict(self):
        # Tests that an emptied bucket *created by* conflict resolution is
        # viewed as a conflict:  conflict resolution doesn't have enough
        # info to unlink the empty bucket from the BTree correctly.
        import transaction
        from ZODB.POSException import ConflictError
        b = orig = self._makeOne()
        for i in range(0, 200, 4):
            b[i] = i
        # bucket 0 has 15 values: 0, 4 .. 56
        # bucket 1 has 15 values: 60, 64 .. 116
        # bucket 2 has 20 values: 120, 124 .. 196
        state = b.__getstate__()
        # Looks like:  ((bucket0, 60, bucket1, 120, bucket2), firstbucket)
        # If these fail, the *preconditions* for running the test aren't
        # satisfied -- the test itself hasn't been run yet.
        self.assertEqual(len(state), 2)
        self.assertEqual(len(state[0]), 5)
        self.assertEqual(state[0][1], 60)
        self.assertEqual(state[0][3], 120)

        # Invoke conflict resolution by committing a transaction.
        self.openDB()

        tm1 = transaction.TransactionManager()
        r1 = self.db.open(transaction_manager=tm1).root()
        r1["t"] = b
        tm1.commit()

        tm2 = transaction.TransactionManager()
        r2 = self.db.open(transaction_manager=tm2).root()
        copy = r2["t"]
        # Make sure all of copy is loaded.
        list(copy.values())

        self.assertEqual(orig._p_serial, copy._p_serial)

        # In one transaction, delete half of bucket 1.
        b = orig
        for k in 60, 64, 68, 72, 76, 80, 84, 88:
            del b[k]
        # bucket 0 has 15 values: 0, 4 .. 56
        # bucket 1 has 7 values: 92, 96, 100, 104, 108, 112, 116
        # bucket 2 has 20 values: 120, 124 .. 196
        state = b.__getstate__()
        # Looks like:  ((bucket0, 60, bucket1, 120, bucket2), firstbucket)
        # The next block is still verifying preconditions.
        self.assertEqual(len(state) , 2)
        self.assertEqual(len(state[0]), 5)
        self.assertEqual(state[0][1], 92)
        self.assertEqual(state[0][3], 120)

        tm1.commit()

        # In the other transaction, delete the other half of bucket 1.
        b = copy
        for k in 92, 96, 100, 104, 108, 112, 116:
            del b[k]
        # bucket 0 has 15 values: 0, 4 .. 56
        # bucket 1 has 8 values: 60, 64, 68, 72, 76, 80, 84, 88
        # bucket 2 has 20 values: 120, 124 .. 196
        state = b.__getstate__()
        # Looks like:  ((bucket0, 60, bucket1, 120, bucket2), firstbucket)
        # The next block is still verifying preconditions.
        self.assertEqual(len(state), 2)
        self.assertEqual(len(state[0]), 5)
        self.assertEqual(state[0][1], 60)
        self.assertEqual(state[0][3], 120)

        # Conflict resolution empties bucket1 entirely.  This used to
        # create an "insane" BTree (a legit BTree cannot contain an empty
        # bucket -- it contains NULL pointers the BTree code doesn't
        # expect, and segfaults result).
        self.assertRaises(ConflictError, tm2.commit)

    @_skip_wo_ZODB
    def testEmptyBucketNoConflict(self):
        # Tests that a plain empty bucket (on input) is not viewed as a
        # conflict.
        import transaction
        b = orig = self._makeOne()
        for i in range(0, 200, 4):
            b[i] = i
        # bucket 0 has 15 values: 0, 4 .. 56
        # bucket 1 has 15 values: 60, 64 .. 116
        # bucket 2 has 20 values: 120, 124 .. 196
        state = b.__getstate__()
        # Looks like:  ((bucket0, 60, bucket1, 120, bucket2), firstbucket)
        # If these fail, the *preconditions* for running the test aren't
        # satisfied -- the test itself hasn't been run yet.
        self.assertEqual(len(state), 2)
        self.assertEqual(len(state[0]), 5)
        self.assertEqual(state[0][1], 60)
        self.assertEqual(state[0][3], 120)

        # Invoke conflict resolution by committing a transaction.
        self.openDB()

        r1 = self.db.open().root()
        r1["t"] = orig
        transaction.commit()

        r2 = self.db.open().root()
        copy = r2["t"]
        # Make sure all of copy is loaded.
        list(copy.values())

        self.assertEqual(orig._p_serial, copy._p_serial)

        # In one transaction, just add a key.
        b = orig
        b[1] = 1
        # bucket 0 has 16 values: [0, 1] + [4, 8 .. 56]
        # bucket 1 has 15 values: 60, 64 .. 116
        # bucket 2 has 20 values: 120, 124 .. 196
        state = b.__getstate__()
        # Looks like:  ((bucket0, 60, bucket1, 120, bucket2), firstbucket)
        # The next block is still verifying preconditions.
        self.assertEqual(len(state), 2)
        self.assertEqual(len(state[0]), 5)
        self.assertEqual(state[0][1], 60)
        self.assertEqual(state[0][3], 120)

        transaction.commit()

        # In the other transaction, delete bucket 2.
        b = copy
        for k in range(120, 200, 4):
            del b[k]
        # bucket 0 has 15 values: 0, 4 .. 56
        # bucket 1 has 15 values: 60, 64 .. 116
        state = b.__getstate__()
        # Looks like:  ((bucket0, 60, bucket1), firstbucket)
        # The next block is still verifying preconditions.
        self.assertEqual(len(state), 2)
        self.assertEqual(len(state[0]), 3)
        self.assertEqual(state[0][1], 60)

        # This shouldn't create a ConflictError.
        transaction.commit()
        # And the resulting BTree shouldn't have internal damage.
        b._check()

    # The snaky control flow in _bucket__p_resolveConflict ended up trying
    # to decref a NULL pointer if conflict resolution was fed 3 empty
    # buckets.  http://collector.zope.org/Zope/553
    def testThreeEmptyBucketsNoSegfault(self):
        from ZODB.POSException import ConflictError
        t = self._makeOne()
        t[1] = 1
        bucket = t._firstbucket
        del t[1]
        state1 = bucket.__getstate__()
        state2 = bucket.__getstate__()
        state3 = bucket.__getstate__()
        self.assert_(state2 is not state1 and
                     state2 is not state3 and
                     state3 is not state1)
        self.assert_(state2 == state1 and
                     state3 == state1)
        self.assertRaises(ConflictError, bucket._p_resolveConflict,
                          state1, state2, state3)
        # When an empty BTree resolves conflicts, it computes the
        # bucket state as None, so...
        self.assertRaises(ConflictError, bucket._p_resolveConflict,
                          None, None, None)

    @_skip_wo_ZODB
    def testCantResolveBTreeConflict(self):
        # Test that a conflict involving two different changes to
        # an internal BTree node is unresolvable.  An internal node
        # only changes when there are enough additions or deletions
        # to a child bucket that the bucket is split or removed.
        # It's (almost necessarily) a white-box test, and sensitive to
        # implementation details.
        import transaction
        from ZODB.POSException import ConflictError
        b = orig = self._makeOne()
        for i in range(0, 200, 4):
            b[i] = i
        # bucket 0 has 15 values: 0, 4 .. 56
        # bucket 1 has 15 values: 60, 64 .. 116
        # bucket 2 has 20 values: 120, 124 .. 196
        state = b.__getstate__()
        # Looks like:  ((bucket0, 60, bucket1, 120, bucket2), firstbucket)
        # If these fail, the *preconditions* for running the test aren't
        # satisfied -- the test itself hasn't been run yet.
        self.assertEqual(len(state), 2)
        self.assertEqual(len(state[0]), 5)
        self.assertEqual(state[0][1], 60)
        self.assertEqual(state[0][3], 120)

        # Set up database connections to provoke conflict.
        self.openDB()
        tm1 = transaction.TransactionManager()
        r1 = self.db.open(transaction_manager=tm1).root()
        r1["t"] = orig
        tm1.commit()

        tm2 = transaction.TransactionManager()
        r2 = self.db.open(transaction_manager=tm2).root()
        copy = r2["t"]
        # Make sure all of copy is loaded.
        list(copy.values())

        self.assertEqual(orig._p_serial, copy._p_serial)

        # Now one transaction should add enough keys to cause a split,
        # and another should remove all the keys in one bucket.

        for k in range(200, 300, 4):
            orig[k] = k
        tm1.commit()

        for k in range(0, 60, 4):
            del copy[k]

        self.assertRaises(ConflictError, tm2.commit)

    @_skip_wo_ZODB
    def testConflictWithOneEmptyBucket(self):
        # If one transaction empties a bucket, while another adds an item
        # to the bucket, all the changes "look resolvable":  bucket conflict
        # resolution returns a bucket containing (only) the item added by
        # the latter transaction, but changes from the former transaction
        # removing the bucket are uncontested:  the bucket is removed from
        # the BTree despite that resolution thinks it's non-empty!  This
        # was first reported by Dieter Maurer, to zodb-dev on 22 Mar 2005.
        import transaction
        from ZODB.POSException import ConflictError
        b = orig = self._makeOne()
        for i in range(0, 200, 4):
            b[i] = i
        # bucket 0 has 15 values: 0, 4 .. 56
        # bucket 1 has 15 values: 60, 64 .. 116
        # bucket 2 has 20 values: 120, 124 .. 196
        state = b.__getstate__()
        # Looks like:  ((bucket0, 60, bucket1, 120, bucket2), firstbucket)
        # If these fail, the *preconditions* for running the test aren't
        # satisfied -- the test itself hasn't been run yet.
        self.assertEqual(len(state), 2)
        self.assertEqual(len(state[0]), 5)
        self.assertEqual(state[0][1], 60)
        self.assertEqual(state[0][3], 120)

        # Set up database connections to provoke conflict.
        self.openDB()
        tm1 = transaction.TransactionManager()
        r1 = self.db.open(transaction_manager=tm1).root()
        r1["t"] = orig
        tm1.commit()

        tm2 = transaction.TransactionManager()
        r2 = self.db.open(transaction_manager=tm2).root()
        copy = r2["t"]
        # Make sure all of copy is loaded.
        list(copy.values())

        self.assertEqual(orig._p_serial, copy._p_serial)

        # Now one transaction empties the first bucket, and another adds a
        # key to the first bucket.

        for k in range(0, 60, 4):
            del orig[k]
        tm1.commit()

        copy[1] = 1

        self.assertRaises(ConflictError, tm2.commit)

        # Same thing, except commit the transactions in the opposite order.
        b = self._makeOne()
        for i in range(0, 200, 4):
            b[i] = i

        tm1 = transaction.TransactionManager()
        r1 = self.db.open(transaction_manager=tm1).root()
        r1["t"] = b
        tm1.commit()

        tm2 = transaction.TransactionManager()
        r2 = self.db.open(transaction_manager=tm2).root()
        copy = r2["t"]
        # Make sure all of copy is loaded.
        list(copy.values())

        self.assertEqual(b._p_serial, copy._p_serial)

        # Now one transaction empties the first bucket, and another adds a
        # key to the first bucket.
        b[1] = 1
        tm1.commit()

        for k in range(0, 60, 4):
            del copy[k]

        self.assertRaises(ConflictError, tm2.commit)

    @_skip_wo_ZODB
    def testConflictOfInsertAndDeleteOfFirstBucketItem(self):
        """
        Recently, BTrees became careful about removing internal keys
        (keys in internal aka BTree nodes) when they were deleted from
        buckets. This poses a problem for conflict resolution.

        We want to guard against a case in which the first key in a
        bucket is removed in one transaction while a key is added
        after that key but before the next key in another transaction
        with the result that the added key is unreachble

        original:

          Bucket(...), k1, Bucket((k1, v1), (k3, v3), ...)

        tran1

          Bucket(...), k3, Bucket(k3, v3), ...)

        tran2

          Bucket(...), k1, Bucket((k1, v1), (k2, v2), (k3, v3), ...)

          where k1 < k2 < k3

        We don't want:

          Bucket(...), k3, Bucket((k2, v2), (k3, v3), ...)

          as k2 would be unfindable, so we want a conflict.

        """
        import transaction
        from ZODB.POSException import ConflictError
        mytype = self._getTargetClass()
        db = self.openDB()
        tm1 = transaction.TransactionManager()
        conn1 = db.open(tm1)
        conn1.root.t = t = mytype()
        for i in range(0, 200, 2):
            t[i] = i
        tm1.commit()
        k = t.__getstate__()[0][1]
        assert t.__getstate__()[0][2].keys()[0] == k

        tm2 = transaction.TransactionManager()
        conn2 = db.open(tm2)

        t[k+1] = k+1
        del conn2.root.t[k]
        for i in range(200,300):
            conn2.root.t[i] = i

        tm1.commit()
        self.assertRaises(ConflictError, tm2.commit)
        tm2.abort()

        k = t.__getstate__()[0][1]
        t[k+1] = k+1
        del conn2.root.t[k]

        tm2.commit()
        self.assertRaises(ConflictError, tm1.commit)
        tm1.abort()



def test_suite():
    suite = unittest.TestSuite((
        unittest.makeSuite(OOBTreeTests),
        unittest.makeSuite(OOBucketTests),
        unittest.makeSuite(OOTreeSetTests),
        unittest.makeSuite(OOSetTests),

        unittest.makeSuite(IIBTreeTests),
        unittest.makeSuite(IIBucketTests),
        unittest.makeSuite(IITreeSetTests),
        unittest.makeSuite(IISetTests),

        unittest.makeSuite(IOBTreeTests),
        unittest.makeSuite(IOBucketTests),
        unittest.makeSuite(IOTreeSetTests),
        unittest.makeSuite(IOSetTests),

        unittest.makeSuite(OIBTreeTests),
        unittest.makeSuite(OIBucketTests),
        unittest.makeSuite(OITreeSetTests),
        unittest.makeSuite(OISetTests),

        unittest.makeSuite(IFBTreeTests),
        unittest.makeSuite(IFBucketTests),
        unittest.makeSuite(IFTreeSetTests),
        unittest.makeSuite(IFSetTests),

        unittest.makeSuite(LLBTreeTests),
        unittest.makeSuite(LLBucketTests),
        unittest.makeSuite(LLTreeSetTests),
        unittest.makeSuite(LLSetTests),

        unittest.makeSuite(LOBTreeTests),
        unittest.makeSuite(LOBucketTests),
        unittest.makeSuite(LOTreeSetTests),
        unittest.makeSuite(LOSetTests),

        unittest.makeSuite(OLBTreeTests),
        unittest.makeSuite(OLBucketTests),
        unittest.makeSuite(OLTreeSetTests),
        unittest.makeSuite(OLSetTests),

        unittest.makeSuite(LFBTreeTests),
        unittest.makeSuite(LFBucketTests),
        unittest.makeSuite(LFTreeSetTests),
        unittest.makeSuite(LFSetTests),

        unittest.makeSuite(NastyConfictFunctionalTests),
    ))

    return suite
