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

def _skip_wo_ZODB(test_method): #pragma NO COVER
    try:
        import ZODB
    except ImportError: # skip this test if ZODB is not available
        def _dummy(*args):
            pass
        return _dummy
    else:
        return test_method


class Base(object):
    # Tests common to all types: sets, buckets, and BTrees 

    db = None

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
        except TypeError, v:
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
        self.assert_(t in read)
        del read[:]
        add(100)
        self.assert_(t in read)
        del read[:]

        transaction.abort()
        conn.cacheMinimize()
        list(t)
        self.assert_(100 in t)
        self.assert_(not read)


class MappingBase(Base):
    # Tests common to mappings (buckets, btrees) 

    def _populate(self, t, l):
        # Make some data
        for i in range(l): t[i]=i

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
            self.assert_(len(r) > 10000)

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
        self.assertEqual(a , 1, `a`)

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
        r = range(1000)
        for x in r:
            k = random.choice(r)
            t[k] = x
            added[k] = x
        addl = added.keys()
        self.assertEqual(len(t) , len(addl), len(t))

    def testHasKeyWorks(self):
        t = self._makeOne()
        t[1] = 1
        self.assert_(t.has_key(1))
        self.assert_(1 in t)
        self.assert_(0 not in t)
        self.assert_(2 not in t)

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
            lst = list(t.values(0+x,99-x))
            lst.sort()
            self.assertEqual(lst,range(0+x,99-x+1))

            lst = list(t.values(max=99-x, min=0+x))
            lst.sort()
            self.assertEqual(lst,range(0+x,99-x+1))

    def testValuesNegativeIndex(self):
        t = self._makeOne()
        L = [-3, 6, -11, 4]
        for i in L:
            t[i] = i
        L.sort()
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
            self.assertEqual(list(lst), range(0+x, 99-x+1))

            lst = t.keys(max=99-x, min=0+x)
            self.assertEqual(list(lst), range(0+x, 99-x+1))

        self.assertEqual(len(v), 100)

    def testKeysNegativeIndex(self):
        t = self._makeOne()
        L = [-3, 6, -11, 4]
        for i in L:
            t[i] = i
        L.sort()
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
        self.assertEqual(items, zip(range(12, 21), range(24, 43, 2)))

        items = list(t.iteritems(min=12, max=20))
        self.assertEqual(items, zip(range(12, 21), range(24, 43, 2)))

    def testItemsNegativeIndex(self):
        t = self._makeOne()
        L = [-3, 6, -11, 4]
        for i in L:
            t[i] = i
        L.sort()
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
        self.assertEqual(t.maxKey(6), 6)
        self.assertEqual(t.maxKey(9), 8)
        self.assertEqual(t.minKey(), 1)
        self.assertEqual(t.minKey(3), 3)
        self.assertEqual(t.minKey(9), 10)

        try:
            t.maxKey(t.minKey() - 1)
        except ValueError, err:
            self.assertEqual(str(err), "no key satisfies the conditions")
        else:
            self.fail("expected ValueError")

        try:
            t.minKey(t.maxKey() + 1)
        except ValueError, err:
            self.assertEqual(str(err), "no key satisfies the conditions")
        else:
            self.fail("expected ValueError")

    def testClear(self):
        import random
        t = self._makeOne()
        r = range(100)
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

        items=d.items()
        items.sort()

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
        t.update(zip(range(300), range(300)))
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
        self.assertEqual(list(tslice), zip(range(20, 80), [1]*60))

    def testIterators(self):
        t = self._makeOne()

        for keys in [], [-2], [1, 4], range(-170, 2000, 6):
            t.clear()
            for k in keys:
                t[k] = -3 * k

            self.assertEqual(list(t), keys)

            x = []
            for k in t:
                x.append(k)
            self.assertEqual(x, keys)

            it = iter(t)
            self.assert_(it is iter(it))
            x = []
            try:
                while 1:
                    x.append(it.next())
            except StopIteration:
                pass
            self.assertEqual(x, keys)

            self.assertEqual(list(t.iterkeys()), keys)
            self.assertEqual(list(t.itervalues()), list(t.values()))
            self.assertEqual(list(t.iteritems()), list(t.items()))

    def testRangedIterators(self):
        t = self._makeOne()

        for keys in [], [-2], [1, 4], range(-170, 2000, 13):
            t.clear()
            values = []
            for k in keys:
                value = -3 * k
                t[k] = value
                values.append(value)
            items = zip(keys, values)

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

                    gooditems = zip(goodkeys, goodvalues)
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

                            gooditems = zip(goodkeys, goodvalues)
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
        self.assert_(1 in t)
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
        r = range(100)
        for x in r:
            k = random.choice(r)
            if not added.has_key(k):
                t[k] = x
                added[k] = 1
        addl = added.keys()
        addl.sort()
        diff = lsubtract(list(t.keys()), addl)
        self.assertEqual(diff , [], (diff, addl, list(t.keys())))
        self._checkIt(t)

    def testRandomOverlappingInserts(self):
        import random
        t = self._makeOne()
        added = {}
        r = range(100)
        for x in r:
            k = random.choice(r)
            t[k] = x
            added[k] = 1
        addl = added.keys()
        addl.sort()
        diff = lsubtract(t.keys(), addl)
        self.assertEqual(diff , [], diff)
        self._checkIt(t)

    def testRandomDeletes(self):
        import random
        t = self._makeOne()
        r = range(1000)
        added = []
        for x in r:
            k = random.choice(r)
            t[k] = x
            added.append(k)
        deleted = []
        for x in r:
            k = random.choice(r)
            if t.has_key(k):
                self.assert_(k in t)
                del t[k]
                deleted.append(k)
                if t.has_key(k):
                    self.fail( "had problems deleting %s" % k )
        badones = []
        for x in deleted:
            if t.has_key(x):
                badones.append(x)
        self.assertEqual(badones , [], (badones, added, deleted))
        self._checkIt(t)

    def testTargetedDeletes(self):
        import random
        t = self._makeOne()
        r = range(1000)
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
        r = range(1000)
        for x in r:
            t[x] = 1
        self.assertEqual(realseq(t.keys()) , r, realseq(t.keys()))
        for x in r:
            del t[x]
        self.assertEqual(realseq(t.keys()) , [], realseq(t.keys()))
        self._checkIt(t)

    def testPathologicalLeftBranching(self):
        t = self._makeOne()
        r = range(1000)
        revr = r[:]
        revr.reverse()
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
            try: del t[x]
            except KeyError:
                if t.has_key(x):
                    self.assertEqual(1,2,"failed to delete %s" % x)
        self._checkIt(t)

    def testRangeSearchAfterSequentialInsert(self):
        t = self._makeOne()
        r = range(100)
        for x in r:
            t[x] = 0
        diff = lsubtract(list(t.keys(0, 100)), r)
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
        self.assert_(len(items) > 2)   # at least two buckets and a key
        # All values in the first bucket are < firstkey.  All in the
        # second bucket are >= firstkey, and firstkey is the first key in
        # the second bucket.
        firstkey = items[1]
        therange = t.keys(-1, firstkey)
        self.assertEqual(len(therange), firstkey + 1)
        self.assertEqual(list(therange), range(firstkey + 1))
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
        self.assertEqual(list(therange), range(firstkey))
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
            except RuntimeError, detail:
                self.assertEqual(str(detail), "the bucket being iterated "
                                              "changed size")
                break
            except KeyError, v:
                # The Python implementation behaves very differently and
                # gives a key error in this situation. It can't mess up
                # memory and can't readily detect changes to underlying buckets
                # in any sane way.
                self.assertEqual(str(v), str(k[0]))
        self._checkIt(t)


