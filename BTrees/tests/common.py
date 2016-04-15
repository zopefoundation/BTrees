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

import platform
from unittest import skip


def _skip_wo_ZODB(test_method):  # pragma: no COVER
    try:
        import ZODB  # noqa
    except ImportError:  # skip this test if ZODB is not available
        return skip("ZODB not available")(test_method)
    else:
        return test_method


def _skip_under_Py3k(test_method):  # pragma: no COVER
    try:
        unicode
    except NameError:  # skip this test
        return skip("Python 3")(test_method)
    else:
        return test_method


def _skip_on_32_bits(test_method):  # pragma: no COVER
    if platform.architecture()[0] == '32bit':
        return skip("32-bit platform")(test_method)
    return test_method


class Base(object):
    # Tests common to all types: sets, buckets, and BTrees

    db = None

    def _getTargetClass(self):
        raise NotImplementedError("subclass should return the target type")

    def _makeOne(self):
        return self._getTargetClass()()


    def tearDown(self):
        if self.db is not None:
            self.db.close()

    def _getRoot(self):
        from ZODB import DB
        from ZODB.MappingStorage import MappingStorage
        if self.db is None:
            # Unclear:  On the next line, the ZODB4 flavor of this routine
            # [asses a cache_size argument:
            #     self.db = DB(MappingStorage(), cache_size=1)
            # If that's done here, though, testLoadAndStore() and
            # testGhostUnghost() both nail the CPU and seemingly
            # never finish.
            self.db = DB(MappingStorage())
        return self.db.open().root()

    def _closeRoot(self, root):
        import transaction
        # If we don't commit/abort the transaction, then
        # closing the Connection tends to fail with
        # "Cannot close connection joined to transaction"
        transaction.abort()
        root._p_jar.close()

    @_skip_wo_ZODB
    def testLoadAndStore(self):
        import transaction
        for i in 0, 10, 1000:
            t = self._makeOne()
            self._populate(t, i)
            root = None
            root = self._getRoot()
            root[i] = t
            transaction.commit()

            root2 = self._getRoot()
            if hasattr(t, 'items'):
                self.assertEqual(list(root2[i].items()) , list(t.items()))
            else:
                self.assertEqual(list(root2[i].keys()) , list(t.keys()))

            self._closeRoot(root)
            self._closeRoot(root2)

    def testSetstateArgumentChecking(self):
        try:
            self._makeOne().__setstate__(('',))
        except TypeError as v:
            self.assertEqual(str(v), 'tuple required for first state element')
        else:
            raise AssertionError("Expected exception")

    @_skip_wo_ZODB
    def testGhostUnghost(self):
        import transaction
        for i in 0, 10, 1000:
            t = self._makeOne()
            self._populate(t, i)
            root = self._getRoot()
            root[i] = t
            transaction.commit()

            root2 = self._getRoot()
            root2[i]._p_deactivate()
            transaction.commit()
            if hasattr(t, 'items'):
                self.assertEqual(list(root2[i].items()) , list(t.items()))
            else:
                self.assertEqual(list(root2[i].keys()) , list(t.keys()))

            self._closeRoot(root)
            self._closeRoot(root2)

    def testSimpleExclusiveKeyRange(self):
        t = self._makeOne()
        self.assertEqual(list(t.keys()), [])
        self.assertEqual(list(t.keys(excludemin=True)), [])
        self.assertEqual(list(t.keys(excludemax=True)), [])
        self.assertEqual(list(t.keys(excludemin=True, excludemax=True)), [])

        self._populate(t, 1)
        self.assertEqual(list(t.keys()), [0])
        self.assertEqual(list(t.keys(excludemin=True)), [])
        self.assertEqual(list(t.keys(excludemax=True)), [])
        self.assertEqual(list(t.keys(excludemin=True, excludemax=True)), [])

        t.clear()
        self._populate(t, 2)
        self.assertEqual(list(t.keys()), [0, 1])
        self.assertEqual(list(t.keys(excludemin=True)), [1])
        self.assertEqual(list(t.keys(excludemax=True)), [0])
        self.assertEqual(list(t.keys(excludemin=True, excludemax=True)), [])

        t.clear()
        self._populate(t, 3)
        self.assertEqual(list(t.keys()), [0, 1, 2])
        self.assertEqual(list(t.keys(excludemin=True)), [1, 2])
        self.assertEqual(list(t.keys(excludemax=True)), [0, 1])
        self.assertEqual(list(t.keys(excludemin=True, excludemax=True)), [1])

        self.assertEqual(list(t.keys(-1, 3, excludemin=True, excludemax=True)),
                         [0, 1, 2])
        self.assertEqual(list(t.keys(0, 3, excludemin=True, excludemax=True)),
                         [1, 2])
        self.assertEqual(list(t.keys(-1, 2, excludemin=True, excludemax=True)),
                         [0, 1])
        self.assertEqual(list(t.keys(0, 2, excludemin=True, excludemax=True)),
                         [1])

    @_skip_wo_ZODB
    def test_UpdatesDoReadChecksOnInternalNodes(self):
        import transaction
        from ZODB import DB
        from ZODB.MappingStorage import MappingStorage
        t = self._makeOne()
        if not hasattr(t, '_firstbucket'):
            return
        self._populate(t, 1000)
        store = MappingStorage()
        db = DB(store)
        conn = db.open()
        conn.root.t = t
        transaction.commit()

        read = []
        def readCurrent(ob):
            read.append(ob)
            conn.__class__.readCurrent(conn, ob)
            return 1

        conn.readCurrent = readCurrent

        try:
            add = t.add
            remove = t.remove
        except AttributeError:
            def add(i):
                t[i] = i
            def remove(i):
                del t[i]

        # Modifying a thing
        remove(100)
        self.assertTrue(t in read)
        del read[:]
        add(100)
        self.assertTrue(t in read)
        del read[:]

        transaction.abort()
        conn.cacheMinimize()
        list(t)
        self.assertTrue(100 in t)
        self.assertTrue(not read)

    def test_impl_pickle(self):
        # Issue #2
        # Nothing we pickle should include the 'Py' suffix of
        # implementation classes, and unpickling should give us
        # back the best available type
        import pickle
        made_one = self._makeOne()

        for proto in range(1, pickle.HIGHEST_PROTOCOL + 1):
            dumped_str = pickle.dumps(made_one, proto)
            self.assertTrue(b'Py' not in dumped_str, repr(dumped_str))

            loaded_one = pickle.loads(dumped_str)

            # If we're testing the pure-Python version, but we have the
            # C extension available, then the loaded type will be the C
            # extension but the made type will be the Python version.
            # Otherwise, they match. (Note that if we don't have C extensions
            # available, the __name__ will be altered to not have Py in it. See _fix_pickle)
            if 'Py' in type(made_one).__name__:
                self.assertTrue(type(loaded_one) is not type(made_one))
            else:
                self.assertTrue(type(loaded_one) is type(made_one) is self._getTargetClass(), (type(loaded_one), type(made_one), self._getTargetClass(), repr(dumped_str)))

            dumped_str2 = pickle.dumps(loaded_one, proto)
            self.assertEqual(dumped_str, dumped_str2)

    def test_pickle_empty(self):
        # Issue #2
        # Pickling an empty object and unpickling it should result
        # in an object that can be pickled, yielding an identical
        # pickle (and not an AttributeError)
        import pickle
        t = self._makeOne()

        s = pickle.dumps(t)
        t2 = pickle.loads(s)

        s2 = pickle.dumps(t2)
        self.assertEqual(s, s2)

        if hasattr(t2, '__len__'):
            # checks for _firstbucket
            self.assertEqual(0, len(t2))

        # This doesn't hold for things like Bucket and Set, sadly
        # self.assertEqual(t, t2)

    def test_pickle_subclass(self):
        # Issue #2: Make sure our class swizzling doesn't break
        # pickling subclasses

        # We need a globally named subclass for pickle, but it needs
        # to be unique in case tests run in parallel
        base_class = type(self._makeOne())
        class_name = 'PickleSubclassOf' + base_class.__name__
        PickleSubclass = type(class_name, (base_class,), {})
        globals()[class_name] = PickleSubclass

        import pickle
        loaded = pickle.loads(pickle.dumps(PickleSubclass()))
        self.assertTrue(type(loaded) is PickleSubclass, type(loaded))
        self.assertTrue(PickleSubclass().__class__ is PickleSubclass)

    def test_isinstance_subclass(self):
        # Issue #2:
        # In some cases we define a __class__ attribute that gets
        # invoked for isinstance and *lies*. Check that isinstance still
        # works (almost) as expected.

        t = self._makeOne()
        # It's a little bit weird, but in the fibbing case,
        # we're an instance of two unrelated classes
        self.assertTrue(isinstance(t, type(t)), (t, type(t)))
        self.assertTrue(isinstance(t, t.__class__))

        class Sub(type(t)):
            pass

        self.assertTrue(issubclass(Sub, type(t)))

        if type(t) is not t.__class__:
            # We're fibbing; this breaks issubclass of itself,
            # contrary to the usual mechanism
            self.assertFalse(issubclass(t.__class__, type(t)))


        class NonSub(object):
            pass

        self.assertFalse(issubclass(NonSub, type(t)))
        self.assertFalse(isinstance(NonSub(), type(t)))

