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

from .common import _skip_wo_ZODB
from .common import ConflictTestBase


class NastyConfictFunctionalTests(ConflictTestBase, unittest.TestCase):
    # FUNCTESTS: Provoke various conflict scenarios using ZODB + transaction

    def _getTargetClass(self):
        from BTrees.OOBTree import OOBTree
        return OOBTree

    def openDB(self):
        # The conflict tests tend to open two or more connections
        # and then try to commit them. A standard FileStorage
        # is not MVCC aware, and so each connection would have the same
        # instance of the storage, leading to the error
        # "Duplicate tpc_begin calls for same transaction" on commit;
        # thus we use a MVCCMappingStorage for these tests, ensuring each
        # connection has its own storage.
        # Unfortunately, it wants to acquire the identically same
        # non-recursive lock in each of its *its* tpc_* methods, which deadlocks.
        # The solution is to give each instance its own lock, and trust in the
        # serialization (ordering) of the datamanager, and the fact that these tests are
        # single-threaded.
        import threading
        from ZODB.tests.MVCCMappingStorage  import MVCCMappingStorage
        class _MVCCMappingStorage(MVCCMappingStorage):
            def new_instance(self):
                inst = MVCCMappingStorage.new_instance(self)
                inst._commit_lock = threading.Lock()
                return inst
        from ZODB.DB import DB
        self.storage = _MVCCMappingStorage()
        self.db = DB(self.storage)
        return self.db


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
            if candidate not in b:
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
        # Note that the conflict is raised by our C extension, rather than
        # indirectly via the storage, and hence is a more specialized type.
        # This test therefore does not require ZODB.
        from BTrees.Interfaces import BTreesConflictError
        t = self._makeOne()
        t[1] = 1
        bucket = t._firstbucket
        del t[1]
        state1 = bucket.__getstate__()
        state2 = bucket.__getstate__()
        state3 = bucket.__getstate__()
        self.assertTrue(state2 is not state1 and
                        state2 is not state3 and
                        state3 is not state1)
        self.assertTrue(state2 == state1 and
                        state3 == state1)
        self.assertRaises(BTreesConflictError, bucket._p_resolveConflict,
                          state1, state2, state3)
        # When an empty BTree resolves conflicts, it computes the
        # bucket state as None, so...
        self.assertRaises(BTreesConflictError, bucket._p_resolveConflict,
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
        # Recently, BTrees became careful about removing internal keys
        # (keys in internal aka BTree nodes) when they were deleted from
        # buckets. This poses a problem for conflict resolution.

        # We want to guard against a case in which the first key in a
        # bucket is removed in one transaction while a key is added
        # after that key but before the next key in another transaction
        # with the result that the added key is unreachable.

        # original:

        #   Bucket(...), k1, Bucket((k1, v1), (k3, v3), ...)

        # tran1

        #   Bucket(...), k3, Bucket(k3, v3), ...)

        # tran2

        #   Bucket(...), k1, Bucket((k1, v1), (k2, v2), (k3, v3), ...)

        #   where k1 < k2 < k3

        # We don't want:

        #   Bucket(...), k3, Bucket((k2, v2), (k3, v3), ...)

        #   as k2 would be unfindable, so we want a conflict.

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
    return unittest.TestSuite((
        unittest.makeSuite(NastyConfictFunctionalTests),
    ))