class NormalSetTests(Base):
    # Test common to all set types 

    def _populate(self, t, l):
        # Make some data
        t.update(range(l))

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
        t = self._makeOne()
        t.insert(1)
        self.assert_(t.has_key(1))
        self.assert_(1 in t)
        self.assert_(2 not in t)

    def testBigInsert(self):
        t = self._makeOne()
        r = xrange(10000)
        for x in r:
            t.insert(x)
        for x in r:
            self.assert_(t.has_key(x))
            self.assert_(x in t)

    def testRemoveSucceeds(self):
        t = self._makeOne()
        r = xrange(10000)
        for x in r: t.insert(x)
        for x in r: t.remove(x)

    def testRemoveFails(self):
        self.assertRaises(KeyError, self._removenonexistent)

    def _removenonexistent(self):
        self._makeOne().remove(1)

    def testHasKeyFails(self):
        t = self._makeOne()
        self.assert_(not t.has_key(1))
        self.assert_(1 not in t)

    def testKeys(self):
        t = self._makeOne()
        r = xrange(1000)
        for x in r:
            t.insert(x)
        diff = lsubtract(t.keys(), r)
        self.assertEqual(diff, [])


    def testClear(self):
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
        self.assertEqual(t.maxKey(6) , 6)
        self.assertEqual(t.maxKey(9) , 8)
        self.assertEqual(t.minKey() , 1)
        self.assertEqual(t.minKey(3) , 3)
        self.assertEqual(t.minKey(9) , 10)
        self.assert_(t.minKey() in t)
        self.assert_(t.minKey()-1 not in t)
        self.assert_(t.maxKey() in t)
        self.assert_(t.maxKey()+1 not in t)

        try:
            t.maxKey(t.minKey() - 1)
        except ValueError, err:
            self.assertEqual(str(err), "no key satisfies the conditions")
        else:
            self.fail("expected ValueError")

        try:
            t.minKey(t.maxKey() + 1)
        except ValueError, err:
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

        items = d.keys()
        items.sort()

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
            self.assertEqual(len(kslice), n)

            # Test whole-structure slices.
            x = kslice[:]
            self.assertEqual(list(x), keys[:])

            for lo in range(-2*n, 2*n+1):
                # Test one-sided slices.
                x = kslice[:lo]
                self.assertEqual(list(x), keys[:lo])
                x = kslice[lo:]
                self.assertEqual(list(x), keys[lo:])

                for hi in range(-2*n, 2*n+1):
                    # Test two-sided slices.
                    x = kslice[lo:hi]
                    self.assertEqual(list(x), keys[lo:hi])

    def testIterator(self):
        t = self._makeOne()

        for keys in [], [-2], [1, 4], range(-170, 2000, 6):
            t.clear()
            t.update(keys)

            self.assertEqual(list(t), keys)

            x = []
            for k in t:
                x.append(k)
            self.assertEqual(x, keys)

            it = iter(t)
            self.assert_(it is iter(it))
            x = []
            try:
                while 1:
                    x.append(it.next())
            except StopIteration:
                pass
            self.assertEqual(x, keys)