class MappingBase(Base):
    # Tests common to mappings (buckets, btrees)

    def _populate(self, t, l):
        # Make some data
        for i in range(l):
            t[i]=i

    def testShortRepr(self):
        # test the repr because buckets have a complex repr implementation
        # internally the cutoff from a stack allocated buffer to a heap
        # allocated buffer is 10000.
        t = self._makeOne()
        for i in range(5):
            t[i] = i
        r = repr(t)
        # Make sure the repr is **not* 10000 bytes long for a shrort bucket.
        # (the buffer must be terminated when copied).
        self.assertTrue(len(r) < 10000)
        # Make sure the repr is human readable if it's a bucket
        if 'Bucket' in r:
            self.assertTrue(r.startswith("BTrees"))
            self.assertTrue(r.endswith(repr(t.items()) + ')'), r)
        else:
            self.assertEqual(r[:8], '<BTrees.')
        # Make sure it's the same between Python and C
        self.assertTrue('Py' not in r)

    def testRepr(self):
        # test the repr because buckets have a complex repr implementation
        # internally the cutoff from a stack allocated buffer to a heap
        # allocated buffer is 10000.
        t = self._makeOne()
        for i in range(1000):
            t[i] = i
        r = repr(t)
        # Make sure the repr is 10000 bytes long for a bucket.
        # But since the test is also run for btrees, skip the length
        # check if the repr starts with '<'
        if not r.startswith('<'):
            self.assertTrue(len(r) > 10000)

    def testGetItemFails(self):
        self.assertRaises(KeyError, self._getitemfail)

    def _getitemfail(self):
        return self._makeOne()[1]

    def testGetReturnsDefault(self):
        self.assertEqual(self._makeOne().get(1) , None)
        self.assertEqual(self._makeOne().get(1, 'foo') , 'foo')

    def testSetItemGetItemWorks(self):
        t = self._makeOne()
        t[1] = 1
        a = t[1]
        self.assertEqual(a , 1, repr(a))

    def testReplaceWorks(self):
        t = self._makeOne()
        t[1] = 1
        self.assertEqual(t[1] , 1, t[1])
        t[1] = 2
        self.assertEqual(t[1] , 2, t[1])

    def testLen(self):
        import random
        t = self._makeOne()
        added = {}
        r = list(range(1000))
        for x in r:
            k = random.choice(r)
            t[k] = x
            added[k] = x
        addl = added.keys()
        self.assertEqual(len(t) , len(addl), len(t))

    def testHasKeyWorks(self):
        from .._compat import PY2
        t = self._makeOne()
        t[1] = 1
        if PY2:
            self.assertTrue(t.has_key(1))
        self.assertTrue(1 in t)
        self.assertTrue(0 not in t)
        self.assertTrue(2 not in t)

    def testValuesWorks(self):
        t = self._makeOne()
        for x in range(100):
            t[x] = x*x
        v = t.values()
        for i in range(100):
            self.assertEqual(v[i], i*i)
        self.assertRaises(IndexError, lambda: v[i+1])
        i = 0
        for value in t.itervalues():
            self.assertEqual(value, i*i)
            i += 1

    def testValuesWorks1(self):
        t = self._makeOne()
        for x in range(100):
            t[99-x] = x

        for x in range(40):
            lst = sorted(t.values(0+x,99-x))
            self.assertEqual(lst, list(range(0+x,99-x+1)))

            lst = sorted(t.values(max=99-x, min=0+x))
            self.assertEqual(lst, list(range(0+x,99-x+1)))

    def testValuesNegativeIndex(self):
        t = self._makeOne()
        L = [-3, 6, -11, 4]
        for i in L:
            t[i] = i
        L = sorted(L)
        vals = t.values()
        for i in range(-1, -5, -1):
            self.assertEqual(vals[i], L[i])
        self.assertRaises(IndexError, lambda: vals[-5])

    def testKeysWorks(self):
        t = self._makeOne()
        for x in range(100):
            t[x] = x
        v = t.keys()
        i = 0
        for x in v:
            self.assertEqual(x,i)
            i = i + 1
        self.assertRaises(IndexError, lambda: v[i])

        for x in range(40):
            lst = t.keys(0+x,99-x)
            self.assertEqual(list(lst), list(range(0+x, 99-x+1)))

            lst = t.keys(max=99-x, min=0+x)
            self.assertEqual(list(lst), list(range(0+x, 99-x+1)))

        self.assertEqual(len(v), 100)

    def testKeysNegativeIndex(self):
        t = self._makeOne()
        L = [-3, 6, -11, 4]
        for i in L:
            t[i] = i
        L = sorted(L)
        keys = t.keys()
        for i in range(-1, -5, -1):
            self.assertEqual(keys[i], L[i])
        self.assertRaises(IndexError, lambda: keys[-5])

    def testItemsWorks(self):
        t = self._makeOne()
        for x in range(100):
            t[x] = 2*x
        v = t.items()
        i = 0
        for x in v:
            self.assertEqual(x[0], i)
            self.assertEqual(x[1], 2*i)
            i += 1
        self.assertRaises(IndexError, lambda: v[i+1])

        i = 0
        for x in t.iteritems():
            self.assertEqual(x, (i, 2*i))
            i += 1

        items = list(t.items(min=12, max=20))
        self.assertEqual(items, list(zip(range(12, 21), range(24, 43, 2))))

        items = list(t.iteritems(min=12, max=20))
        self.assertEqual(items, list(zip(range(12, 21), range(24, 43, 2))))

    def testItemsNegativeIndex(self):
        t = self._makeOne()
        L = [-3, 6, -11, 4]
        for i in L:
            t[i] = i
        L = sorted(L)
        items = t.items()
        for i in range(-1, -5, -1):
            self.assertEqual(items[i], (L[i], L[i]))
        self.assertRaises(IndexError, lambda: items[-5])

    def testDeleteInvalidKeyRaisesKeyError(self):
        self.assertRaises(KeyError, self._deletefail)

    def _deletefail(self):
        t = self._makeOne()
        del t[1]

    def testMaxKeyMinKey(self):
        t = self._makeOne()
        t[7] = 6
        t[3] = 10
        t[8] = 12
        t[1] = 100
        t[5] = 200
        t[10] = 500
        t[6] = 99
        t[4] = 150
        del t[7]
        self.assertEqual(t.maxKey(), 10)
        self.assertEqual(t.maxKey(None), 10)
        self.assertEqual(t.maxKey(6), 6)
        self.assertEqual(t.maxKey(9), 8)
        self.assertEqual(t.minKey(), 1)
        self.assertEqual(t.minKey(None), 1)
        self.assertEqual(t.minKey(3), 3)
        self.assertEqual(t.minKey(9), 10)

        try:
            t.maxKey(t.minKey() - 1)
        except ValueError as err:
            self.assertEqual(str(err), "no key satisfies the conditions")
        else:
            self.fail("expected ValueError")

        try:
            t.minKey(t.maxKey() + 1)
        except ValueError as err:
            self.assertEqual(str(err), "no key satisfies the conditions")
        else:
            self.fail("expected ValueError")

    def testClear(self):
        import random
        t = self._makeOne()
        r = list(range(100))
        for x in r:
            rnd = random.choice(r)
            t[rnd] = 0
        t.clear()
        diff = lsubtract(list(t.keys()), [])
        self.assertEqual(diff, [])

    def testUpdate(self):
        import random
        t = self._makeOne()
        d={}
        l=[]
        for i in range(10000):
            k=random.randrange(-2000, 2001)
            d[k]=i
            l.append((k, i))

        items= sorted(d.items())

        t.update(d)
        self.assertEqual(list(t.items()), items)

        t.clear()
        self.assertEqual(list(t.items()), [])

        t.update(l)
        self.assertEqual(list(t.items()), items)

    # Before ZODB 3.4.2, update/construction from PersistentMapping failed.
    def testUpdateFromPersistentMapping(self):
        from persistent.mapping import PersistentMapping
        t = self._makeOne()
        pm = PersistentMapping({1: 2})
        t.update(pm)
        self.assertEqual(list(t.items()), [(1, 2)])

        # Construction goes thru the same internals as .update().
        t = t.__class__(pm)
        self.assertEqual(list(t.items()), [(1, 2)])

    def testEmptyRangeSearches(self):
        t = self._makeOne()
        t.update([(1,1), (5,5), (9,9)])
        self.assertEqual(list(t.keys(-6,-4)), [], list(t.keys(-6,-4)))
        self.assertEqual(list(t.keys(2,4)), [], list(t.keys(2,4)))
        self.assertEqual(list(t.keys(6,8)), [], list(t.keys(6,8)))
        self.assertEqual(list(t.keys(10,12)), [], list(t.keys(10,12)))
        self.assertEqual(list(t.keys(9, 1)), [], list(t.keys(9, 1)))

        # For IITreeSets, this one was returning 31 for len(keys), and
        # list(keys) produced a list with 100 elements.
        t.clear()
        t.update(list(zip(range(300), range(300))))
        keys = t.keys(200, 50)
        self.assertEqual(len(keys), 0)
        self.assertEqual(list(keys), [])
        self.assertEqual(list(t.iterkeys(200, 50)), [])

        keys = t.keys(max=50, min=200)
        self.assertEqual(len(keys), 0)
        self.assertEqual(list(keys), [])
        self.assertEqual(list(t.iterkeys(max=50, min=200)), [])

    def testSlicing(self):
        # Test that slicing of .keys()/.values()/.items() works exactly the
        # same way as slicing a Python list with the same contents.
        # This tests fixes to several bugs in this area, starting with
        # http://collector.zope.org/Zope/419,
        # "BTreeItems slice contains 1 too many elements".
        from .._compat import xrange
        t = self._makeOne()
        for n in range(10):
            t.clear()
            self.assertEqual(len(t), 0)

            keys = []
            values = []
            items = []
            for key in range(n):
                value = -2 * key
                t[key] = value
                keys.append(key)
                values.append(value)
                items.append((key, value))
            self.assertEqual(len(t), n)

            kslice = t.keys()
            vslice = t.values()
            islice = t.items()
            self.assertEqual(len(kslice), n)
            self.assertEqual(len(vslice), n)
            self.assertEqual(len(islice), n)

            # Test whole-structure slices.
            x = kslice[:]
            self.assertEqual(list(x), keys[:])

            x = vslice[:]
            self.assertEqual(list(x), values[:])

            x = islice[:]
            self.assertEqual(list(x), items[:])

            for lo in range(-2*n, 2*n+1):
                # Test one-sided slices.
                x = kslice[:lo]
                self.assertEqual(list(x), keys[:lo])
                x = kslice[lo:]
                self.assertEqual(list(x), keys[lo:])

                x = vslice[:lo]
                self.assertEqual(list(x), values[:lo])
                x = vslice[lo:]
                self.assertEqual(list(x), values[lo:])

                x = islice[:lo]
                self.assertEqual(list(x), items[:lo])
                x = islice[lo:]
                self.assertEqual(list(x), items[lo:])

                for hi in range(-2*n, 2*n+1):
                    # Test two-sided slices.
                    x = kslice[lo:hi]
                    self.assertEqual(list(x), keys[lo:hi])

                    x = vslice[lo:hi]
                    self.assertEqual(list(x), values[lo:hi])

                    x = islice[lo:hi]
                    self.assertEqual(list(x), items[lo:hi])

        # The specific test case from Zope collector 419.
        t.clear()
        for i in xrange(100):
            t[i] = 1
        tslice = t.items()[20:80]
        self.assertEqual(len(tslice), 60)
        self.assertEqual(list(tslice), list(zip(range(20, 80), [1]*60)))

    def testIterators(self):
        t = self._makeOne()

        for keys in [], [-2], [1, 4], list(range(-170, 2000, 6)):
            t.clear()
            for k in keys:
                t[k] = -3 * k

            self.assertEqual(list(t), keys)

            x = []
            for k in t:
                x.append(k)
            self.assertEqual(x, keys)

            it = iter(t)
            self.assertTrue(it is iter(it))
            x = []
            try:
                while 1:
                    x.append(next(it))
            except StopIteration:
                pass
            self.assertEqual(x, keys)

            self.assertEqual(list(t.iterkeys()), keys)
            self.assertEqual(list(t.itervalues()), list(t.values()))
            self.assertEqual(list(t.iteritems()), list(t.items()))

    def testRangedIterators(self):
        t = self._makeOne()

        for keys in [], [-2], [1, 4], list(range(-170, 2000, 13)):
            t.clear()
            values = []
            for k in keys:
                value = -3 * k
                t[k] = value
                values.append(value)
            items = list(zip(keys, values))

            self.assertEqual(list(t.iterkeys()), keys)
            self.assertEqual(list(t.itervalues()), values)
            self.assertEqual(list(t.iteritems()), items)

            if not keys:
                continue

            min_mid_max = (keys[0], keys[len(keys) >> 1], keys[-1])
            for key1 in min_mid_max:
                for lo in range(key1 - 1, key1 + 2):
                    # Test one-sided range iterators.
                    goodkeys = [k for k in keys if lo <= k]
                    got = t.iterkeys(lo)
                    self.assertEqual(goodkeys, list(got))

                    goodvalues = [t[k] for k in goodkeys]
                    got = t.itervalues(lo)
                    self.assertEqual(goodvalues, list(got))

                    gooditems = list(zip(goodkeys, goodvalues))
                    got = t.iteritems(lo)
                    self.assertEqual(gooditems, list(got))

                    for key2 in min_mid_max:
                        for hi in range(key2 - 1, key2 + 2):
                            goodkeys = [k for k in keys if lo <= k <= hi]
                            got = t.iterkeys(min=lo, max=hi)
                            self.assertEqual(goodkeys, list(got))

                            goodvalues = [t[k] for k in goodkeys]
                            got = t.itervalues(lo, max=hi)
                            self.assertEqual(goodvalues, list(got))

                            gooditems = list(zip(goodkeys, goodvalues))
                            got = t.iteritems(max=hi, min=lo)
                            self.assertEqual(gooditems, list(got))

    def testBadUpdateTupleSize(self):
        # This one silently ignored the excess in Zope3.
        t = self._makeOne()
        self.assertRaises(TypeError, t.update, [(1, 2, 3)])

        # This one dumped core in Zope3.
        self.assertRaises(TypeError, t.update, [(1,)])

        # This one should simply succeed.
        t.update([(1, 2)])
        self.assertEqual(list(t.items()), [(1, 2)])

    def testSimpleExclusivRanges(self):
        def identity(x):
            return x
        def dup(x):
            return [(y, y) for y in x]

        for methodname, f in (("keys", identity),
                              ("values", identity),
                              ("items", dup),
                              ("iterkeys", identity),
                              ("itervalues", identity),
                              ("iteritems", dup)):

            t = self._makeOne()
            meth = getattr(t, methodname, None)
            if meth is None:
                continue

            self.assertEqual(list(meth()), [])
            self.assertEqual(list(meth(excludemin=True)), [])
            self.assertEqual(list(meth(excludemax=True)), [])
            self.assertEqual(list(meth(excludemin=True, excludemax=True)), [])

            self._populate(t, 1)
            self.assertEqual(list(meth()), f([0]))
            self.assertEqual(list(meth(excludemin=True)), [])
            self.assertEqual(list(meth(excludemax=True)), [])
            self.assertEqual(list(meth(excludemin=True, excludemax=True)), [])

            t.clear()
            self._populate(t, 2)
            self.assertEqual(list(meth()), f([0, 1]))
            self.assertEqual(list(meth(excludemin=True)), f([1]))
            self.assertEqual(list(meth(excludemax=True)), f([0]))
            self.assertEqual(list(meth(excludemin=True, excludemax=True)), [])

            t.clear()
            self._populate(t, 3)
            self.assertEqual(list(meth()), f([0, 1, 2]))
            self.assertEqual(list(meth(excludemin=True)), f([1, 2]))
            self.assertEqual(list(meth(excludemax=True)), f([0, 1]))
            self.assertEqual(list(meth(excludemin=True, excludemax=True)),
                            f([1]))
            self.assertEqual(list(meth(-1, 3, excludemin=True,
                                       excludemax=True)),
                             f([0, 1, 2]))
            self.assertEqual(list(meth(0, 3, excludemin=True,
                                       excludemax=True)),
                             f([1, 2]))
            self.assertEqual(list(meth(-1, 2, excludemin=True,
                                       excludemax=True)),
                             f([0, 1]))
            self.assertEqual(list(meth(0, 2, excludemin=True,
                                       excludemax=True)),
                             f([1]))

    def testSetdefault(self):
        t = self._makeOne()

        self.assertEqual(t.setdefault(1, 2), 2)
        # That should also have associated 1 with 2 in the tree.
        self.assertTrue(1 in t)
        self.assertEqual(t[1], 2)
        # And trying to change it again should have no effect.
        self.assertEqual(t.setdefault(1, 666), 2)
        self.assertEqual(t[1], 2)

        # Not enough arguments.
        self.assertRaises(TypeError, t.setdefault)
        self.assertRaises(TypeError, t.setdefault, 1)
        # Too many arguments.
        self.assertRaises(TypeError, t.setdefault, 1, 2, 3)


    def testPop(self):
        t = self._makeOne()

        # Empty container.
        # If no default given, raises KeyError.
        self.assertRaises(KeyError, t.pop, 1)
        # But if default given, returns that instead.
        self.assertEqual(t.pop(1, 42), 42)

        t[1] = 3
        # KeyError when key is not in container and default is not passed.
        self.assertRaises(KeyError, t.pop, 5)
        self.assertEqual(list(t.items()), [(1, 3)])
        # If key is in container, returns the value and deletes the key.
        self.assertEqual(t.pop(1), 3)
        self.assertEqual(len(t), 0)

        # If key is present, return value bypassing default.
        t[1] = 3
        self.assertEqual(t.pop(1, 7), 3)
        self.assertEqual(len(t), 0)

        # Pop only one item.
        t[1] = 3
        t[2] = 4
        self.assertEqual(len(t), 2)
        self.assertEqual(t.pop(1), 3)
        self.assertEqual(len(t), 1)
        self.assertEqual(t[2], 4)
        self.assertEqual(t.pop(1, 3), 3)

        # Too few arguments.
        self.assertRaises(TypeError, t.pop)
        # Too many arguments.
        self.assertRaises(TypeError, t.pop, 1, 2, 3)

