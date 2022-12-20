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

import sys
import functools
import unittest
import platform
from unittest import skip

from BTrees._compat import _c_optimizations_ignored
from BTrees._compat import PYPY
from BTrees._base   import _tp_name

def _no_op(test_method):
    return test_method

try:
    __import__('ZODB')
except ImportError:
    _skip_wo_ZODB = skip('ZODB not available')
else:
    _skip_wo_ZODB = _no_op

if platform.architecture()[0] == '32bit':
    _skip_on_32_bits = skip("32-bit platform")
else:
    _skip_on_32_bits = _no_op

if _c_optimizations_ignored():
    skipOnPurePython = skip("Not on Pure Python")
else:
    skipOnPurePython = _no_op

def _skip_if_pure_py_and_py_test(self):
    if _c_optimizations_ignored() and 'Py' in type(self).__name__:
        # No need to run this again. The "C" tests will catch it.
        # This relies on the fact that we always define tests in pairs,
        # one normal/C and one with Py in the name for the Py test.
        raise unittest.SkipTest("Redundant with the C test")

# pylint:disable=too-many-lines
# pylint:disable=no-member,protected-access,unused-variable,import-error
# pylint:disable=line-too-long,unidiomatic-typecheck,abstract-method
# pylint:disable=redefined-builtin

#: The exceptions that can be raised by failed
#: unsigned conversions. The OverflowError is raised
#: by the interpreter and is nicer than the manual error.
UnsignedError = (TypeError, OverflowError)

def uses_negative_keys_and_values(func):
    """
    Apply this decorator to tests that use negative keys and values.

    If the underlying mapping doesn't support that, it will
    be expected to raise a TypeError or OverflowError.
    """
    @functools.wraps(func)
    def test(self):
        if not (self.SUPPORTS_NEGATIVE_KEYS and self.SUPPORTS_NEGATIVE_VALUES):
            with self.assertRaises(UnsignedError):
                func(self)
        else:
            func(self)
    return test

class SignedMixin:
    SUPPORTS_NEGATIVE_KEYS = True
    SUPPORTS_NEGATIVE_VALUES = True
    #: The values to pass to ``random.randrange()`` to generate
    #: valid keys.
    KEY_RANDRANGE_ARGS = (-2000, 2001)


class ZODBAccess:

    db = None

    def tearDown(self):
        if self.db is not None:
            self.db.close()
            del self.db

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


class Base(ZODBAccess, SignedMixin):
    # Tests common to all types: sets, buckets, and BTrees

    def _getTargetClass(self):
        raise NotImplementedError("subclass should return the target type")

    def _getTargetInterface(self):
        raise NotImplementedError("subclass must return the expected interface ")

    def _makeOne(self):
        return self._getTargetClass()()

    def setUp(self):
        super().setUp()
        _skip_if_pure_py_and_py_test(self)

    def coerce_to_key(self, item):
        return item

    def coerce_to_value(self, value):
        return value

    # These are constant tuples. Indexing them produces a key/value
    # corresponding to the index.
    KEYS = tuple(range(2001))
    VALUES = tuple(range(2001))

    def testSubclassesCanHaveAttributes(self):
        # https://github.com/zopefoundation/BTrees/issues/168
        class Subclass(self._getTargetClass()):
            pass
        Subclass.foo = 1
        self.assertIn('foo', Subclass.__dict__)
        self.assertNotIn('foo', self._getTargetClass().__dict__)

    @skipOnPurePython
    def testCannotSetArbitraryAttributeOnBase(self):
        if 'Py' in self._getTargetClass().__name__:
            # pure-python classes can have arbitrary attributes
            self.skipTest("Not on Pure Python.")
        with self.assertRaises(TypeError):
            self._getTargetClass().foo = 1

    def testProvidesInterface(self):
        from zope.interface import providedBy
        from zope.interface.common.sequence import IMinimalSequence
        from zope.interface.verify import verifyObject
        t = self._makeOne()
        self._populate(t, 10)
        # reprs are usually the same in the Python and C implementations,
        # so you need the actual class to be sure of what you're dealing with
        __traceback_info__ = type(t)
        verifyObject(self._getTargetInterface(), t)

        for meth in ('keys', 'values'):
            if providedBy(t).get(meth):
                # The interface says it should be here,
                # make sure it is. This will be things
                # like Tree, Bucket, Set.
                seq = getattr(t, meth)()
                if type(seq) not in (tuple, list):
                    verifyObject(IMinimalSequence, seq)

    def _getColectionsABC(self):
        raise NotImplementedError("subclass should return the collection ABC")

    def testIsinstanceCollectionsABC(self):
        abc = self._getCollectionsABC()
        t = self._makeOne()

        self.assertIsInstance(t, abc)
        # Now make sure that it actually has the required methods.
        # First, get the required methods:
        abc_attrs = set(dir(abc))
        # If the method was None, that means it's not required;
        # if it's not callable, it's not a method (None is not callable)
        # If it's a private attribute (starting with only one _), it's
        # an implementation detail to ignore.
        abc_attrs -= {x for x in abc_attrs
                         if (x[0] == '_' and x[1] != '_')
                         or not callable(getattr(abc, x, None))}
        # Drop things from Python typing and zope.interface that may or may not
        # be present.
        abc_attrs -= {
            '__provides__',
            '__implemented__',
            '__providedBy__',
            '__class_getitem__', # Python 3.9+
            # Also the equality and comparison operators;
            # we don't implement those methods, but the ABC does.
            '__lt__', '__le__', '__eq__', '__gt__', '__ge__', '__ne__',
        }
        btr_attrs = set(dir(type(t)))

        missing_attrs = abc_attrs - btr_attrs
        self.assertFalse(sorted(missing_attrs),
                         "Class {!r} is missing these methods: {}".format(type(t), missing_attrs))

    def testPersistentSubclass(self):
        # Can we subclass this and Persistent?
        # https://github.com/zopefoundation/BTrees/issues/78
        import persistent

        class PersistentSubclass(persistent.Persistent):
            pass

        __traceback_info__ = self._getTargetClass(), persistent.Persistent
        type('Subclass', (self._getTargetClass(), PersistentSubclass), {})

    def testPurePython(self):
        import importlib
        kind = self._getTargetClass()
        class_name = kind.__name__
        module_name = kind.__module__
        module = importlib.import_module(module_name)

        # If we're in pure python mode, our target class module
        # should not have an '_' in it (fix_pickle changes the name
        # to remove the 'Py')

        # If we're in the C extension mode, our target class
        # module still doesn't have the _ in it, but we should be able to find
        # a Py class that's different

        self.assertNotIn('_', module_name)
        self.assertIs(getattr(module, class_name), kind)

        if not _c_optimizations_ignored() and 'Py' not in type(self).__name__:
            self.assertIsNot(getattr(module, class_name + 'Py'), kind)

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
                self.assertEqual(list(root2[i].items()), list(t.items()))
            else:
                self.assertEqual(list(root2[i].keys()), list(t.keys()))

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
                self.assertEqual(list(root2[i].items()), list(t.items()))
            else:
                self.assertEqual(list(root2[i].keys()), list(t.keys()))

            self._closeRoot(root)
            self._closeRoot(root2)

    def testSimpleExclusiveKeyRange(self):
        t = self._makeOne()
        K = self.KEYS
        self.assertEqual(list(t.keys()), [])
        self.assertEqual(list(t.keys(excludemin=True)), [])
        self.assertEqual(list(t.keys(excludemax=True)), [])
        self.assertEqual(list(t.keys(excludemin=True, excludemax=True)), [])

        self._populate(t, 1)
        self.assertEqual(list(t.keys()), [K[0]])
        self.assertEqual(list(t.keys(excludemin=True)), [])
        self.assertEqual(list(t.keys(excludemax=True)), [])
        self.assertEqual(list(t.keys(excludemin=True, excludemax=True)), [])

        t.clear()
        self._populate(t, 2)
        self.assertEqual(list(t.keys()), [K[0], K[1]])
        self.assertEqual(list(t.keys(excludemin=True)), [K[1]])
        self.assertEqual(list(t.keys(excludemax=True)), [K[0]])
        self.assertEqual(list(t.keys(excludemin=True, excludemax=True)), [])

        t.clear()
        self._populate(t, 3)
        self.assertEqual(list(t.keys()), [K[0], K[1], K[2]])
        self.assertEqual(list(t.keys(excludemin=True)), [K[1], K[2]])
        self.assertEqual(list(t.keys(excludemax=True)), [K[0], K[1]])
        self.assertEqual(list(t.keys(excludemin=True, excludemax=True)), [K[1]])

        for low, high, expected in ((-1, 3, [0, 1, 2]), (-1, 2, [0, 1])):
            if self.SUPPORTS_NEGATIVE_KEYS:
                self.assertEqual(list(t.keys(low, high, excludemin=True, excludemax=True)),
                                 expected)
            else:
                with self.assertRaises(UnsignedError):
                    t.keys(low, high, excludemin=True, excludemax=True)

        self.assertEqual(list(t.keys(K[0], K[3], excludemin=True, excludemax=True)),
                         [K[1], K[2]])
        self.assertEqual(list(t.keys(K[0], K[2], excludemin=True, excludemax=True)),
                         [K[1]])

    @_skip_wo_ZODB
    def test_UpdatesDoReadChecksOnInternalNodes(self):
        import transaction
        from ZODB import DB
        from ZODB.MappingStorage import MappingStorage
        t = self._makeOne()
        K = self.KEYS
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
            _add = t.add
            _remove = t.remove
        except AttributeError:
            def add(i):
                t[self.coerce_to_key(i)] = self.coerce_to_value(i)
            def remove(i):
                del t[self.coerce_to_key(i)]
        else:
            def add(i):
                _add(self.coerce_to_key(i))
            def remove(i):
                _remove(self.coerce_to_key(i))

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
        self.assertTrue(K[100] in t)
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


        class NonSub:
            pass

        self.assertFalse(issubclass(NonSub, type(t)))
        self.assertFalse(isinstance(NonSub(), type(t)))