class ExtendedSetTests(NormalSetTests):

    def testLen(self):
        t = self._makeOne()
        r = xrange(10000)
        for x in r: t.insert(x)
        self.assertEqual(len(t) , 10000, len(t))

    def testGetItem(self):
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
        self.assert_(data[1] != key)

        # The tree should have changed:
        self.assert_(tree._p_changed)

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
        self.assert_(data[1] != key)

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
        for name in ('Bucket', 'BTree', 'Set', 'TreeSet'):
            klass = getattr(self._getModule(), name)
            self.assertEqual(klass.__module__, self._getModule().__name__)
            self.assert_(klass is getattr(self._getModule(),
                                          self.prefix + name))

    def testModuleProvides(self):
        from zope.interface.verify import verifyObject
        verifyObject(self._getInterface(), self._getModule())

    def testFamily(self):
        import BTrees
        if self.prefix == 'OO':
            self.assert_(
                getattr(self._getModule(), 'family', self) is self)
        elif 'L' in self.prefix:
            self.assert_(self._getModule().family is BTrees.family64)
        elif 'I' in self.prefix:
            self.assert_(self._getModule().family is BTrees.family32)


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

    def testLongIntKeysWork(self):
        from BTrees.IIBTree import using64bits
        if not using64bits:
            return
        t = self._makeOne()
        o1, o2 = self.getTwoValues()
        assert o1 != o2

        # Test some small key values first:
        t[0L] = o1
        self.assertEqual(t[0], o1)
        t[0] = o2
        self.assertEqual(t[0L], o2)
        self.assertEqual(list(t.keys()), [0])

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
        keys = list(self.getTwoKeys())
        keys.sort()
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


## utility functions

def lsubtract(l1, l2):
    l1 = list(l1)
    l2 = list(l2)
    l = filter(lambda x, l1=l1: x not in l1, l2)
    l = l + filter(lambda x, l2=l2: x not in l2, l1)
    return l

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