class BTreeTests(MappingBase):
    # Tests common to all BTrees

    def _getTargetClass(self):
        # Most of the subclasses override _makeOne and not
        # _getTargetClass, so we can get the type that way.
        # TODO: This could change for less repetition in the subclasses,
        # using the name of the class to import the module and find
        # the type.
        if type(self)._makeOne is not BTreeTests._makeOne:
            return type(self._makeOne())
        raise NotImplementedError()

    def _makeOne(self, *args):
        return self._getTargetClass()(*args)

    def _checkIt(self, t):
        from BTrees.check import check
        t._check()
        check(t)

    def testDeleteNoChildrenWorks(self):
        t = self._makeOne()
        t[5] = 6
        t[2] = 10
        t[6] = 12
        t[1] = 100
        t[3] = 200
        t[10] = 500
        t[4] = 99
        del t[4]
        diff = lsubtract(t.keys(), [1,2,3,5,6,10])
        self.assertEqual(diff , [], diff)
        self._checkIt(t)

    def testDeleteOneChildWorks(self):
        t = self._makeOne()
        t[5] = 6
        t[2] = 10
        t[6] = 12
        t[1] = 100
        t[3] = 200
        t[10] = 500
        t[4] = 99
        del t[3]
        diff = lsubtract(t.keys(), [1,2,4,5,6,10])
        self.assertEqual(diff , [], diff)
        self._checkIt(t)

    def testDeleteTwoChildrenNoInorderSuccessorWorks(self):
        t = self._makeOne()
        t[5] = 6
        t[2] = 10
        t[6] = 12
        t[1] = 100
        t[3] = 200
        t[10] = 500
        t[4] = 99
        del t[2]
        diff = lsubtract(t.keys(), [1,3,4,5,6,10])
        self.assertEqual(diff , [], diff)
        self._checkIt(t)

    def testDeleteTwoChildrenInorderSuccessorWorks(self):
        # 7, 3, 8, 1, 5, 10, 6, 4 -- del 3
        t = self._makeOne()
        t[7] = 6
        t[3] = 10
        t[8] = 12
        t[1] = 100
        t[5] = 200
        t[10] = 500
        t[6] = 99
        t[4] = 150
        del t[3]
        diff = lsubtract(t.keys(), [1,4,5,6,7,8,10])
        self.assertEqual(diff , [], diff)
        self._checkIt(t)

    def testDeleteRootWorks(self):
        # 7, 3, 8, 1, 5, 10, 6, 4 -- del 7
        t = self._makeOne()
        t[7] = 6
        t[3] = 10
        t[8] = 12
        t[1] = 100
        t[5] = 200
        t[10] = 500
        t[6] = 99
        t[4] = 150
        del t[7]
        diff = lsubtract(t.keys(), [1,3,4,5,6,8,10])
        self.assertEqual(diff , [], diff)
        self._checkIt(t)

    def testRandomNonOverlappingInserts(self):
        import random
        t = self._makeOne()
        added = {}
        r = list(range(100))
        for x in r:
            k = random.choice(r)
            if k not in added:
                t[k] = x
                added[k] = 1
        addl = sorted(added.keys())
        diff = lsubtract(list(t.keys()), addl)
        self.assertEqual(diff , [], (diff, addl, list(t.keys())))
        self._checkIt(t)

    def testRandomOverlappingInserts(self):
        import random
        t = self._makeOne()
        added = {}
        r = list(range(100))
        for x in r:
            k = random.choice(r)
            t[k] = x
            added[k] = 1
        addl = sorted(added.keys())
        diff = lsubtract(t.keys(), addl)
        self.assertEqual(diff , [], diff)
        self._checkIt(t)

    def testRandomDeletes(self):
        import random
        t = self._makeOne()
        r = list(range(1000))
        added = []
        for x in r:
            k = random.choice(r)
            t[k] = x
            added.append(k)
        deleted = []
        for x in r:
            k = random.choice(r)
            if k in t:
                self.assertTrue(k in t)
                del t[k]
                deleted.append(k)
                if k in t:
                    self.fail( "had problems deleting %s" % k )
        badones = []
        for x in deleted:
            if x in t:
                badones.append(x)
        self.assertEqual(badones , [], (badones, added, deleted))
        self._checkIt(t)

    def testTargetedDeletes(self):
        import random
        t = self._makeOne()
        r = list(range(1000))
        for x in r:
            k = random.choice(r)
            t[k] = x
        for x in r:
            try:
                del t[x]
            except KeyError:
                pass
        self.assertEqual(realseq(t.keys()) , [], realseq(t.keys()))
        self._checkIt(t)

    def testPathologicalRightBranching(self):
        t = self._makeOne()
        r = list(range(1000))
        for x in r:
            t[x] = 1
        self.assertEqual(realseq(t.keys()) , r, realseq(t.keys()))
        for x in r:
            del t[x]
        self.assertEqual(realseq(t.keys()) , [], realseq(t.keys()))
        self._checkIt(t)

    def testPathologicalLeftBranching(self):
        t = self._makeOne()
        r = list(range(1000))
        revr = list(reversed(r[:]))
        for x in revr:
            t[x] = 1
        self.assertEqual(realseq(t.keys()) , r, realseq(t.keys()))

        for x in revr:
            del t[x]
        self.assertEqual(realseq(t.keys()) , [], realseq(t.keys()))
        self._checkIt(t)

    def testSuccessorChildParentRewriteExerciseCase(self):
        t = self._makeOne()
        add_order = [
            85, 73, 165, 273, 215, 142, 233, 67, 86, 166, 235, 225, 255,
            73, 175, 171, 285, 162, 108, 28, 283, 258, 232, 199, 260,
            298, 275, 44, 261, 291, 4, 181, 285, 289, 216, 212, 129,
            243, 97, 48, 48, 159, 22, 285, 92, 110, 27, 55, 202, 294,
            113, 251, 193, 290, 55, 58, 239, 71, 4, 75, 129, 91, 111,
            271, 101, 289, 194, 218, 77, 142, 94, 100, 115, 101, 226,
            17, 94, 56, 18, 163, 93, 199, 286, 213, 126, 240, 245, 190,
            195, 204, 100, 199, 161, 292, 202, 48, 165, 6, 173, 40, 218,
            271, 228, 7, 166, 173, 138, 93, 22, 140, 41, 234, 17, 249,
            215, 12, 292, 246, 272, 260, 140, 58, 2, 91, 246, 189, 116,
            72, 259, 34, 120, 263, 168, 298, 118, 18, 28, 299, 192, 252,
            112, 60, 277, 273, 286, 15, 263, 141, 241, 172, 255, 52, 89,
            127, 119, 255, 184, 213, 44, 116, 231, 173, 298, 178, 196,
            89, 184, 289, 98, 216, 115, 35, 132, 278, 238, 20, 241, 128,
            179, 159, 107, 206, 194, 31, 260, 122, 56, 144, 118, 283,
            183, 215, 214, 87, 33, 205, 183, 212, 221, 216, 296, 40,
            108, 45, 188, 139, 38, 256, 276, 114, 270, 112, 214, 191,
            147, 111, 299, 107, 101, 43, 84, 127, 67, 205, 251, 38, 91,
            297, 26, 165, 187, 19, 6, 73, 4, 176, 195, 90, 71, 30, 82,
            139, 210, 8, 41, 253, 127, 190, 102, 280, 26, 233, 32, 257,
            194, 263, 203, 190, 111, 218, 199, 29, 81, 207, 18, 180,
            157, 172, 192, 135, 163, 275, 74, 296, 298, 265, 105, 191,
            282, 277, 83, 188, 144, 259, 6, 173, 81, 107, 292, 231,
            129, 65, 161, 113, 103, 136, 255, 285, 289, 1
            ]
        delete_order = [
            276, 273, 12, 275, 2, 286, 127, 83, 92, 33, 101, 195,
            299, 191, 22, 232, 291, 226, 110, 94, 257, 233, 215, 184,
            35, 178, 18, 74, 296, 210, 298, 81, 265, 175, 116, 261,
            212, 277, 260, 234, 6, 129, 31, 4, 235, 249, 34, 289, 105,
            259, 91, 93, 119, 7, 183, 240, 41, 253, 290, 136, 75, 292,
            67, 112, 111, 256, 163, 38, 126, 139, 98, 56, 282, 60, 26,
            55, 245, 225, 32, 52, 40, 271, 29, 252, 239, 89, 87, 205,
            213, 180, 97, 108, 120, 218, 44, 187, 196, 251, 202, 203,
            172, 28, 188, 77, 90, 199, 297, 282, 141, 100, 161, 216,
            73, 19, 17, 189, 30, 258
            ]
        for x in add_order:
            t[x] = 1
        for x in delete_order:
            try:
                del t[x]
            except KeyError:
                if x in t:
                    self.assertEqual(1,2,"failed to delete %s" % x)
        self._checkIt(t)

    def testRangeSearchAfterSequentialInsert(self):
        t = self._makeOne()
        r = range(100)
        for x in r:
            t[x] = 0
        diff = lsubtract(list(t.keys(0, 100)), r)
        self.assertEqual(diff , [], diff)
        # The same thing with no bounds
        diff = lsubtract(list(t.keys(None, None)), r)
        self.assertEqual(diff , [], diff)
        # The same thing with each bound set and the other
        # explicitly None
        diff = lsubtract(list(t.keys(0, None)), r)
        self.assertEqual(diff , [], diff)
        diff = lsubtract(list(t.keys(None,100)), r)
        self.assertEqual(diff , [], diff)
        self._checkIt(t)

    def testRangeSearchAfterRandomInsert(self):
        import random
        t = self._makeOne()
        r = range(100)
        a = {}
        for x in r:
            rnd = random.choice(r)
            t[rnd] = 0
            a[rnd] = 0
        diff = lsubtract(list(t.keys(0, 100)), a.keys())
        self.assertEqual(diff, [], diff)
        self._checkIt(t)

    def testPathologicalRangeSearch(self):
        t = self._makeOne()
        # Build a 2-level tree with at least two buckets.
        for i in range(200):
            t[i] = i
        items, dummy = t.__getstate__()
        self.assertTrue(len(items) > 2)   # at least two buckets and a key
        # All values in the first bucket are < firstkey.  All in the
        # second bucket are >= firstkey, and firstkey is the first key in
        # the second bucket.
        firstkey = items[1]
        therange = t.keys(-1, firstkey)
        self.assertEqual(len(therange), firstkey + 1)
        self.assertEqual(list(therange), list(range(firstkey + 1)))
        # Now for the tricky part.  If we delete firstkey, the second bucket
        # loses its smallest key, but firstkey remains in the BTree node.
        # If we then do a high-end range search on firstkey, the BTree node
        # directs us to look in the second bucket, but there's no longer any
        # key <= firstkey in that bucket.  The correct answer points to the
        # end of the *first* bucket.  The algorithm has to be smart enough
        # to "go backwards" in the BTree then; if it doesn't, it will
        # erroneously claim that the range is empty.
        del t[firstkey]
        therange = t.keys(min=-1, max=firstkey)
        self.assertEqual(len(therange), firstkey)
        self.assertEqual(list(therange), list(range(firstkey)))
        self._checkIt(t)

    def testInsertMethod(self):
        t = self._makeOne()
        t[0] = 1
        self.assertEqual(t.insert(0, 1) , 0)
        self.assertEqual(t.insert(1, 1) , 1)
        self.assertEqual(lsubtract(list(t.keys()), [0,1]) , [])
        self._checkIt(t)

    def testDamagedIterator(self):
        # A cute one from Steve Alexander.  This caused the BTreeItems
        # object to go insane, accessing memory beyond the allocated part
        # of the bucket.  If it fails, the symptom is either a C-level
        # assertion error (if the BTree code was compiled without NDEBUG),
        # or most likely a segfault (if the BTree code was compiled with
        # NDEBUG).
        t = self._makeOne()
        self._populate(t, 10)
        # In order for this to fail, it's important that k be a "lazy"
        # iterator, referring to the BTree by indirect position (index)
        # instead of a fully materialized list.  Then the position can
        # end up pointing into trash memory, if the bucket pointed to
        # shrinks.
        k = t.keys()
        for dummy in range(20):
            try:
                del t[k[0]]
            except RuntimeError as detail:
                self.assertEqual(str(detail), "the bucket being iterated "
                                              "changed size")
                break
            except KeyError as v:
                # The Python implementation behaves very differently and
                # gives a key error in this situation. It can't mess up
                # memory and can't readily detect changes to underlying buckets
                # in any sane way.
                self.assertEqual(str(v), str(k[0]))
        self._checkIt(t)

    def testAddTwoSetsChanged(self):
        # A bug in the BTree Python implementation once
        # caused adding a second item to a tree to fail
        # to set _p_changed (adding the first item sets it because
        # the _firstbucket gets set, but the second item only grew the
        # existing bucket)
        t = self._makeOne()
        # Note that for the property to actually hold, we have to fake a
        # _p_jar and _p_oid
        t._p_oid = b'\0\0\0\0\0'
        class Jar(object):
            def __init__(self):
                self._cache = self
                self.registered = None

            def mru(self, arg):
                pass
            def readCurrent(self, arg):
                pass
            def register(self, arg):
                self.registered = arg

        t._p_jar = Jar()
        t[1] = 3
        # reset these, setting _firstbucket triggered a change
        t._p_changed = False
        t._p_jar.registered = None
        t[2] = 4
        self.assertTrue(t._p_changed)
        self.assertEqual(t, t._p_jar.registered)

        # Setting the same key to a different value also triggers a change
        t._p_changed = False
        t._p_jar.registered = None
        t[2] = 5
        self.assertTrue(t._p_changed)
        self.assertEqual(t, t._p_jar.registered)

        # Likewise with only a single value
        t = self._makeOne()
        t._p_oid = b'\0\0\0\0\0'
        t._p_jar = Jar()
        t[1] = 3
        # reset these, setting _firstbucket triggered a change
        t._p_changed = False
        t._p_jar.registered = None

        t[1] = 6
        self.assertTrue(t._p_changed)
        self.assertEqual(t, t._p_jar.registered)

    def testRemoveInSmallMapSetsChanged(self):
        # A bug in the BTree Python implementation once caused
        # deleting from a small btree to set _p_changed.
        # There must be at least two objects so that _firstbucket doesn't
        # get set
        t = self._makeOne()
        # Note that for the property to actually hold, we have to fake a
        # _p_jar and _p_oid
        t._p_oid = b'\0\0\0\0\0'
        class Jar(object):
            def __init__(self):
                self._cache = self
                self.registered = None

            def mru(self, arg):
                pass
            def readCurrent(self, arg):
                pass
            def register(self, arg):
                self.registered = arg

        t._p_jar = Jar()
        t[0] = 1
        t[1] = 2
        # reset these, setting _firstbucket triggered a change
        t._p_changed = False
        t._p_jar.registered = None

        # now remove the second value
        del t[1]
        self.assertTrue(t._p_changed)
        self.assertEqual(t, t._p_jar.registered)

    def test_legacy_py_pickle(self):
        # Issue #2
        # If we have a pickle that includes the 'Py' suffix,
        # it (unfortunately) unpickles to the python type. But
        # new pickles never produce that.
        import pickle
        made_one = self._makeOne()

        for proto in (1, 2):
            s = pickle.dumps(made_one, proto)
            # It's not legacy
            assert b'TreePy\n' not in s, repr(s)
            # \np for protocol 1, \nq for proto 2,
            assert b'Tree\np' in s or b'Tree\nq' in s, repr(s)

            # Now make it pseudo-legacy
            legacys = s.replace(b'Tree\np', b'TreePy\np').replace(b'Tree\nq', b'TreePy\nq')

            # It loads up as the specified class
            loaded_one = pickle.loads(legacys)

            # It still functions and can be dumped again, as the original class
            s2 = pickle.dumps(loaded_one, proto)
            self.assertTrue(b'Py' not in s2)
            self.assertEqual(s2, s)