class MappingBase(Base): # pylint:disable=too-many-public-methods
    # Tests common to mappings (buckets, btrees)
    SUPPORTS_NEGATIVE_VALUES = True

    def _populate(self, t, l):
        # Make some data
        to_key = self.coerce_to_key
        to_value = self.coerce_to_value
        for i in range(l):
            t[to_key(i)] = to_value(i)

    def _getCollectionsABC(self):
        import collections.abc
        return collections.abc.MutableMapping

    def test_popitem(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        # Empty
        with self.assertRaises(KeyError):
            t.popitem()

        self._populate(t, 2000)
        self.assertEqual(len(t), 2000)
        for i in range(2000):
            self.assertEqual(t.popitem(), (K[i], V[i]))
            self.assertEqual(len(t), 2000 - i - 1)

        # Back to empty
        self.assertEqual(len(t), 0)
        with self.assertRaises(KeyError):
            t.popitem()

    def testShortRepr(self):
        # test the repr because buckets have a complex repr implementation
        # internally the cutoff from a stack allocated buffer to a heap
        # allocated buffer is 10000.
        t = self._makeOne()
        to_key = self.coerce_to_key
        to_value = self.coerce_to_value
        for i in range(5):
            t[to_key(i)] = to_value(i)
        t._p_oid = b'12345678'
        r = repr(t)
        # Make sure the repr is **not* 10000 bytes long for a shrort bucket.
        # (the buffer must be terminated when copied).
        self.assertTrue(len(r) < 10000)
        # Make sure the repr is human readable if it's a bucket
        if 'Bucket' in r:
            self.assertTrue(r.startswith("BTrees"))
            self.assertTrue(r.endswith(repr(t.items()) + ')'), r)
        else:
            # persistent-4.4 changed the default reprs, adding
            # oid and jar reprs
            self.assertIn("<BTrees.", r)
            self.assertIn('BTree object at', r)
            self.assertIn('oid 0x3132333435363738', r)

        # Make sure it's the same between Python and C
        self.assertNotIn('Py', r)

    def testRepr(self):
        # test the repr because buckets have a complex repr implementation
        # internally the cutoff from a stack allocated buffer to a heap
        # allocated buffer is 10000.
        t = self._makeOne()
        to_key = self.coerce_to_key
        to_value = self.coerce_to_value
        for i in range(1000):
            t[to_key(i)] = to_value(i)
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
        self.assertEqual(self._makeOne().get(1), None)
        self.assertEqual(self._makeOne().get(1, 'foo'), 'foo')

    def testGetReturnsDefaultWrongTypes(self):
        self.assertIsNone(self._makeOne().get('abc'))
        self.assertEqual(self._makeOne().get('abc', 'def'), 'def')

    def testGetReturnsDefaultOverflowRanges(self):
        too_big = 2 ** 64 + 1
        self.assertIsNone(self._makeOne().get(too_big))
        self.assertEqual(self._makeOne().get(too_big, 'def'), 'def')

        too_small = -too_big
        self.assertIsNone(self._makeOne().get(too_small))
        self.assertEqual(self._makeOne().get(too_small, 'def'), 'def')

    def testSetItemGetItemWorks(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        t[K[1]] = V[1]
        a = t[K[1]]
        self.assertEqual(a, V[1], repr(a))

    def testReplaceWorks(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        t[K[1]] = V[1]
        self.assertEqual(t[K[1]], V[1], t[K[1]])
        t[K[1]] = V[2]
        self.assertEqual(t[K[1]], V[2], t[K[1]])

    def testLen(self):
        import random
        t = self._makeOne()
        added = {}
        r = list(range(1000))
        for x in r:
            k = random.choice(r)
            k = self.coerce_to_key(k)
            t[k] = self.coerce_to_value(x)
            added[k] = self.coerce_to_value(x)
        addl = added.keys()
        self.assertEqual(len(t), len(addl), len(t))

    def testHasKeyWorks(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        t[K[1]] = V[1]
        self.assertTrue(t.has_key(K[1]))

        self.assertIn(K[1], t)
        self.assertNotIn(K[0], t)
        self.assertNotIn(K[2], t)

    def testHasKeyOverflowAndTypes(self):
        t = self._makeOne()

        too_big = 2 ** 64 + 1
        too_small = -too_big
        self.assertNotIn(too_big, t)
        self.assertNotIn(too_small, t)
        self.assertFalse(t.has_key(too_big))
        self.assertFalse(t.has_key(too_small))
        self.assertFalse(t.has_key('abc'))

    def testValuesWorks(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        for x in range(100):
            t[K[x]] = self.coerce_to_value(x * x)
        values = t.values()
        for i in range(100):
            v = self.coerce_to_value(i * i)
            self.assertEqual(values[i], v)
        self.assertRaises(IndexError, lambda: values[i + 1])
        i = 0
        for value in t.itervalues():
            self.assertEqual(value, self.coerce_to_value(i * i))
            i += 1

    def testValuesWorks1(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        for x in range(100):
            k = self.coerce_to_key(99 - x)
            t[k] = V[x]

        for x in range(40):
            lst = sorted(t.values(K[0 + x], K[99 - x]))
            self.assertEqual(lst, [V[i] for i in range(0 + x, 99 - x + 1)])

            lst = sorted(t.values(max=K[99 - x], min=K[0 + x]))
            self.assertEqual(lst, [V[i] for i in range(0 + x, 99 - x + 1)])

    @uses_negative_keys_and_values
    def testValuesNegativeIndex(self):
        t = self._makeOne()
        L = [-3, 6, -11, 4]
        for i in L:
            t[i] = self.coerce_to_value(i)
        L = sorted(L)
        vals = t.values()
        for i in range(-1, -5, -1):
            self.assertEqual(vals[i], L[i])
        self.assertRaises(IndexError, lambda: vals[-5])

    def testKeysWorks(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        for x in range(100):
            t[K[x]] = V[x]
        v = t.keys()
        i = 0
        for x in v:
            self.assertEqual(x, K[i])
            i = i + 1
        self.assertRaises(IndexError, lambda: v[i])

        for x in range(40):
            lst = t.keys(K[0 + x], K[99 - x])
            self.assertEqual(list(lst), [K[x] for x in range(0 + x, 99 - x + 1)])


            lst = t.keys(max=K[99-x], min=K[0+x])
            self.assertEqual(list(lst), [K[x] for x in range(0+x, 99-x+1)])

        self.assertEqual(len(v), 100)

    @uses_negative_keys_and_values
    def testKeysNegativeIndex(self):
        t = self._makeOne()
        L = [-3, 6, -11, 4]
        for i in L:
            t[i] = self.coerce_to_value(i)
        L = sorted(L)
        keys = t.keys()
        for i in range(-1, -5, -1):
            self.assertEqual(keys[i], L[i])
        self.assertRaises(IndexError, lambda: keys[-5])

    def testItemsWorks(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        for x in range(100):
            t[K[x]] = V[2*x]
        v = t.items()
        i = 0
        for x in v:
            self.assertEqual(x[0], K[i])
            self.assertEqual(x[1], V[2*i])
            i += 1
        self.assertRaises(IndexError, lambda: v[i+1])

        i = 0
        for x in t.iteritems():
            self.assertEqual(x, (K[i], V[2*i]))
            i += 1

        items = list(t.items(min=K[12], max=K[20]))
        self.assertEqual(items, list(zip(
            (K[i] for i in range(12, 21)),
            (V[i] for i in range(24, 43, 2))
        )))

        items = list(t.iteritems(min=K[12], max=K[20]))
        self.assertEqual(items, list(zip(
            (K[i] for i in range(12, 21)),
            (V[i] for i in range(24, 43, 2))
        )))

    def testItemsNegativeIndex(self):
        if not (self.SUPPORTS_NEGATIVE_KEYS and self.SUPPORTS_NEGATIVE_VALUES):
            self.skipTest("Needs negative keys and values")
        t = self._makeOne()
        L = [-3, 6, -11, 4]
        for i in L:
            t[i] = self.coerce_to_value(i)
        L = sorted(L)
        items = t.items()
        for i in range(-1, -5, -1):
            self.assertEqual(items[i], (L[i], L[i]))
        self.assertRaises(IndexError, lambda: items[-5])

    def testDeleteInvalidKeyRaisesKeyError(self):
        self.assertRaises(KeyError, self._deletefail)

    def _deletefail(self):
        t = self._makeOne()
        del t[self.KEYS[1]]

    def testMaxKeyMinKey(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        t[K[7]] = V[6]
        t[K[3]] = V[10]
        t[K[8]] = V[12]
        t[K[1]] = V[100]
        t[K[5]] = V[200]
        t[K[10]] = V[500]
        t[K[6]] = V[99]
        t[K[4]] = V[150]
        del t[K[7]]
        K = self.KEYS
        self.assertEqual(t.maxKey(), K[10])
        self.assertEqual(t.maxKey(None), K[10])
        self.assertEqual(t.maxKey(K[6]), K[6])
        self.assertEqual(t.maxKey(K[9]), K[8])
        self.assertEqual(t.minKey(), K[1])
        self.assertEqual(t.minKey(None), K[1])
        self.assertEqual(t.minKey(K[3]), K[3])
        self.assertEqual(t.minKey(K[9]), K[10])

        try:
            too_small = t.minKey() - 1
        except TypeError:
            # we can't do arithmetic with the key type;
            # must be fsBTree.
            return

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
            t[self.coerce_to_key(rnd)] = self.VALUES[0]
        t.clear()
        diff = lsubtract(list(t.keys()), [])
        self.assertEqual(diff, [])

    def testUpdate(self):
        import random
        t = self._makeOne()
        d = {}
        l = []
        for i in range(10000):
            k = random.randrange(*self.KEY_RANDRANGE_ARGS)
            k = self.coerce_to_key(k)
            v = self.coerce_to_value(i)
            d[k] = v
            l.append((k, v))

        items = sorted(d.items())

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
        K = self.KEYS
        V = self.VALUES
        pm = PersistentMapping({K[1]: V[2]})
        t.update(pm)
        self.assertEqual(list(t.items()), [(K[1], V[2])])

        # Construction goes thru the same internals as .update().
        t = t.__class__(pm)
        self.assertEqual(list(t.items()), [(K[1], V[2])])

    def testEmptyRangeSearches(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        t.update([(K[1], V[1]), (K[5], V[5]), (K[9], V[9])])
        if self.SUPPORTS_NEGATIVE_KEYS and self.SUPPORTS_NEGATIVE_VALUES:
            self.assertEqual(list(t.keys(self.coerce_to_key(-6), self.coerce_to_key(-4))), [])

        self.assertEqual(list(t.keys(K[2], K[4])), [])
        self.assertEqual(list(t.keys(K[6], K[8])), [])
        self.assertEqual(list(t.keys(K[10], K[12])), [])
        self.assertEqual(list(t.keys(K[9], K[1])), [])

        # For IITreeSets, this one was returning 31 for len(keys), and
        # list(keys) produced a list with 100 elements.
        t.clear()
        t.update(list(zip(
            (self.coerce_to_key(x) for x in range(300)),
            (self.coerce_to_value(x) for x in range(300)))))
        two_hundred = K[200]
        fifty = K[50]
        keys = t.keys(two_hundred, fifty)
        self.assertEqual(len(keys), 0)
        self.assertEqual(list(keys), [])
        self.assertEqual(list(t.iterkeys(two_hundred, fifty)), [])

        keys = t.keys(max=fifty, min=two_hundred)
        self.assertEqual(len(keys), 0)
        self.assertEqual(list(keys), [])
        self.assertEqual(list(t.iterkeys(max=fifty, min=two_hundred)), [])

    def testSlicing(self): # pylint:disable=too-many-locals
        # Test that slicing of .keys()/.values()/.items() works exactly the
        # same way as slicing a Python list with the same contents.
        # This tests fixes to several bugs in this area, starting with
        # http://collector.zope.org/Zope/419,
        # "BTreeItems slice contains 1 too many elements".
        t = self._makeOne()
        val_multiplier = -2 if self.SUPPORTS_NEGATIVE_VALUES else 2
        K = self.KEYS
        V = self.VALUES
        for n in range(10):
            t.clear()
            self.assertEqual(len(t), 0)

            keys = []
            values = []
            items = []

            for key in range(n):
                value = key * val_multiplier
                key = K[key]
                value = self.coerce_to_value(value)
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
        for i in range(100):
            t[K[i]] = self.VALUES[1]
        tslice = t.items()[20:80]
        self.assertEqual(len(tslice), 60)
        self.assertEqual(list(tslice), list(zip(
            [K[x] for x in range(20, 80)],
            [V[1]] * 60
        )))

    @uses_negative_keys_and_values
    def testIterators(self):
        t = self._makeOne()

        for keys in [], [-2], [1, 4], list(range(-170, 2000, 6)):
            t.clear()
            for k in keys:
                val = -3 * k
                t[k] = self.coerce_to_value(val)

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

    @uses_negative_keys_and_values
    def testRangedIterators(self): # pylint:disable=too-many-locals
        t = self._makeOne()

        for keys in [], [-2], [1, 4], list(range(-170, 2000, 13)):
            t.clear()
            values = []
            for k in keys:
                value = -3 * k
                t[k] = self.coerce_to_value(value)
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
        t = self._makeOne()
        # This one silently ignored the excess in Zope3.
        key = self.KEYS[1]
        value = self.VALUES[2]
        self.assertRaises(TypeError, t.update, [(key, value, value)])

        # This one dumped core in Zope3.
        self.assertRaises(TypeError, t.update, [(key,)])

        # This one should simply succeed.
        t.update([(key, value)])
        self.assertEqual(list(t.items()), [(key, value)])

    def testSimpleExclusivRanges(self):
        K = self.KEYS
        V = self.VALUES

        def list_keys(x):
            return [K[k] for k in x]
        def list_values(x):
            return [V[k] for k in x]
        def as_items(x):
            return [(K[k], V[k]) for k in x]

        for methodname, f in (("keys", list_keys),
                              ("values", list_values),
                              ("items", as_items),
                              ("iterkeys", list_keys),
                              ("itervalues", list_values),
                              ("iteritems", as_items)):

            t = self._makeOne()
            meth = getattr(t, methodname, None)
            if meth is None:
                continue

            __traceback_info__ = meth

            supports_negative = self.SUPPORTS_NEGATIVE_KEYS

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
            if supports_negative:
                self.assertEqual(list(meth(self.coerce_to_key(-1), K[2], excludemin=True,
                                           excludemax=True)),
                                 f([0, 1]))

                self.assertEqual(list(meth(self.coerce_to_key(-1), K[3], excludemin=True,
                                           excludemax=True)),
                                 f([0, 1, 2]))

            self.assertEqual(list(meth(K[0], K[3], excludemin=True,
                                       excludemax=True)),
                             f([1, 2]))
            self.assertEqual(list(meth(K[0], K[2], excludemin=True,
                                       excludemax=True)),
                             f([1]))

    def testSetdefault(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        self.assertEqual(t.setdefault(K[1], V[2]), V[2])
        # That should also have associated 1 with 2 in the tree.
        self.assertTrue(K[1] in t)
        self.assertEqual(t[K[1]], V[2])
        # And trying to change it again should have no effect.
        self.assertEqual(t.setdefault(K[1], self.coerce_to_value(666)), V[2])
        self.assertEqual(t[K[1]], V[2])

        # Not enough arguments.
        self.assertRaises(TypeError, t.setdefault)
        self.assertRaises(TypeError, t.setdefault, K[1])
        # Too many arguments.
        self.assertRaises(TypeError, t.setdefault, K[1], V[2], V[3])


    def testPop(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        # Empty container.
        # If no default given, raises KeyError.
        self.assertRaises(KeyError, t.pop, K[1])
        # But if default given, returns that instead.
        self.assertEqual(t.pop(K[1], 42), 42)

        t[K[1]] = V[3]
        # KeyError when key is not in container and default is not passed.
        self.assertRaises(KeyError, t.pop, K[5])
        self.assertEqual(list(t.items()), [(K[1], V[3])])
        # If key is in container, returns the value and deletes the key.
        self.assertEqual(t.pop(K[1]), V[3])
        self.assertEqual(len(t), 0)

        # If key is present, return value bypassing default.
        t[K[1]] = V[3]
        self.assertEqual(t.pop(K[1], 7), V[3])
        self.assertEqual(len(t), 0)

        # Pop only one item.
        t[K[1]] = V[3]
        t[K[2]] = V[4]
        self.assertEqual(len(t), 2)
        self.assertEqual(t.pop(K[1]), V[3])
        self.assertEqual(len(t), 1)
        self.assertEqual(t[K[2]], V[4])
        self.assertEqual(t.pop(K[1], 3), 3)

        # Too few arguments.
        self.assertRaises(TypeError, t.pop)
        # Too many arguments.
        self.assertRaises(TypeError, t.pop, K[1], 2, 3)

    def __test_key_or_value_type(self, k, v, to_test, kvtype):
        try:
            kvtype(to_test)
        except Exception as e: # pylint:disable=broad-except
            with self.assertRaises(type(e)):
                self._makeOne()[k] = self.coerce_to_value(v)
        else:
            self._makeOne()[k] = self.coerce_to_value(v)

    def __test_key(self, k):
        v = self.getTwoValues()[0]
        self.__test_key_or_value_type(k, v, k, self.key_type)

    def __test_value(self, v):
        k = self.getTwoKeys()[0]
        self.__test_key_or_value_type(k, v, v, self.value_type)

    def test_assign_key_type_str(self):
        self.__test_key('c')

    # Assigning a str may or may not work; but querying for
    # one will always return a correct answer, not raise
    # a TypeError.
    def testStringAllowedInContains(self):
        self.assertFalse('key' in self._makeOne())

    def testStringKeyRaisesKeyErrorWhenMissing(self):
        self.assertRaises(KeyError, self._makeOne().__getitem__, 'key')

    def testStringKeyReturnsDefaultFromGetWhenMissing(self):
        self.assertEqual(self._makeOne().get('key', 42), 42)

    def test_assign_key_type_float(self):
        self.__test_key(2.5)

    def test_assign_key_type_None(self):
        self.__test_key(None)

    def test_assign_value_type_str(self):
        self.__test_value('c')

    def test_assign_value_type_float(self):
        self.__test_value(2.5)

    def test_assign_value_type_None(self):
        self.__test_value(None)

    def testNewStyleClassAsKeyNotAllowed(self):
        m = self._makeOne()
        class New:
            pass

        with self.assertRaises(TypeError):
            m[New] = self.getTwoValues()[0]

    def testClassAsKeyNotAllowed(self):
        m = self._makeOne()
        class Cls:
            pass

        with self.assertRaises(TypeError):
            m[Cls] = self.getTwoValues()[0]

    def testNewStyleClassWithCustomMetaClassNotAllowed(self):

        class Meta(type):
            pass

        cls = Meta('Class', (object,), {})
        m = self._makeOne()
        with self.assertRaises(TypeError):
            m[cls] = self.getTwoValues()[0]

    def testEmptyFirstBucketReportedByGuido(self):
        # This was for Integer keys
        b = self._makeOne()
        for i in range(29972): # reduce to 29971 and it works
            b[self.coerce_to_key(i)] = self.coerce_to_value(i)
        for i in range(30): # reduce to 29 and it works
            del b[self.coerce_to_key(i)]
            try:
                big_key = self.coerce_to_key(i + 40000)
            except TypeError:
                # fsBtree only has a two-byte key
                self.skipTest('Key to big')
            b[big_key] = self.coerce_to_value(i)

        self.assertEqual(b.keys()[0], self.KEYS[30])

    def testKeyAndValueOverflow(self):
        if self.key_type.get_upper_bound() is None or self.value_type.get_upper_bound() is None:
            self.skipTest("Needs bounded key and value")

        import struct

        good = set()
        b = self._makeOne()

        # Some platforms (Windows) use a 32-bit value for long,
        # meaning that PyInt_AsLong and such can throw OverflowError
        # for values that are in range on most other platforms. And on Python 2,
        # PyInt_Check can fail with a TypeError starting at small values
        # like 2147483648. So we look for small longs and catch those errors
        # even when we think we should be in range. In all cases, our code
        # catches the unexpected error (OverflowError) and turns it into TypeError.
        long_is_32_bit = struct.calcsize('@l') < 8
        in_range_errors = TypeError
        out_of_range_errors = TypeError

        K = self.KEYS
        V = self.VALUES
        def trial(i):
            i = int(i)
            __traceback_info__ = i, type(i)
            # As key
            if i > self.key_type.get_upper_bound():
                with self.assertRaises(out_of_range_errors):
                    b[i] = V[0]
            elif i < self.key_type.get_lower_bound():
                with self.assertRaises(out_of_range_errors):
                    b[i] = V[0]
            else:
                try:
                    b[i] = V[0]
                except in_range_errors:
                    pass
                else:
                    good.add(i)
                    self.assertEqual(b[i], 0)

            # As value
            if i > self.value_type.get_upper_bound():
                with self.assertRaises(out_of_range_errors):
                    b[V[0]] = self.coerce_to_value(i)
            elif i < self.value_type.get_lower_bound():
                with self.assertRaises(out_of_range_errors):
                    b[V[0]] = self.coerce_to_value(i)
            else:
                try:
                    b[V[0]] = self.coerce_to_value(i)
                except in_range_errors:
                    pass
                else:
                    self.assertEqual(b[V[0]], i)

        for i in range(self.key_type.get_upper_bound() - 3,
                       self.key_type.get_upper_bound() + 3):

            trial(i)
            trial(-i)

        if 0 in b:
            del b[0]
        self.assertEqual(sorted(good), sorted(b))
        if not long_is_32_bit:
            if self.key_type.get_lower_bound() == 0:
                # None of the negative values got in
                self.assertEqual(4, len(b))
            else:
                # 9, not 4 * 2, because of the asymmetry
                # of twos complement binary integers
                self.assertEqual(9, len(b))

    @_skip_wo_ZODB
    def testAccessRaisesPOSKeyErrorOnSelf(self):
        # We don't hide a POSKeyError that happens when
        # accessing the object itself in `get()`.
        # See https://github.com/zopefoundation/BTrees/issues/161
        from ZODB.POSException import POSKeyError
        import transaction
        transaction.begin()
        m = self._makeOne()
        root = self._getRoot()
        root.m = m
        transaction.commit()
        conn = root._p_jar
        # Ghost the object
        conn.cacheMinimize()
        self.assertEqual(m._p_status, "ghost")
        # Remove the backing data
        self.db._storage._data.clear()

        transaction.begin()
        K = self.KEYS

        try:
            with self.assertRaises(POSKeyError):
                m.get(K[1])

            with self.assertRaises(POSKeyError):
                m.setdefault(K[1], self.VALUES[1])

            with self.assertRaises(POSKeyError):
                _ = K[1] in m

            with self.assertRaises(POSKeyError):
                m.pop(K[1])
        finally:
            self._closeRoot(root)

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

    def _makeOne(self, *args): # pylint:disable=arguments-differ
        return self._getTargetClass()(*args)

    def _checkIt(self, t):
        from BTrees.check import check
        t._check()
        check(t)

    @_skip_wo_ZODB
    def testAccessRaisesPOSKeyErrorOnNested(self):
        # We don't hide a POSKeyError that happens when
        # accessing sub objects in `get()`.
        # See https://github.com/zopefoundation/BTrees/issues/161
        from ZODB.POSException import POSKeyError
        import transaction
        transaction.begin()
        m = self._makeOne()
        root = self._getRoot()
        root.m = m
        self._populate(m, 1000)
        transaction.commit()
        conn = root._p_jar
        # Ghost the objects...
        conn.cacheMinimize()
        # ...but activate the tree itself, leaving the
        # buckets ghosted
        m._p_activate()

        # Remove the backing data
        self.db._storage._data.clear()
        to_key = self.coerce_to_key
        to_value = self.coerce_to_value
        transaction.begin()
        try:
            with self.assertRaises(POSKeyError):
                m.get(to_key(1))

            with self.assertRaises(POSKeyError):
                m.setdefault(to_key(1), to_value(1))

            with self.assertRaises(POSKeyError):
                _ = to_key(1) in m

            with self.assertRaises(POSKeyError):
                m.pop(to_key(1))
        finally:
            self._closeRoot(root)

    def testDeleteNoChildrenWorks(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        t[K[5]] = V[6]
        t[K[2]] = V[10]
        t[K[6]] = V[12]
        t[K[1]] = V[100]
        t[K[3]] = V[200]
        t[K[10]] = self.coerce_to_value(500)
        t[K[4]] = V[99]
        del t[K[4]]
        keys = [
            self.coerce_to_key(x)
            for x in (1, 2, 3, 5, 6, 10)
        ]
        diff = lsubtract(t.keys(), keys)
        self.assertEqual(diff, [], diff)
        self._checkIt(t)

    def testDeleteOneChildWorks(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        t[K[5]] = V[6]
        t[K[2]] = V[10]
        t[K[6]] = V[12]
        t[K[1]] = V[100]
        t[K[3]] = V[200]
        t[K[10]] = self.coerce_to_value(500)
        t[K[4]] = V[99]
        del t[K[3]]
        keys = [
            self.coerce_to_key(x)
            for x in (1, 2, 4, 5, 6, 10)
        ]
        diff = lsubtract(t.keys(), keys)
        self.assertEqual(diff, [], diff)
        self._checkIt(t)

    def testDeleteTwoChildrenNoInorderSuccessorWorks(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        t[K[5]] = V[6]
        t[K[2]] = V[10]
        t[K[6]] = V[12]
        t[K[1]] = V[100]
        t[K[3]] = V[200]
        t[K[10]] = self.coerce_to_value(500)
        t[K[4]] = V[99]
        del t[K[2]]
        keys = [
            self.coerce_to_key(x)
            for x in (1, 3, 4, 5, 6, 10)
        ]
        diff = lsubtract(t.keys(), keys)
        self.assertEqual(diff, [], diff)
        self._checkIt(t)

    def testDeleteTwoChildrenInorderSuccessorWorks(self):
        # 7, 3, 8, 1, 5, 10, 6, 4 -- del 3
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        t[K[7]] = V[6]
        t[K[3]] = V[10]
        t[K[8]] = V[12]
        t[K[1]] = V[100]
        t[K[5]] = V[200]
        t[K[10]] = self.coerce_to_value(500)
        t[K[6]] = V[99]
        t[K[4]] = V[150]
        del t[K[3]]
        keys = [
            self.coerce_to_key(x)
            for x in (1, 4, 5, 6, 7, 8, 10)
        ]
        diff = lsubtract(t.keys(), keys)
        self.assertEqual(diff, [], diff)
        self._checkIt(t)

    def testDeleteRootWorks(self):
        # 7, 3, 8, 1, 5, 10, 6, 4 -- del 7
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        t[K[7]] = V[6]
        t[K[3]] = V[10]
        t[K[8]] = V[12]
        t[K[1]] = V[100]
        t[K[5]] = V[200]
        t[K[10]] = self.coerce_to_value(500)
        t[K[6]] = V[99]
        t[K[4]] = V[150]
        del t[K[7]]
        keys = [
            self.coerce_to_key(x)
            for x in (1, 3, 4, 5, 6, 8, 10)
        ]
        diff = lsubtract(t.keys(), keys)
        self.assertEqual(diff, [], diff)
        self._checkIt(t)

    def testRandomNonOverlappingInserts(self):
        import random
        t = self._makeOne()
        added = {}
        r = list(range(100))
        K = self.KEYS
        V = self.VALUES
        for x in r:
            k = random.choice(r)
            k = K[k]
            if k not in added:
                t[k] = V[x]
                added[k] = V[1]
        addl = sorted(added.keys())
        diff = lsubtract(list(t.keys()), addl)
        self.assertEqual(diff, [], (diff, addl, list(t.keys())))
        self._checkIt(t)

    def testRandomOverlappingInserts(self):
        import random
        t = self._makeOne()
        added = {}
        r = list(range(100))
        K = self.KEYS
        V = self.VALUES
        for x in r:
            k = random.choice(r)
            k = K[k]
            t[k] = V[x]
            added[k] = V[1]
        addl = sorted(added.keys())
        diff = lsubtract(t.keys(), addl)
        self.assertEqual(diff, [], diff)
        self._checkIt(t)

    def testRandomDeletes(self):
        import random
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        r = list(range(1000))

        added = []
        for x in r:
            k = random.choice(r)
            k = K[k]
            t[k] = V[x]
            added.append(k)
        deleted = []
        for x in r:
            k = random.choice(r)
            k = K[k]
            if k in t:
                self.assertTrue(k in t)
                del t[k]
                deleted.append(k)
                if k in t:
                    self.fail("had problems deleting %s" % k)
        badones = []
        for x in deleted:
            if x in t:
                badones.append(x)
        self.assertEqual(badones, [], (badones, added, deleted))
        self._checkIt(t)

    def testTargetedDeletes(self):
        import random
        t = self._makeOne()
        r = list(range(1000))
        K = self.KEYS
        V = self.VALUES
        for x in r:
            k = random.choice(r)
            k = K[k]
            v = V[x]
            t[k] = v
        for x in r:
            k = K[x]
            try:
                del t[k]
            except KeyError:
                pass
        self.assertEqual(realseq(t.keys()), [], realseq(t.keys()))
        self._checkIt(t)

    def testPathologicalRightBranching(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        r = [K[k] for k in range(1000)]
        for x in r:
            t[x] = V[1]
        self.assertEqual(realseq(t.keys()), r, realseq(t.keys()))
        for x in r:
            del t[x]
        self.assertEqual(realseq(t.keys()), [], realseq(t.keys()))
        self._checkIt(t)

    def testPathologicalLeftBranching(self):
        t = self._makeOne()
        r = [self.coerce_to_key(k) for k in range(1000)]
        revr = list(reversed(r[:]))
        for x in revr:
            t[x] = self.VALUES[1]
        self.assertEqual(realseq(t.keys()), r, realseq(t.keys()))

        for x in revr:
            del t[x]
        self.assertEqual(realseq(t.keys()), [], realseq(t.keys()))
        self._checkIt(t)

    def testSuccessorChildParentRewriteExerciseCase(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
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
            t[K[x]] = V[1]
        for x in delete_order:
            try:
                del t[K[x]]
            except KeyError:
                if K[x] in t:
                    self.assertEqual(1, 2, "failed to delete %s" % x)
        self._checkIt(t)

    def testRangeSearchAfterSequentialInsert(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        r = [K[k] for k in range(100)]
        for x in r:
            t[x] = V[0]
        diff = lsubtract(list(t.keys(K[0], K[100])), r)
        self.assertEqual(diff, [], diff)
        # The same thing with no bounds
        diff = lsubtract(list(t.keys(None, None)), r)
        self.assertEqual(diff, [], diff)
        # The same thing with each bound set and the other
        # explicitly None
        diff = lsubtract(list(t.keys(K[0], None)), r)
        self.assertEqual(diff, [], diff)
        diff = lsubtract(list(t.keys(None, K[100])), r)
        self.assertEqual(diff, [], diff)
        self._checkIt(t)

    def testRangeSearchAfterRandomInsert(self):
        import random
        t = self._makeOne()
        r = range(100)
        a = {}
        V = self.VALUES
        K = self.KEYS
        for x in r:
            rnd = random.choice(r)
            rnd = K[rnd]
            t[rnd] = V[0]
            a[rnd] = V[0]
        diff = lsubtract(list(t.keys(K[0], K[100])), a.keys())
        self.assertEqual(diff, [], diff)
        self._checkIt(t)

    def testPathologicalRangeSearch(self):
        # XXX: This test needs some work to be able to handle fsBTree
        # objects. It makes assumptions about bucket sizes and key ordering
        # that doesn't hold.
        if self._getTargetClass().__name__[:2] == 'fs':
            self.skipTest("XXX: Needs ported for fsBTree")
        t = self._makeOne()
        # Build a 2-level tree with at least two buckets.
        if self.SUPPORTS_NEGATIVE_KEYS:
            range_begin = 0
            firstkey_offset = 1
        else:
            range_begin = 1
            firstkey_offset = 0

        before_range_begin = range_begin - 1
        for i in range(range_begin, 200 + range_begin):
            t[self.coerce_to_key(i)] = self.coerce_to_value(i)
        items, dummy = t.__getstate__()
        self.assertTrue(len(items) > 2)   # at least two buckets and a key
        # All values in the first bucket are < firstkey.  All in the
        # second bucket are >= firstkey, and firstkey is the first key in
        # the second bucket.
        firstkey = items[1]
        therange = t.keys(self.coerce_to_key(before_range_begin), firstkey)
        self.assertEqual(len(therange), firstkey + firstkey_offset)
        self.assertEqual(list(therange), list(range(range_begin, firstkey + 1)))
        # Now for the tricky part.  If we delete firstkey, the second bucket
        # loses its smallest key, but firstkey remains in the BTree node.
        # If we then do a high-end range search on firstkey, the BTree node
        # directs us to look in the second bucket, but there's no longer any
        # key <= firstkey in that bucket.  The correct answer points to the
        # end of the *first* bucket.  The algorithm has to be smart enough
        # to "go backwards" in the BTree then; if it doesn't, it will
        # erroneously claim that the range is empty.
        del t[firstkey]
        therange = t.keys(min=before_range_begin, max=firstkey)
        self.assertEqual(len(therange), firstkey - range_begin)
        self.assertEqual(list(therange), list(range(range_begin, firstkey)))
        self._checkIt(t)

    def testInsertMethod(self):
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        t[K[0]] = V[1]
        self.assertEqual(t.insert(K[0], V[1]), 0)
        self.assertEqual(t.insert(K[1], V[1]), 1)
        self.assertEqual(lsubtract(list(t.keys()), [K[0], K[1]]), [])
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
                self.assertEqual(v.args[0], k[0])
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
        class Jar:
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
        K = self.KEYS
        V = self.VALUES
        t[K[1]] = V[3]
        # reset these, setting _firstbucket triggered a change
        t._p_changed = False
        t._p_jar.registered = None
        t[K[2]] = V[4]
        self.assertTrue(t._p_changed)
        self.assertEqual(t, t._p_jar.registered)

        # Setting the same key to a different value also triggers a change
        t._p_changed = False
        t._p_jar.registered = None
        t[K[2]] = V[5]
        self.assertTrue(t._p_changed)
        self.assertEqual(t, t._p_jar.registered)

        # Likewise with only a single value
        t = self._makeOne()
        t._p_oid = b'\0\0\0\0\0'
        t._p_jar = Jar()
        t[K[1]] = V[3]
        # reset these, setting _firstbucket triggered a change
        t._p_changed = False
        t._p_jar.registered = None

        t[K[1]] = V[6]
        self.assertTrue(t._p_changed)
        self.assertEqual(t, t._p_jar.registered)

    def testRemoveInSmallMapSetsChanged(self):
        # A bug in the BTree Python implementation once caused
        # deleting from a small btree to set _p_changed.
        # There must be at least two objects so that _firstbucket doesn't
        # get set
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        # Note that for the property to actually hold, we have to fake a
        # _p_jar and _p_oid
        t._p_oid = b'\0\0\0\0\0'
        class Jar:
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
        t[K[0]] = V[1]
        t[K[1]] = V[2]
        # reset these, setting _firstbucket triggered a change
        t._p_changed = False
        t._p_jar.registered = None

        # now remove the second value
        del t[K[1]]
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

    def testSetstateBadChild(self):
        # tree used to allow to pass in non (tree or bucket) node as a child
        # via __setstate__. This was leading to crashes when using C mode.
        t = self._makeOne()
        b = t._bucket_type()
        K = self.KEYS
        V = self.VALUES
        if isaset(b):
            b.add(K[1])
        else:
            b[K[1]] = V[11]

        # xchild is non-BTree class deriving from Persistent
        import persistent
        xchild = persistent.Persistent()
        self.assertIs(xchild._p_oid, None)

        typeErrOK = "tree child %s is neither %s nor %s" % \
                        (_tp_name(type(xchild)), _tp_name(type(t)),
                         _tp_name(t._bucket_type))

        # if the following is allowed, e.g.
        # t.__getstate__(), or t[0]=1 corrupt memory and crash.
        with self.assertRaises(TypeError) as exc:
            t.__setstate__(
                (
                    (xchild,), # child0 is neither tree nor bucket
                    b
                )
            )
        self.assertEqual(str(exc.exception), typeErrOK)

        # if the following is allowed, e.g. t[5]=1 corrupts memory and crash.
        with self.assertRaises(TypeError) as exc:
            t.__setstate__(
                (
                    (b, K[4], xchild),
                    b
                )
            )
        self.assertEqual(str(exc.exception), typeErrOK)


class NormalSetTests(Base):
    # Test common to all set types

    def _getCollectionsABC(self):
        import collections.abc
        return collections.abc.MutableSet

    def _populate(self, t, l):
        # Make some data
        t.update(self.coerce_to_key(k) for k in range(l))

    def test_isdisjoint(self):
        t = self._makeOne()
        K = self.KEYS
        # The empty set is disjoint with itself
        self.assertTrue(t.isdisjoint(t))
        # Empty sequences
        self.assertTrue(t.isdisjoint(()))
        self.assertTrue(t.isdisjoint([]))
        self.assertTrue(t.isdisjoint(set()))
        # non-empty sequences but empty set
        self.assertTrue(t.isdisjoint((K[1], K[2])))
        self.assertTrue(t.isdisjoint([K[1], K[2]]))
        self.assertTrue(t.isdisjoint({K[1], K[2]}))
        self.assertTrue(t.isdisjoint(K[k] for k in range(10)))

        # non-empty sequences and non-empty set, null intersection
        self._populate(t, 2)
        self.assertEqual(set(t), {K[0], K[1]})

        self.assertTrue(t.isdisjoint((K[2], K[3])))
        self.assertTrue(t.isdisjoint([K[2], K[3]]))
        self.assertTrue(t.isdisjoint({K[2], K[3]}))
        self.assertTrue(t.isdisjoint(K[k] for k in range(2, 10)))

        # non-null intersection
        self.assertFalse(t.isdisjoint(t))
        self.assertFalse(t.isdisjoint((K[0],)))
        self.assertFalse(t.isdisjoint((K[1],)))
        self.assertFalse(t.isdisjoint([K[2], K[3], K[0]]))
        self.assertFalse(t.isdisjoint({K[2], K[3], K[1]}))
        self.assertFalse(t.isdisjoint(K[k] for k in range(1, 10)))

    def test_discard(self):
        t = self._makeOne()
        K = self.KEYS
        # empty set, raises no error, even if the key is
        # of the wrong type
        t.discard(K[1])
        t.discard(object())
        self.assertEqual(set(t), set())

        # non-empty set, discarding absent key
        self._populate(t, 2)
        self.assertEqual(set(t), {K[0], K[1]})
        t.discard(K[3])
        t.discard(object())
        self.assertEqual(set(t), {K[0], K[1]})

        t.discard(K[1])
        self.assertEqual(set(t), {K[0]})
        t.discard(K[0])
        self.assertEqual(set(t), set())

    def test_pop(self):
        t = self._makeOne()
        K = self.KEYS
        with self.assertRaises(KeyError):
            t.pop()

        self._populate(t, 2)
        self.assertEqual(K[0], t.pop())
        self.assertEqual(K[1], t.pop())
        self.assertEqual(set(t), set())
        with self.assertRaises(KeyError):
            t.pop()

    def test___ior__(self):
        t = self._makeOne()
        K = self.KEYS
        orig_t = t
        t |= (K[1],)
        t |= [K[2],]
        t |= {K[1], K[2], K[3]}
        t |= (K[k] for k in range(10))
        t |= t
        self.assertIs(t, orig_t)
        self.assertEqual(set(t), {K[k] for k in range(10)})

    def test___iand__(self):
        t = self._makeOne()
        K = self.KEYS
        orig_t = t
        t &= (K[1],)
        t &= [K[2],]
        t &= {K[3], K[4]}
        self.assertIs(t, orig_t)
        self.assertEqual(set(t), set())

        self._populate(t, 10)
        self.assertEqual(set(t), {K[k] for k in range(10)})

        t &= (K[1], K[2], K[3])
        self.assertIs(t, orig_t)
        self.assertEqual(set(t), {K[1], K[2], K[3]})

    def test___isub__(self):
        t = self._makeOne()
        K = self.KEYS
        orig_t = t
        t -= (K[1],)
        t -= [K[2],]
        t -= {K[3], K[4]}
        self.assertIs(t, orig_t)
        self.assertEqual(set(t), set())

        self._populate(t, 10)
        self.assertEqual(set(t), {K[k] for k in range(10)})

        t -= (K[1], K[2], K[3])
        self.assertIs(t, orig_t)
        self.assertEqual(set(t), {K[0], K[4], K[5], K[6], K[7], K[8], K[9]})

        t -= t
        self.assertIs(t, orig_t)
        self.assertEqual(set(t), set())

    def test___ixor__(self):
        t = self._makeOne()
        orig_t = t
        K = self.KEYS
        t ^= (K[1],)
        self.assertEqual(set(t), {K[1],})
        t ^= t
        self.assertEqual(set(t), set())

        t ^= (K[1], K[2], K[3])
        self.assertEqual(set(t), {K[1], K[2], K[3]})
        t ^= [K[2], K[3], K[4]]
        self.assertEqual(set(t), {K[1], K[4]})

    def test___xor__(self):
        t = self._makeOne()
        K = self.KEYS
        u = t ^ (K[1],)
        self.assertEqual(set(u), {K[1],})
        u = t ^ t
        self.assertEqual(set(u), set())

        u = t ^ (K[1], K[2], K[3])
        self.assertEqual(set(u), {K[1], K[2], K[3]})
        t.update(u)
        u = t ^ [K[2], K[3], K[4]]
        self.assertEqual(set(u), {K[1], K[4]})

    def testShortRepr(self):
        t = self._makeOne()
        K = self.KEYS
        for i in range(5):
            t.add(K[i])
        t._p_oid = b'12345678'
        r = repr(t)
        # Make sure the repr is **not* 10000 bytes long for a shrort bucket.
        # (the buffer must be terminated when copied).
        self.assertTrue(len(r) < 10000)
        # Make sure the repr is human readable, unless it's a tree
        if 'TreeSet' not in r:
            self.assertTrue(r.endswith("Set(%r)" % t.keys()))
        else:
            # persistent-4.4 changed the default reprs, adding
            # oid and jar reprs
            self.assertIn("<BTrees.", r)
            self.assertIn('TreeSet object at', r)
            self.assertIn('oid 0x3132333435363738', r)

        # Make sure it's the same between Python and C
        self.assertNotIn('Py', r)


    def testInsertReturnsValue(self):
        t = self._makeOne()
        K = self.KEYS
        self.assertEqual(t.insert(K[5]), 1)
        self.assertEqual(t.add(K[4]), 1)

    def testDuplicateInsert(self):
        t = self._makeOne()
        k = self.KEYS[5]
        t.insert(k)
        self.assertEqual(t.insert(k), 0)
        self.assertEqual(t.add(k), 0)

    def testInsert(self):
        t = self._makeOne()
        K = self.KEYS
        t.insert(K[1])
        self.assertTrue(K[1] in t)
        self.assertTrue(K[2] not in t)

    def testBigInsert(self):
        t = self._makeOne()
        r = range(10000)
        to_key = self.coerce_to_key
        for x in r:
            t.insert(to_key(x))
        for x in r:
            x = to_key(x)
            self.assertTrue(x in t)

    def testRemoveSucceeds(self):
        t = self._makeOne()
        r = range(10000)
        to_key = self.coerce_to_key
        for x in r:
            t.insert(to_key(x))
        for x in r:
            t.remove(to_key(x))

    def testRemoveFails(self):
        self.assertRaises(KeyError, self._removenonexistent)

    def _removenonexistent(self):
        self._makeOne().remove(self.KEYS[1])

    def testHasKeyFails(self):
        t = self._makeOne()
        self.assertTrue(1 not in t)

    def testKeys(self):
        t = self._makeOne()
        r = [self.KEYS[x] for x in range(1000)]
        for x in r:
            t.insert(x)
        diff = lsubtract(t.keys(), r)
        self.assertEqual(diff, [])
        diff = lsubtract(t.keys(None, None), r)
        self.assertEqual(diff, [])


    def testClear(self):
        t = self._makeOne()
        r = range(1000)
        K = self.KEYS
        for x in r:
            t.insert(K[x])
        t.clear()
        diff = lsubtract(t.keys(), [])
        self.assertEqual(diff, [], diff)

    def testMaxKeyMinKey(self):
        t = self._makeOne()
        K = self.KEYS
        t.insert(K[1])
        t.insert(K[2])
        t.insert(K[3])
        t.insert(K[8])
        t.insert(K[5])
        t.insert(K[10])
        t.insert(K[6])
        t.insert(K[4])
        self.assertEqual(t.maxKey(), K[10])
        self.assertEqual(t.maxKey(None), K[10])
        self.assertEqual(t.maxKey(K[6]), K[6])
        self.assertEqual(t.maxKey(K[9]), K[8])
        self.assertEqual(t.minKey(), K[1])
        self.assertEqual(t.minKey(None), K[1])
        self.assertEqual(t.minKey(K[3]), K[3])
        self.assertEqual(t.minKey(K[9]), K[10])
        self.assertTrue(t.minKey() in t)
        self.assertTrue(t.maxKey() in t)
        try:
            bigger = t.maxKey() + 1
        except TypeError:
            assert 'fs' in type(t).__name__
        else:
            self.assertTrue(bigger not in t)
            self.assertTrue(t.minKey() - 1 not in t)
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
        d = {}
        l = []
        for i in range(10000):
            k = random.randrange(*self.KEY_RANDRANGE_ARGS)
            k = self.coerce_to_key(k)
            d[k] = self.coerce_to_value(i)
            l.append(k)

        items = sorted(d.keys())

        t.update(l)
        self.assertEqual(list(t.keys()), items)

    def testEmptyRangeSearches(self):
        t = self._makeOne()
        K = self.KEYS
        t.update([K[1], K[5], K[9]])
        if self.SUPPORTS_NEGATIVE_KEYS:
            self.assertEqual(list(t.keys(-6, -4)), [])

        self.assertEqual(list(t.keys(K[2], K[4])), [])
        self.assertEqual(list(t.keys(K[6], K[8])), [])
        self.assertEqual(list(t.keys(K[10], K[12])), [])
        self.assertEqual(list(t.keys(K[9], K[1])), [])

        # For IITreeSets, this one was returning 31 for len(keys), and
        # list(keys) produced a list with 100 elements.
        t.clear()
        t.update(K[k] for k in range(300))
        keys = t.keys(K[200], K[50])
        self.assertEqual(len(keys), 0)
        self.assertEqual(list(keys), [])

        keys = t.keys(max=K[50], min=K[200])
        self.assertEqual(len(keys), 0)
        self.assertEqual(list(keys), [])

    def testSlicing(self):
        # Test that slicing of .keys() works exactly the same way as slicing
        # a Python list with the same contents.
        t = self._makeOne()
        for n in range(10):
            t.clear()
            self.assertEqual(len(t), 0)

            keys = [self.coerce_to_key(x) for x in range(10 * n, 11 * n)]
            t.update(keys)
            self.assertEqual(len(t), n)

            kslice = t.keys()
            self.assertEqual(len(list(kslice)), n)

            # Test whole-structure slices.
            x = kslice[:]
            self.assertEqual(list(x), list(keys[:]))

            for lo in range(-2 * n, 2 * n + 1):
                # Test one-sided slices.
                x = kslice[:lo]
                self.assertEqual(list(x), list(keys[:lo]))
                x = kslice[lo:]
                self.assertEqual(list(x), list(keys[lo:]))

                for hi in range(-2 * n, 2 * n + 1):
                    # Test two-sided slices.
                    x = kslice[lo:hi]
                    self.assertEqual(list(x), list(keys[lo:hi]))

    def testIterator(self):
        t = self._makeOne()

        for keys in [], [-2], [1, 4], list(range(-170, 2000, 6)):
            t.clear()
            if keys and keys[0] < 0 and not self.SUPPORTS_NEGATIVE_KEYS:
                with self.assertRaises(UnsignedError):
                    t.update(keys)
                continue

            keys = [self.coerce_to_key(k) for k in keys]
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
        class Jar:
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
        t.add(self.KEYS[0])
        t.add(self.KEYS[1])
        # reset these, setting _firstbucket triggered a change
        t._p_changed = False
        t._p_jar.registered = None

        # now remove the second value
        t.remove(self.KEYS[1])
        self.assertTrue(t._p_changed)
        self.assertEqual(t, t._p_jar.registered)

    def testAddingOneSetsChanged(self):
        # A bug in the BTree Set Python implementation once caused
        # adding an object not to set _p_changed
        t = self._makeOne()
        # Note that for the property to actually hold, we have to fake a
        # _p_jar and _p_oid
        t._p_oid = b'\0\0\0\0\0'
        class Jar:
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
        t.add(self.KEYS[0])
        self.assertTrue(t._p_changed)
        self.assertEqual(t, t._p_jar.registered)

        # Whether or not doing `t.add(0)` again would result in
        # _p_changed being set depends on whether this is a TreeSet or a plain Set


class ExtendedSetTests(NormalSetTests):

    def testLen(self):
        t = self._makeOne()
        r = range(10000)
        to_key = self.coerce_to_key
        for x in r:
            t.insert(to_key(x))
        self.assertEqual(len(t), 10000, len(t))

    def testGetItem(self):
        t = self._makeOne()
        r = range(10000)
        to_key = self.coerce_to_key
        for x in r:
            t.insert(to_key(x))
        for x in r:
            self.assertEqual(t[x], to_key(x))

class KeyCoercionFailed(Exception):
    """Raised when we use a static key that we expect to be able to fit."""

class InternalKeysMappingTest:
    # There must not be any internal keys not in the BTree

    def _makeOne(self):
        return self._getTargetClass()()

    def add_key(self, tree, i):
        value = self.coerce_to_value(i)
        try:
            key = self.coerce_to_key(i)
        except TypeError:
            raise KeyCoercionFailed(i)

        tree[key] = value

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

        # Grow the btree until we have multiple buckets.
        # (Calling ``__getstate__`` to check the internals is expensive, especially
        # with the Python implementation, so only do so when we hit the threshold we expect
        # the tree to grow. This makes the difference between a 6s test and a 0.6s test.)
        bucket_size = self.key_type.bucket_size_for_value(self.value_type)
        tree_size = self.key_type.tree_size
        while 1:
            i += 1
            self.add_key(tree, i)
            if i >= bucket_size:
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
            try:
                self.add_key(tree, i)
            except KeyCoercionFailed:
                # Only expected in fsbtree
                assert i == 32768 and type(tree).__name__.startswith('fs')
                break
            if i >= tree_size * bucket_size:
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


class ModuleTest:
    # test for presence of generic names in module
    prefix = ''
    key_type = None
    value_type = None
    def _getModule(self):
        raise NotImplementedError

    def testNames(self):
        names = ['Bucket', 'BTree', 'Set', 'TreeSet']
        mod = self._getModule()
        mod_all = mod.__all__
        for name in names:
            klass = getattr(mod, name)
            self.assertEqual(klass.__module__, mod.__name__)
            self.assertIs(klass, getattr(mod,
                                         self.prefix + name))
            self.assertIn(name, mod_all)
            self.assertIn(self.prefix + name, mod_all)

        # BBB for zope.app.security ZCML :(
        pfx_iter = self.prefix + 'TreeIterator'
        klass = getattr(mod, pfx_iter)
        self.assertEqual(klass.__module__, mod.__name__)

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

    def _check_union_presence(self, datatype, name):
        mod = self._getModule()
        if datatype.supports_value_union():
            in_ = self.assertIn
            has = self.assertTrue
        else:
            in_ = self.assertNotIn
            has = self.assertFalse

        in_(name, dir(mod))
        has(hasattr(mod, name))
        in_(name, mod.__all__)

    # The weighted* functions require the value type to support unions.
    def test_weightedUnion_presence(self):
        self._check_union_presence(self.value_type, 'weightedUnion')

    def test_weightedIntersection_presence(self):
        self._check_union_presence(self.value_type, 'weightedIntersection')

    # The multiunion function requires the key type to support unions
    def test_multiunion_presence(self):
        self._check_union_presence(self.key_type, 'multiunion')


class I_SetsBase:

    def setUp(self):
        super().setUp()
        _skip_if_pure_py_and_py_test(self)

    def _getTargetClass(self):
        raise NotImplementedError

    def _makeOne(self):
        return self._getTargetClass()()

    def testBadBadKeyAfterFirst(self):
        with self.assertRaises(TypeError):
            self._getTargetClass()([1, object()])

        t = self._makeOne()
        with self.assertRaises(TypeError):
            t.update([1, object()])

    def __test_key(self, k):
        try:
            self.key_type(k)
        except Exception as e: # pylint:disable=broad-except
            with self.assertRaises(type(e)):
                self._makeOne().insert(k)
        else:
            self._makeOne().insert(k)

    def test_key_type_str(self):
        self.__test_key('c')

    def test_key_type_float(self):
        self.__test_key(2.5)

    def test_key_type_None(self):
        self.__test_key(None)


LARGEST_32_BITS = 2147483647
SMALLEST_32_BITS = -LARGEST_32_BITS - 1

SMALLEST_POSITIVE_33_BITS = LARGEST_32_BITS + 1
LARGEST_NEGATIVE_33_BITS = SMALLEST_32_BITS - 1

LARGEST_64_BITS = 0x7fffffffffffffff # Signed. 2**63 - 1
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
        # These values must be usable as keys.
        return 0, 1

    def _skip_if_not_64bit(self):
        mod = sys.modules[self._getTargetClass().__module__]
        if not mod.using64bits:
            self.skipTest("Needs 64 bit support.") # pragma: no cover

class TestLongIntKeys(TestLongIntSupport):
    SUPPORTS_NEGATIVE_KEYS = True

    def _makeLong(self, v):
        try:
            return long(v)
        except NameError: # pragma: no cover
            return int(v)

    def testLongIntKeysWork(self):
        self._skip_if_not_64bit()
        t = self._makeOne()
        K = self.KEYS
        V = self.VALUES
        o1, o2 = self.getTwoValues()
        assert o1 != o2

        # Test some small key values first:
        one_long = self._makeLong(1)
        t[one_long] = o1
        self.assertEqual(t[K[1]], o1)
        t[K[1]] = o2
        self.assertEqual(t[one_long], o2)
        self.assertEqual(list(t.keys()), [1])
        self.assertEqual(list(t.keys(None, None)), [1])

        # Test some large key values too:
        k1 = SMALLEST_POSITIVE_33_BITS
        k2 = LARGEST_64_BITS
        k3 = SMALLEST_64_BITS if self.SUPPORTS_NEGATIVE_KEYS else 0
        t[k1] = o1
        t[k2] = o2
        t[k3] = o1
        self.assertEqual(t[k1], o1)
        self.assertEqual(t[k2], o2)
        self.assertEqual(t[k3], o1)
        self.assertEqual(list(t.keys()), [k3, 1, k1, k2])
        self.assertEqual(list(t.keys(k3, None)), [k3, 1, k1, k2])
        self.assertEqual(list(t.keys(None, k2)), [k3, 1, k1, k2])

    def testLongIntKeysOutOfRange(self):
        self._skip_if_not_64bit()
        o1, o2 = self.getTwoValues()
        t = self._makeOne()
        k1 = SMALLEST_POSITIVE_65_BITS if self.SUPPORTS_NEGATIVE_KEYS else 2**64 + 1
        with self.assertRaises(TypeError):
            t[k1] = self.coerce_to_value(o1)

        t = self._makeOne()
        with self.assertRaises(TypeError):
            t[LARGEST_NEGATIVE_65_BITS] = self.coerce_to_value(o1)

class TestLongIntValues(TestLongIntSupport):
    SUPPORTS_NEGATIVE_VALUES = True
    def testLongIntValuesWork(self):
        self._skip_if_not_64bit()
        t = self._makeOne()
        keys = sorted(self.getTwoKeys())
        k1, k2 = keys
        assert k1 != k2

        # This is the smallest positive integer that requires 33 bits:
        v1 = SMALLEST_POSITIVE_33_BITS
        v2 = v1 + 1

        t[k1] = self.coerce_to_value(v1)
        t[k2] = self.coerce_to_value(v2)
        self.assertEqual(t[k1], v1)
        self.assertEqual(t[k2], v2)
        self.assertEqual(list(t.values()), [v1, v2])
        self.assertEqual(list(t.values(None, None)), [v1, v2])

    def testLongIntValuesOutOfRange(self):
        self._skip_if_not_64bit()
        k1, k2 = self.getTwoKeys()
        t = self._makeOne()
        v1 = SMALLEST_POSITIVE_65_BITS if self.SUPPORTS_NEGATIVE_VALUES else 2**64 + 1
        with self.assertRaises(TypeError):
            t[k1] = self.coerce_to_value(v1)

        t = self._makeOne()
        with self.assertRaises(TypeError):
            t[k1] = self.coerce_to_value(LARGEST_NEGATIVE_65_BITS)


# Given a mapping builder (IIBTree, OOBucket, etc), return a function
# that builds an object of that type given only a list of keys.
def makeMapBuilder(self, mapbuilder):
    def result(keys=(), mapbuilder=mapbuilder, self=self):
        return mapbuilder(list(zip(
            (self.KEYS[k] for k in keys),
            (self.VALUES[k] for k in keys)
        )))
    return result

def makeSetBuilder(self, setbuilder):
    def result(keys=(), setbuilder=setbuilder, self=self):
        return setbuilder(self.KEYS[k] for k in keys)
    return result

# Subclasses have to set up:
#     builders() - function returning functions to build inputs,
#     each returned callable takes an optional keys arg
#     intersection, union, difference - set to the type-correct versions
class SetResult:
    def setUp(self):
        super().setUp()
        _skip_if_pure_py_and_py_test(self)

        rawAkeys = [1,    3,    5, 6] # pylint:disable=bad-whitespace
        rawBkeys = [   2, 3, 4,    6, 7] # pylint:disable=bad-whitespace
        self.Akeys = [self.KEYS[k] for k in rawAkeys]
        self.Bkeys = [self.KEYS[k] for k in rawBkeys]
        self.As = [makeset(rawAkeys) for makeset in self.builders()]
        self.Bs = [makeset(rawBkeys) for makeset in self.builders()]
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
            self.assertIsNone(C)

        for op in self.union, self.intersection, self.difference:
            for A in self.As:
                C = op(A, None)
                self.assertIs(C, A)

                C = op(None, A)
                if op == self.difference:
                    self.assertIsNone(C, None)
                else:
                    self.assertIs(C, A)

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

    def _reversed(self, x):
        x = list(x)
        x.reverse()
        return x

    def testUnion(self):
        inputs = self.As + self.Bs
        for A in inputs:
            for B in inputs:
                for convert in lambda x: x, self._reversed, list, tuple, set:
                    # For all of these tests, we need to be sure we have at least
                    # one value that is *not* sorted relative to the other.
                    # See https://github.com/zopefoundation/BTrees/issues/171
                    a = convert(A)
                    b = convert(B)
                    if hasattr(b, 'reverse'):
                        b.reverse()
                    __traceback_info__ = a, b
                    C = self.union(a, b)
                    self.assertTrue(not hasattr(C, "values"))
                    self.assertEqual(list(C), self._union(a, b))
                    self.assertEqual(set(A) | set(B), set(A | B))

    def testIntersection(self):
        inputs = self.As + self.Bs
        for A in inputs:
            for B in inputs:
                for convert in lambda x: x, self._reversed, list, tuple, set:
                    a = convert(A)
                    b = convert(B)
                    if hasattr(b, 'reverse'):
                        b.reverse()
                    __traceback_info__ = a, b
                    C = self.intersection(a, b)
                    self.assertTrue(not hasattr(C, "values"))
                    self.assertEqual(list(C), self._intersection(A, B))
                    self.assertEqual(set(A) & set(B), set(A & B))

    def testDifference(self):
        inputs = self.As + self.Bs
        for A in inputs:
            for B in inputs:
                for convert in lambda x: x, self._reversed, list, tuple, set:
                    # Difference is unlike the others: The first argument
                    # must be a BTree type, in both C and Python.
                    C = self.difference(A, convert(B))
                    # Difference preserves LHS values.
                    self.assertEqual(hasattr(C, "values"), hasattr(A, "values"))
                    want = self._difference(A, B)
                    if hasattr(A, "values"):
                        self.assertEqual(list(C.items()), want)
                    else:
                        self.assertEqual(list(C), want)
                    self.assertEqual(set(A) - set(B), set(A - B))

    def testLargerInputs(self): # pylint:disable=too-many-locals
        from BTrees.IIBTree import IISet # pylint:disable=no-name-in-module
        from random import randint
        MAXSIZE = 200
        MAXVAL = 400
        K = self.KEYS
        for i in range(3):
            n = randint(0, MAXSIZE)
            Akeys = [randint(1, MAXVAL) for j in range(n)]
            As = [makeset(Akeys) for makeset in self.builders()]
            Akeys = IISet(Akeys)

            n = randint(0, MAXSIZE)
            Bkeys = [randint(1, MAXVAL) for j in range(n)]
            Bs = [makeset(Bkeys) for makeset in self.builders()]
            Bkeys = IISet(Bkeys)

            Akeys = [K[k] for k in Akeys]
            Bkeys = [K[k] for k in Bkeys]

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
class Weighted(SignedMixin):

    def setUp(self):
        self.Aitems = [(1, 10), (3, 30), (5, 50), (6, 60)]
        self.Bitems = [(2, 21), (3, 31), (4, 41), (6, 61), (7, 71)]

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
                    if (w1 < 0 or w2 < 0) and not self.SUPPORTS_NEGATIVE_VALUES:
                        continue
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
                    if (w1 < 0 or w2 < 0) and not self.SUPPORTS_NEGATIVE_VALUES:
                        continue
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
class MultiUnion(SignedMixin):

    def setUp(self):
        super().setUp()
        _skip_if_pure_py_and_py_test(self)

    def testEmpty(self):
        self.assertEqual(len(self.multiunion([])), 0)

    def _testOne(self, builder):
        for sequence in (
                [3],
                list(range(20)),
                list(range(-10, 0, 2)) + list(range(1, 10, 2)),
        ):
            if min(sequence) < 0 and not self.SUPPORTS_NEGATIVE_KEYS:
                continue
            seq1 = sequence[:]
            seq2 = list(reversed(sequence[:]))
            seqsorted = sorted(sequence[:])
            for seq in seq1, seq2, seqsorted:
                input = builder(seq)
                output = self.multiunion([input])
                self.assertEqual(len(seq), len(output))
                self.assertEqual(seqsorted, list(output))

    def testOneBTSet(self):
        self._testOne(self.mkset)

    def testOneBTTreeSet(self):
        self._testOne(self.mktreeset)

    def testOneList(self):
        self._testOne(list)

    def testOneTuple(self):
        self._testOne(tuple)

    def testOneSet(self):
        self._testOne(set)

    def testOneGenerator(self):
        def generator(seq):
            yield from seq

        self._testOne(generator)

    def testValuesIgnored(self):
        for builder in self.mkbucket, self.mkbtree, dict:
            input = builder([(1, 2), (3, 4), (5, 6)])
            output = self.multiunion([input])
            self.assertEqual([1, 3, 5], list(output))

    def testValuesIgnoredNonInteger(self):
        # This only uses a dict because the bucket and tree can't
        # hold non-integers.
        i1 = {1: 'a', 2: 'b'}
        i2 = {1: 'c', 3: 'd'}

        output = self.multiunion((i1, i2))
        self.assertEqual([1, 2, 3], list(output))

    def testRangeInputs(self):
        i1 = range(3)
        i2 = range(7)

        output = self.multiunion((i1, i2))
        self.assertEqual([0, 1, 2, 3, 4, 5, 6], list(output))

    def testNegativeKeys(self):
        i1 = (-1, -2, -3)
        i2 = (0, 1, 2)

        if not self.SUPPORTS_NEGATIVE_KEYS:
            with self.assertRaises(TypeError):
                self.multiunion((i2, i1))
        else:
            output = self.multiunion((i2, i1))
            self.assertEqual([-3, -2, -1, 0, 1, 2], list(output))

    def testOneIterableWithBadKeys(self):
        i1 = [1, 2, 3, 'a']
        for kind in list, tuple:
            with self.assertRaises(TypeError):
                self.multiunion((kind(i1),))

    def testBadIterable(self):
        class MyException(Exception):
            pass

        def gen():
            yield from range(3)
            raise MyException

        with self.assertRaises(MyException):
            self.multiunion((gen(),))

    def testBigInput(self):
        N = 100000
        if (_c_optimizations_ignored() or 'Py' in type(self).__name__) and not PYPY:
            # This is extremely slow in CPython implemented in Python,
            # taking 20s or more on a 2015-era laptop
            N = N // 10
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
            if self.SUPPORTS_NEGATIVE_KEYS:
                base = i * 4 - N
            else:
                base = i * 4
            inputs.append(mkset([base, base + 1]))
            inputs.append(mktreeset([base + 2, base + 3]))
        shuffle(inputs)
        output = self.multiunion(inputs)
        self.assertEqual(len(output), N * 4)
        if self.SUPPORTS_NEGATIVE_KEYS:
            self.assertEqual(list(output), list(range(-N, 3 * N)))
        else:
            self.assertEqual(list(output), list(range(N * 4)))

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


class ConflictTestBase(SignedMixin):
    # Tests common to all types: sets, buckets, and BTrees

    storage = None
    db = None

    def setUp(self):
        super().setUp()
        _skip_if_pure_py_and_py_test(self)
        def identity(x):
            return x

        self.key_tx = abs if not self.SUPPORTS_NEGATIVE_KEYS else identity
        self.val_tx = abs if not self.SUPPORTS_NEGATIVE_VALUES else identity

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


    def _test_merge(self, o1, o2, o3, expect, message='failed to merge', should_fail=False):
        from BTrees.Interfaces import BTreesConflictError
        s1 = o1.__getstate__()
        s2 = o2.__getstate__()
        s3 = o3.__getstate__()
        expected = expect.__getstate__()
        if expected is None:
            expected = ((((),),),)

        if should_fail:
            with self.assertRaises(BTreesConflictError):
                __traceback_info__ = message
                o1._p_resolveConflict(s1, s2, s3)
        else:
            merged = o1._p_resolveConflict(s1, s2, s3)
            self.assertEqual(merged, expected, message)


class MappingConflictTestBase(ConflictTestBase):
    # Tests common to mappings (buckets, btrees).

    def _skip_if_only_small_keys(self):
        try:
            self.coerce_to_key(99999)
        except TypeError:
            assert 'fs' in self._getTargetClass().__name__
            self.skipTest("Uses keys too large for fsBTree")


    def _deletefail(self):
        t = self._makeOne()
        del t[self.KEYS[1]]

    def _setupConflict(self):
        if self._getTargetClass().__name__.startswith('fs'):
            # Too many negative numbers, could be done with a little work though.
            self.skipTest("Needs ported to fsBTree")
        key_tx = self.key_tx
        l = [
            -5124, -7377, 2274, 8801, -9901, 7327, 1565, 17, -679,
            3686, -3607, 14, 6419, -5637, 6040, -4556, -8622, 3847, 7191,
            -4067
        ]
        l = [key_tx(v) for v in l]

        e1 = [(-1704, 0), (5420, 1), (-239, 2), (4024, 3), (-6984, 4)]
        e1 = [(key_tx(k), v) for k, v in e1]
        e2 = [(7745, 0), (4868, 1), (-2548, 2), (-2711, 3), (-3154, 4)]
        e2 = [(key_tx(k), v) for k, v in e2]

        base = self._makeOne()
        base.update([
            (self.coerce_to_key(i), self.coerce_to_value(i * i))
            for i in l[:20]
        ])
        b1 = type(base)(base)
        b2 = type(base)(base)
        bm = type(base)(base)

        items = base.items()

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
        self._test_merge(base, b1, b2, bm, 'merge  delete')

    def testMergeDeleteAndUpdate(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        V = self.VALUES
        del b1[items[1][0]]
        b2[items[5][0]] = V[1]
        del b1[items[-1][0]]
        b2[items[-2][0]] = V[2]
        del bm[items[1][0]]
        bm[items[5][0]] = V[1]
        del bm[items[-1][0]]
        bm[items[-2][0]] = V[2]
        self._test_merge(base, b1, b2, bm, 'merge update and delete')

    def testMergeUpdate(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        V = self.VALUES
        b1[items[0][0]] = V[1]
        b2[items[5][0]] = V[2]
        b1[items[-1][0]] = V[3]
        b2[items[-2][0]] = V[4]
        bm[items[0][0]] = V[1]
        bm[items[5][0]] = V[2]
        bm[items[-1][0]] = V[3]
        bm[items[-2][0]] = V[4]
        self._test_merge(base, b1, b2, bm, 'merge update')

    def testFailMergeDelete(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        del b1[items[0][0]]
        del b2[items[0][0]]
        self._test_merge(base, b1, b2, bm, 'merge conflicting delete',
                         should_fail=1)

    def testFailMergeUpdate(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        V = self.VALUES
        b1[items[0][0]] = V[1]
        b2[items[0][0]] = V[2]
        self._test_merge(base, b1, b2, bm, 'merge conflicting update',
                         should_fail=1)

    def testFailMergeDeleteAndUpdate(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        del b1[items[0][0]]
        b2[items[0][0]] = self.val_tx(-9)
        self._test_merge(base, b1, b2, bm, 'merge conflicting update and delete',
                         should_fail=1)

    def testMergeInserts(self):
        self._skip_if_only_small_keys()
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        V = self.VALUES
        b1[self.key_tx(-99999)] = self.val_tx(-99999)
        b1[e1[0][0]] = e1[0][1]
        b2[99999] = self.coerce_to_value(99999)
        b2[e1[2][0]] = e1[2][1]

        bm[self.key_tx(-99999)] = self.val_tx(-99999)
        bm[e1[0][0]] = e1[0][1]
        bm[99999] = self.coerce_to_value(99999)
        bm[e1[2][0]] = e1[2][1]
        self._test_merge(base, b1, b2, bm, 'merge insert',
                         should_fail=not self.SUPPORTS_NEGATIVE_KEYS)

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

        self._test_merge(base, b1, b2, bm, 'merge insert from empty')

    def testFailMergeEmptyAndFill(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        b1.clear()
        bm.clear()
        b2.update(e2)
        bm.update(e2)

        self._test_merge(base, b1, b2, bm, 'merge insert from empty', should_fail=1)

    def testMergeEmpty(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        b1.clear()
        bm.clear()

        self._test_merge(base, b1, b2, bm, 'empty one and not other', should_fail=1)

    def testFailMergeInsert(self):
        self._skip_if_only_small_keys()
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        V = self.VALUES
        b1[self.key_tx(-99999)] = self.val_tx(-99999)
        b1[e1[0][0]] = e1[0][1]
        b2[99999] = self.coerce_to_value(99999)
        b2[e1[0][0]] = e1[0][1]
        self._test_merge(base, b1, b2, bm, 'merge conflicting inserts',
                         should_fail=1)


class SetConflictTestBase(ConflictTestBase):
    "Set (as opposed to TreeSet) specific tests."

    def _skip_if_only_small_keys(self):
        try:
            self.coerce_to_key(99999)
        except TypeError:
            assert 'fs' in self._getTargetClass().__name__
            self.skipTest("Uses keys too large for fsBTree")

    def _setupConflict(self):
        to_key = lambda x: self.coerce_to_key(self.key_tx(x))
        l = [to_key(x)for x in [
            -5124, -7377, 2274, 8801, -9901, 7327, 1565, 17, -679,
            3686, -3607, 14, 6419, -5637, 6040, -4556, -8622, 3847, 7191,
            -4067]]

        e1 = [to_key(x) for x in
              [-1704, 5420, -239, 4024, -6984]]
        e2 = [to_key(x) for x in
              [7745, 4868, -2548, -2711, -3154]]


        base = self._makeOne()
        base.update(l)
        b1 = base.__class__(base)
        b2 = base.__class__(base)
        bm = base.__class__(base)

        items = base.keys()

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
        self._test_merge(base, b1, b2, bm, 'merge  delete')

    def testFailMergeDelete(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        b1.remove(items[0])
        b2.remove(items[0])
        self._test_merge(base, b1, b2, bm, 'merge conflicting delete',
                         should_fail=1)

    def testMergeInserts(self):
        self._skip_if_only_small_keys()
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        b1.insert(self.key_tx(-99999))
        b1.insert(e1[0])
        b2.insert(99999)
        b2.insert(e1[2])

        bm.insert(self.key_tx(-99999))
        bm.insert(e1[0])
        bm.insert(99999)
        bm.insert(e1[2])
        self._test_merge(base, b1, b2, bm, 'merge insert',
                         should_fail=not self.SUPPORTS_NEGATIVE_KEYS)

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

        self._test_merge(base, b1, b2, bm, 'merge insert from empty')

    def testFailMergeEmptyAndFill(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        b1.clear()
        bm.clear()
        b2.update(e2)
        bm.update(e2)

        self._test_merge(base, b1, b2, bm, 'merge insert from empty', should_fail=1)

    def testMergeEmpty(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        b1.clear()
        bm.clear()

        self._test_merge(base, b1, b2, bm, 'empty one and not other', should_fail=1)

    def testFailMergeInsert(self):
        self._skip_if_only_small_keys()
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        b1.insert(self.coerce_to_key(self.key_tx(-99999)))
        b1.insert(e1[0])
        b2.insert(99999)
        b2.insert(e1[0])
        self._test_merge(base, b1, b2, bm, 'merge conflicting inserts',
                         should_fail=1)

## utility functions

def lsubtract(l1, l2):
    l1 = list(l1)
    l2 = list(l2)
    return (list(filter(lambda x, l1=l1: x not in l1, l2)) +
            list(filter(lambda x, l2=l2: x not in l2, l1)))

def realseq(itemsob):
    return list(itemsob)

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