class NormalSetTests(Base):
    # Test common to all set types

    def _populate(self, t, l):
        # Make some data
        t.update(range(l))

    def testShortRepr(self):
        t = self._makeOne()
        for i in range(5):
            t.add(i)
        r = repr(t)
        # Make sure the repr is **not* 10000 bytes long for a shrort bucket.
        # (the buffer must be terminated when copied).
        self.assertTrue(len(r) < 10000)
        # Make sure the repr is human readable, unless it's a tree
        if 'TreeSet' not in r:
            self.assertTrue(r.endswith("Set(%r)" % t.keys()))
        else:
            self.assertEqual(r[:7], '<BTrees', r)
        # Make sure it's the same between Python and C
        self.assertTrue('Py' not in r)


    def testInsertReturnsValue(self):
        t = self._makeOne()
        self.assertEqual(t.insert(5) , 1)
        self.assertEqual(t.add(4) , 1)

    def testDuplicateInsert(self):
        t = self._makeOne()
        t.insert(5)
        self.assertEqual(t.insert(5) , 0)
        self.assertEqual(t.add(5) , 0)

    def testInsert(self):
        from .._compat import PY2
        t = self._makeOne()
        t.insert(1)
        if PY2:
            self.assertTrue(t.has_key(1))
        self.assertTrue(1 in t)
        self.assertTrue(2 not in t)

    def testBigInsert(self):
        from .._compat import PY2
        from .._compat import xrange
        t = self._makeOne()
        r = xrange(10000)
        for x in r:
            t.insert(x)
        for x in r:
            if PY2:
                self.assertTrue(t.has_key(x))
            self.assertTrue(x in t)

    def testRemoveSucceeds(self):
        from .._compat import xrange
        t = self._makeOne()
        r = xrange(10000)
        for x in r: t.insert(x)
        for x in r: t.remove(x)

    def testRemoveFails(self):
        self.assertRaises(KeyError, self._removenonexistent)

    def _removenonexistent(self):
        self._makeOne().remove(1)

    def testHasKeyFails(self):
        from .._compat import PY2
        t = self._makeOne()
        if PY2:
            self.assertTrue(not t.has_key(1))
        self.assertTrue(1 not in t)

    def testKeys(self):
        from .._compat import xrange
        t = self._makeOne()
        r = xrange(1000)
        for x in r:
            t.insert(x)
        diff = lsubtract(t.keys(), r)
        self.assertEqual(diff, [])
        diff = lsubtract(t.keys(None,None), r)
        self.assertEqual(diff, [])


    def testClear(self):
        from .._compat import xrange
        t = self._makeOne()
        r = xrange(1000)
        for x in r: t.insert(x)
        t.clear()
        diff = lsubtract(t.keys(), [])
        self.assertEqual(diff , [], diff)

    def testMaxKeyMinKey(self):
        t = self._makeOne()
        t.insert(1)
        t.insert(2)
        t.insert(3)
        t.insert(8)
        t.insert(5)
        t.insert(10)
        t.insert(6)
        t.insert(4)
        self.assertEqual(t.maxKey() , 10)
        self.assertEqual(t.maxKey(None) , 10)
        self.assertEqual(t.maxKey(6) , 6)
        self.assertEqual(t.maxKey(9) , 8)
        self.assertEqual(t.minKey() , 1)
        self.assertEqual(t.minKey(None) , 1)
        self.assertEqual(t.minKey(3) , 3)
        self.assertEqual(t.minKey(9) , 10)
        self.assertTrue(t.minKey() in t)
        self.assertTrue(t.minKey()-1 not in t)
        self.assertTrue(t.maxKey() in t)
        self.assertTrue(t.maxKey()+1 not in t)

        try:
            t.maxKey(t.minKey() - 1)
        except ValueError as err:
            self.assertEqual(str(err), "no key satisfies the conditions")
        else:
            self.fail("expected ValueError")

        try:
            t.minKey(t.maxKey() + 1)
        except ValueError as err:
            self.assertEqual(str(err), "no key satisfies the conditions")
        else:
            self.fail("expected ValueError")

    def testUpdate(self):
        import random
        t = self._makeOne()
        d={}
        l=[]
        for i in range(10000):
            k=random.randrange(-2000, 2001)
            d[k]=i
            l.append(k)

        items = sorted(d.keys())

        t.update(l)
        self.assertEqual(list(t.keys()), items)

    def testEmptyRangeSearches(self):
        t = self._makeOne()
        t.update([1, 5, 9])
        self.assertEqual(list(t.keys(-6,-4)), [], list(t.keys(-6,-4)))
        self.assertEqual(list(t.keys(2,4)), [], list(t.keys(2,4)))
        self.assertEqual(list(t.keys(6,8)), [], list(t.keys(6,8)))
        self.assertEqual(list(t.keys(10,12)), [], list(t.keys(10,12)))
        self.assertEqual(list(t.keys(9,1)), [], list(t.keys(9,1)))

        # For IITreeSets, this one was returning 31 for len(keys), and
        # list(keys) produced a list with 100 elements.
        t.clear()
        t.update(range(300))
        keys = t.keys(200, 50)
        self.assertEqual(len(keys), 0)
        self.assertEqual(list(keys), [])

        keys = t.keys(max=50, min=200)
        self.assertEqual(len(keys), 0)
        self.assertEqual(list(keys), [])

    def testSlicing(self):
        # Test that slicing of .keys() works exactly the same way as slicing
        # a Python list with the same contents.
        t = self._makeOne()
        for n in range(10):
            t.clear()
            self.assertEqual(len(t), 0)

            keys = range(10*n, 11*n)
            t.update(keys)
            self.assertEqual(len(t), n)

            kslice = t.keys()
            self.assertEqual(len(list(kslice)), n)

            # Test whole-structure slices.
            x = kslice[:]
            self.assertEqual(list(x), list(keys[:]))

            for lo in range(-2*n, 2*n+1):
                # Test one-sided slices.
                x = kslice[:lo]
                self.assertEqual(list(x), list(keys[:lo]))
                x = kslice[lo:]
                self.assertEqual(list(x), list(keys[lo:]))

                for hi in range(-2*n, 2*n+1):
                    # Test two-sided slices.
                    x = kslice[lo:hi]
                    self.assertEqual(list(x), list(keys[lo:hi]))

    def testIterator(self):
        t = self._makeOne()

        for keys in [], [-2], [1, 4], list(range(-170, 2000, 6)):
            t.clear()
            t.update(keys)

            self.assertEqual(list(t), keys)

            x = []
            for k in t:
                x.append(k)
            self.assertEqual(x, keys)

            it = iter(t)
            self.assertTrue(it is iter(it))
            x = []
            try:
                while 1:
                    x.append(next(it))
            except StopIteration:
                pass
            self.assertEqual(x, keys)

    def testRemoveInSmallSetSetsChanged(self):
        # A bug in the BTree TreeSet Python implementation once caused
        # deleting an item in a small set to fail to set _p_changed.
        # There must be at least two objects so that _firstbucket doesn't
        # get set
        t = self._makeOne()
        # Note that for the property to actually hold, we have to fake a
        # _p_jar and _p_oid
        t._p_oid = b'\0\0\0\0\0'
        class Jar(object):
            def __init__(self):
                self._cache = self
                self.registered = None

            def mru(self, arg):
                pass
            def readCurrent(self, arg):
                pass
            def register(self, arg):
                self.registered = arg

        t._p_jar = Jar()
        t.add(0)
        t.add(1)
        # reset these, setting _firstbucket triggered a change
        t._p_changed = False
        t._p_jar.registered = None

        # now remove the second value
        t.remove(1)
        self.assertTrue(t._p_changed)
        self.assertEqual(t, t._p_jar.registered)

    def testAddingOneSetsChanged(self):
        # A bug in the BTree Set Python implementation once caused
        # adding an object not to set _p_changed
        t = self._makeOne()
        # Note that for the property to actually hold, we have to fake a
        # _p_jar and _p_oid
        t._p_oid = b'\0\0\0\0\0'
        class Jar(object):
            def __init__(self):
                self._cache = self
                self.registered = None

            def mru(self, arg):
                pass
            def readCurrent(self, arg):
                pass
            def register(self, arg):
                self.registered = arg

        t._p_jar = Jar()
        t.add(0)
        self.assertTrue(t._p_changed)
        self.assertEqual(t, t._p_jar.registered)

        # Whether or not doing `t.add(0)` again would result in
        # _p_changed being set depends on whether this is a TreeSet or a plain Set

class ExtendedSetTests(NormalSetTests):

    def testLen(self):
        from .._compat import xrange
        t = self._makeOne()
        r = xrange(10000)
        for x in r: t.insert(x)
        self.assertEqual(len(t) , 10000, len(t))

    def testGetItem(self):
        from .._compat import xrange
        t = self._makeOne()
        r = xrange(10000)
        for x in r: t.insert(x)
        for x in r:
            self.assertEqual(t[x] , x)


class InternalKeysMappingTest(object):
    # There must not be any internal keys not in the BTree

    def _makeOne(self):
        return self._getTargetClass()()

    def add_key(self, tree, key):
        tree[key] = key

    @_skip_wo_ZODB
    def test_internal_keys_after_deletion(self):
        # Make sure when a key's deleted, it's not an internal key
        #
        # We'll leverage __getstate__ to introspect the internal structures.
        #
        # We need to check BTrees with BTree children as well as BTrees
        # with bucket children.
        import transaction
        from ZODB.MappingStorage import DB
        db = DB()
        conn = db.open()

        tree = conn.root.tree = self._makeOne()
        i = 0

        # Grow the btree until we have multiple buckets
        while 1:
            i += 1
            self.add_key(tree, i)
            data = tree.__getstate__()[0]
            if len(data) >= 3:
                break

        transaction.commit()

        # Now, delete the internal key and make sure it's really gone
        key = data[1]
        del tree[key]
        data = tree.__getstate__()[0]
        self.assertTrue(data[1] != key)

        # The tree should have changed:
        self.assertTrue(tree._p_changed)

        # Grow the btree until we have multiple levels
        while 1:
            i += 1
            self.add_key(tree, i)
            data = tree.__getstate__()[0]
            if data[0].__class__ == tree.__class__:
                assert len(data[2].__getstate__()[0]) >= 3
                break

        # Now, delete the internal key and make sure it's really gone
        key = data[1]
        del tree[key]
        data = tree.__getstate__()[0]
        self.assertTrue(data[1] != key)

        transaction.abort()
        db.close()


class InternalKeysSetTest(object):
    # There must not be any internal keys not in the TreeSet

    def add_key(self, tree, key):
        tree.add(key)


class ModuleTest(object):
    # test for presence of generic names in module
    prefix = None
    def _getModule(self):
        pass
    def testNames(self):
        names = ['Bucket', 'BTree', 'Set', 'TreeSet']
        for name in names:
            klass = getattr(self._getModule(), name)
            self.assertEqual(klass.__module__, self._getModule().__name__)
            self.assertTrue(klass is getattr(self._getModule(),
                                          self.prefix + name))
        # BBB for zope.app.security ZCML :(
        pfx_iter = self.prefix + 'TreeIterator'
        klass = getattr(self._getModule(), pfx_iter)
        self.assertEqual(klass.__module__, self._getModule().__name__)

    def testModuleProvides(self):
        from zope.interface.verify import verifyObject
        verifyObject(self._getInterface(), self._getModule())

    def testFamily(self):
        import BTrees
        if self.prefix == 'OO':
            self.assertTrue(
                getattr(self._getModule(), 'family', self) is self)
        elif 'L' in self.prefix:
            self.assertTrue(self._getModule().family is BTrees.family64)
        elif 'I' in self.prefix:
            self.assertTrue(self._getModule().family is BTrees.family32)


class TypeTest(object):
    # tests of various type errors

    def testBadTypeRaises(self):
        self.assertRaises(TypeError, self._stringraises)
        self.assertRaises(TypeError, self._floatraises)
        self.assertRaises(TypeError, self._noneraises)


class I_SetsBase(object):

    def testBadBadKeyAfterFirst(self):
        t = self._makeOne()
        self.assertRaises(TypeError, t.__class__, [1, ''])
        self.assertRaises(TypeError, t.update, [1, ''])

    def testNonIntegerInsertRaises(self):
        self.assertRaises(TypeError,self._insertstringraises)
        self.assertRaises(TypeError,self._insertfloatraises)
        self.assertRaises(TypeError,self._insertnoneraises)

    def _insertstringraises(self):
        self._makeOne().insert('a')

    def _insertfloatraises(self):
        self._makeOne().insert(1.4)

    def _insertnoneraises(self):
        self._makeOne().insert(None)


LARGEST_32_BITS = 2147483647
SMALLEST_32_BITS = -LARGEST_32_BITS - 1

SMALLEST_POSITIVE_33_BITS = LARGEST_32_BITS + 1
LARGEST_NEGATIVE_33_BITS = SMALLEST_32_BITS - 1

LARGEST_64_BITS = 0x7fffffffffffffff
SMALLEST_64_BITS = -LARGEST_64_BITS - 1

SMALLEST_POSITIVE_65_BITS = LARGEST_64_BITS + 1
LARGEST_NEGATIVE_65_BITS = SMALLEST_64_BITS - 1


class TestLongIntSupport:

    def getTwoValues(self):
        # Return two distinct values; these must compare as un-equal.
        #
        # These values must be usable as values.
        return object(), object()

    def getTwoKeys(self):
        # Return two distinct values, these must compare as un-equal.
        #
        #These values must be usable as keys.
        return 0, 1

    def _set_value(self, key, value):
        t = self._makeOne()
        t[key] = value


class TestLongIntKeys(TestLongIntSupport):

    def _makeLong(self, v):
        try:
            return long(v)
        except NameError: #pragma NO COVER Py3k
            return int(v)

    def testLongIntKeysWork(self):
        from BTrees.IIBTree import using64bits
        if not using64bits:
            return
        t = self._makeOne()
        o1, o2 = self.getTwoValues()
        assert o1 != o2

        # Test some small key values first:
        zero_long = self._makeLong(0)
        t[zero_long] = o1
        self.assertEqual(t[0], o1)
        t[0] = o2
        self.assertEqual(t[zero_long], o2)
        self.assertEqual(list(t.keys()), [0])
        self.assertEqual(list(t.keys(None,None)), [0])

        # Test some large key values too:
        k1 = SMALLEST_POSITIVE_33_BITS
        k2 = LARGEST_64_BITS
        k3 = SMALLEST_64_BITS
        t[k1] = o1
        t[k2] = o2
        t[k3] = o1
        self.assertEqual(t[k1], o1)
        self.assertEqual(t[k2], o2)
        self.assertEqual(t[k3], o1)
        self.assertEqual(list(t.keys()), [k3, 0, k1, k2])
        self.assertEqual(list(t.keys(k3,None)), [k3, 0, k1, k2])
        self.assertEqual(list(t.keys(None,k2)), [k3, 0, k1, k2])

    def testLongIntKeysOutOfRange(self):
        from BTrees.IIBTree import using64bits
        if not using64bits:
            return
        o1, o2 = self.getTwoValues()
        self.assertRaises(
            ValueError,
            self._set_value, SMALLEST_POSITIVE_65_BITS, o1)
        self.assertRaises(
            ValueError,
            self._set_value, LARGEST_NEGATIVE_65_BITS, o1)

class TestLongIntValues(TestLongIntSupport):

    def testLongIntValuesWork(self):
        from BTrees.IIBTree import using64bits
        if not using64bits:
            return
        t = self._makeOne()
        keys = sorted(self.getTwoKeys())
        k1, k2 = keys
        assert k1 != k2

        # This is the smallest positive integer that requires 33 bits:
        v1 = SMALLEST_POSITIVE_33_BITS
        v2 = v1 + 1

        t[k1] = v1
        t[k2] = v2
        self.assertEqual(t[k1], v1)
        self.assertEqual(t[k2], v2)
        self.assertEqual(list(t.values()), [v1, v2])
        self.assertEqual(list(t.values(None,None)), [v1, v2])

    def testLongIntValuesOutOfRange(self):
        from BTrees.IIBTree import using64bits
        if not using64bits:
            return
        k1, k2 = self.getTwoKeys()
        self.assertRaises(
            ValueError,
            self._set_value, k1, SMALLEST_POSITIVE_65_BITS)
        self.assertRaises(
            ValueError,
            self._set_value, k1, LARGEST_NEGATIVE_65_BITS)

# Given a mapping builder (IIBTree, OOBucket, etc), return a function
# that builds an object of that type given only a list of keys.
def makeBuilder(mapbuilder):
    def result(keys=[], mapbuilder=mapbuilder):
        return mapbuilder(list(zip(keys, keys)))
    return result

# Subclasses have to set up:
#     builders() - function returning functions to build inputs,
#     each returned callable tkes an optional keys arg
#     intersection, union, difference - set to the type-correct versions
class SetResult(object):
    def setUp(self):
        self.Akeys = [1,    3,    5, 6   ]
        self.Bkeys = [   2, 3, 4,    6, 7]
        self.As = [makeset(self.Akeys) for makeset in self.builders()]
        self.Bs = [makeset(self.Bkeys) for makeset in self.builders()]
        self.emptys = [makeset() for makeset in self.builders()]

    # Slow but obviously correct Python implementations of basic ops.
    def _union(self, x, y):
        result = list(x)
        for e in y:
            if e not in result:
                result.append(e)
        return sorted(result)

    def _intersection(self, x, y):
        result = []
        for e in x:
            if e in y:
                result.append(e)
        return result

    def _difference(self, x, y):
        result = list(x)
        for e in y:
            if e in result:
                result.remove(e)
        # Difference preserves LHS values.
        if hasattr(x, "values"):
            result = [(k, x[k]) for k in result]
        return result

    def testNone(self):
        for op in self.union, self.intersection, self.difference:
            C = op(None, None)
            self.assertTrue(C is None)

        for op in self.union, self.intersection, self.difference:
            for A in self.As:
                C = op(A, None)
                self.assertTrue(C is A)

                C = op(None, A)
                if op == self.difference:
                    self.assertTrue(C is None)
                else:
                    self.assertTrue(C is A)

    def testEmptyUnion(self):
        for A in self.As:
            for E in self.emptys:
                C = self.union(A, E)
                self.assertTrue(not hasattr(C, "values"))
                self.assertEqual(list(C), self.Akeys)

                C = self.union(E, A)
                self.assertTrue(not hasattr(C, "values"))
                self.assertEqual(list(C), self.Akeys)

    def testEmptyIntersection(self):
        for A in self.As:
            for E in self.emptys:
                C = self.intersection(A, E)
                self.assertTrue(not hasattr(C, "values"))
                self.assertEqual(list(C), [])

                C = self.intersection(E, A)
                self.assertTrue(not hasattr(C, "values"))
                self.assertEqual(list(C), [])

    def testEmptyDifference(self):
        for A in self.As:
            for E in self.emptys:
                C = self.difference(A, E)
                # Difference preserves LHS values.
                self.assertEqual(hasattr(C, "values"), hasattr(A, "values"))
                if hasattr(A, "values"):
                    self.assertEqual(list(C.items()), list(A.items()))
                else:
                    self.assertEqual(list(C), self.Akeys)

                C = self.difference(E, A)
                self.assertEqual(hasattr(C, "values"), hasattr(E, "values"))
                self.assertEqual(list(C), [])

    def testUnion(self):
        inputs = self.As + self.Bs
        for A in inputs:
            for B in inputs:
                C = self.union(A, B)
                self.assertTrue(not hasattr(C, "values"))
                self.assertEqual(list(C), self._union(A, B))

    def testIntersection(self):
        inputs = self.As + self.Bs
        for A in inputs:
            for B in inputs:
                C = self.intersection(A, B)
                self.assertTrue(not hasattr(C, "values"))
                self.assertEqual(list(C), self._intersection(A, B))

    def testDifference(self):
        inputs = self.As + self.Bs
        for A in inputs:
            for B in inputs:
                C = self.difference(A, B)
                # Difference preserves LHS values.
                self.assertEqual(hasattr(C, "values"), hasattr(A, "values"))
                want = self._difference(A, B)
                if hasattr(A, "values"):
                    self.assertEqual(list(C.items()), want)
                else:
                    self.assertEqual(list(C), want)

    def testLargerInputs(self):
        from BTrees.IIBTree import IISet
        from random import randint
        MAXSIZE = 200
        MAXVAL = 400
        for i in range(3):
            n = randint(0, MAXSIZE)
            Akeys = [randint(1, MAXVAL) for j in range(n)]
            As = [makeset(Akeys) for makeset in self.builders()]
            Akeys = IISet(Akeys)

            n = randint(0, MAXSIZE)
            Bkeys = [randint(1, MAXVAL) for j in range(n)]
            Bs = [makeset(Bkeys) for makeset in self.builders()]
            Bkeys = IISet(Bkeys)

            for op, simulator in ((self.union, self._union),
                                  (self.intersection, self._intersection),
                                  (self.difference, self._difference)):
                for A in As:
                    for B in Bs:
                        got = op(A, B)
                        want = simulator(Akeys, Bkeys)
                        self.assertEqual(list(got), want,
                                         (A, B, Akeys, Bkeys, list(got), want))

# Subclasses must set up (as class variables):
#     weightedUnion, weightedIntersection
#     builders -- sequence of constructors, taking items
#     union, intersection -- the module routines of those names
#     mkbucket -- the module bucket builder
class Weighted(object):

    def setUp(self):
        self.Aitems = [(1, 10), (3, 30),  (5, 50), (6, 60)]
        self.Bitems = [(2, 21), (3, 31), (4, 41),  (6, 61), (7, 71)]

        self.As = [make(self.Aitems) for make in self.builders()]
        self.Bs = [make(self.Bitems) for make in self.builders()]
        self.emptys = [make([]) for make in self.builders()]

        weights = []
        for w1 in -3, -1, 0, 1, 7:
            for w2 in -3, -1, 0, 1, 7:
                weights.append((w1, w2))
        self.weights = weights

    def testBothNone(self):
        for op in self.weightedUnion(), self.weightedIntersection():
            w, C = op(None, None)
            self.assertTrue(C is None)
            self.assertEqual(w, 0)

            w, C = op(None, None, 42, 666)
            self.assertTrue(C is None)
            self.assertEqual(w, 0)

    def testLeftNone(self):
        for op in self.weightedUnion(), self.weightedIntersection():
            for A in self.As + self.emptys:
                w, C = op(None, A)
                self.assertTrue(C is A)
                self.assertEqual(w, 1)

                w, C = op(None, A, 42, 666)
                self.assertTrue(C is A)
                self.assertEqual(w, 666)

    def testRightNone(self):
        for op in self.weightedUnion(), self.weightedIntersection():
            for A in self.As + self.emptys:
                w, C = op(A, None)
                self.assertTrue(C is A)
                self.assertEqual(w, 1)

                w, C = op(A, None, 42, 666)
                self.assertTrue(C is A)
                self.assertEqual(w, 42)

    # If obj is a set, return a bucket with values all 1; else return obj.
    def _normalize(self, obj):
        if isaset(obj):
            obj = self.mkbucket(list(zip(obj, [1] * len(obj))))
        return obj

    # Python simulation of weightedUnion.
    def _wunion(self, A, B, w1=1, w2=1):
        if isaset(A) and isaset(B):
            return 1, self.union()(A, B).keys()
        A = self._normalize(A)
        B = self._normalize(B)
        result = []
        for key in self.union()(A, B):
            v1 = A.get(key, 0)
            v2 = B.get(key, 0)
            result.append((key, v1*w1 + v2*w2))
        return 1, result

    def testUnion(self):
        inputs = self.As + self.Bs + self.emptys
        for A in inputs:
            for B in inputs:
                want_w, want_s = self._wunion(A, B)
                got_w, got_s = self.weightedUnion()(A, B)
                self.assertEqual(got_w, want_w)
                if isaset(got_s):
                    self.assertEqual(got_s.keys(), want_s)
                else:
                    self.assertEqual(got_s.items(), want_s)

                for w1, w2 in self.weights:
                    want_w, want_s = self._wunion(A, B, w1, w2)
                    got_w, got_s = self.weightedUnion()(A, B, w1, w2)
                    self.assertEqual(got_w, want_w)
                    if isaset(got_s):
                        self.assertEqual(got_s.keys(), want_s)
                    else:
                        self.assertEqual(got_s.items(), want_s)

    # Python simulation weightedIntersection.
    def _wintersection(self, A, B, w1=1, w2=1):
        if isaset(A) and isaset(B):
            return w1 + w2, self.intersection()(A, B).keys()
        A = self._normalize(A)
        B = self._normalize(B)
        result = []
        for key in self.intersection()(A, B):
            result.append((key, A[key]*w1 + B[key]*w2))
        return 1, result

    def testIntersection(self):
        inputs = self.As + self.Bs + self.emptys
        for A in inputs:
            for B in inputs:
                want_w, want_s = self._wintersection(A, B)
                got_w, got_s = self.weightedIntersection()(A, B)
                self.assertEqual(got_w, want_w)
                if isaset(got_s):
                    self.assertEqual(got_s.keys(), want_s)
                else:
                    self.assertEqual(got_s.items(), want_s)

                for w1, w2 in self.weights:
                    want_w, want_s = self._wintersection(A, B, w1, w2)
                    got_w, got_s = self.weightedIntersection()(A, B, w1, w2)
                    self.assertEqual(got_w, want_w)
                    if isaset(got_s):
                        self.assertEqual(got_s.keys(), want_s)
                    else:
                        self.assertEqual(got_s.items(), want_s)

# Given a set builder (like OITreeSet or OISet), return a function that
# takes a list of (key, value) pairs and builds a set out of the keys.
def itemsToSet(setbuilder):
    def result(items, setbuilder=setbuilder):
        return setbuilder([key for key, value in items])
    return result

# 'thing' is a bucket, btree, set or treeset.  Return true iff it's one of the
# latter two.
def isaset(thing):
    return not hasattr(thing, 'values')

# Subclasses must set up (as class variables):
#     multiunion, union
#     mkset, mktreeset
#     mkbucket, mkbtree
class MultiUnion(object):

    def testEmpty(self):
        self.assertEqual(len(self.multiunion([])), 0)

    def testOne(self):
        for sequence in ([3],
                         list(range(20)),
                         list(range(-10, 0, 2)) + list(range(1, 10, 2)),
                        ):
            seq1 = sequence[:]
            seq2 = list(reversed(sequence[:]))
            seqsorted = sorted(sequence[:])
            for seq in seq1, seq2, seqsorted:
                for builder in self.mkset, self.mktreeset:
                    input = builder(seq)
                    output = self.multiunion([input])
                    self.assertEqual(len(seq), len(output))
                    self.assertEqual(seqsorted, list(output))

    def testValuesIgnored(self):
        for builder in self.mkbucket, self.mkbtree:
            input = builder([(1, 2), (3, 4), (5, 6)])
            output = self.multiunion([input])
            self.assertEqual([1, 3, 5], list(output))

    def testBigInput(self):
        N = 100000
        input = self.mkset(list(range(N)))
        output = self.multiunion([input] * 10)
        self.assertEqual(len(output), N)
        self.assertEqual(output.minKey(), 0)
        self.assertEqual(output.maxKey(), N-1)
        self.assertEqual(list(output), list(range(N)))

    def testLotsOfLittleOnes(self):
        from random import shuffle
        N = 5000
        inputs = []
        mkset, mktreeset = self.mkset, self.mktreeset
        for i in range(N):
            base = i * 4 - N
            inputs.append(mkset([base, base+1]))
            inputs.append(mktreeset([base+2, base+3]))
        shuffle(inputs)
        output = self.multiunion(inputs)
        self.assertEqual(len(output), N*4)
        self.assertEqual(list(output), list(range(-N, 3*N)))

    def testFunkyKeyIteration(self):
        # The internal set iteration protocol allows "iterating over" a
        # a single key as if it were a set.
        N = 100
        union, mkset = self.union, self.mkset
        slow = mkset()
        for i in range(N):
            slow = union(slow, mkset([i]))
        fast = self.multiunion(list(range(N))) # like N distinct singleton sets
        self.assertEqual(len(slow), N)
        self.assertEqual(len(fast), N)
        self.assertEqual(list(slow), list(fast))
        self.assertEqual(list(fast), list(range(N)))


class ConflictTestBase(object):
    # Tests common to all types: sets, buckets, and BTrees

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
        except BTreesConflictError as err:
            pass
        else:
            assert 0, message
    else:
        merged = o1._p_resolveConflict(s1, s2, s3)
        assert merged == expected, message


class MappingConflictTestBase(ConflictTestBase):
    # Tests common to mappings (buckets, btrees).

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
        b1 = type(base)(base)
        b2 = type(base)(base)
        bm = type(base)(base)

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

class SetConflictTestBase(ConflictTestBase):
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


## utility functions

def lsubtract(l1, l2):
    l1 = list(l1)
    l2 = list(l2)
    return (list(filter(lambda x, l1=l1: x not in l1, l2)) +
            list(filter(lambda x, l2=l2: x not in l2, l1)))

def realseq(itemsob):
    return [x for x in itemsob]

def permutations(x):
    # Return a list of all permutations of list x.
    n = len(x)
    if n <= 1:
        return [x]
    result = []
    x0 = x[0]
    for i in range(n):
        # Build the (n-1)! permutations with x[i] in the first position.
        xcopy = x[:]
        first, xcopy[i] = xcopy[i], x0
        result.extend([[first] + p for p in permutations(xcopy[1:])])
    return result
