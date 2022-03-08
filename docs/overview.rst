==========
 Overview
==========

When programming with the ZODB, Python dictionaries aren't always what you
need.  The most important case is where you want to store a very large
mapping.  When a Python dictionary is accessed in a ZODB, the whole
dictionary has to be unpickled and brought into memory.  If you're storing
something very large, such as a 100,000-entry user database, unpickling
such a large object will be slow. BTrees are a balanced tree data
structure that behave like a mapping but distribute keys throughout a
number of tree nodes.  The nodes are stored in sorted order (this has
important consequences -- see below).  Nodes are then only unpickled and
brought into memory as they're accessed, so the entire tree doesn't have to
occupy memory (unless you really are touching every single key).

Related Data Structures
=======================

The BTrees package provides a large collection of related data
structures. The most general data structures store arbitrary ordered_
objects. There are variants of the data structures specialized to
numbers, which are faster and more memory efficient than those dealing
with objects. There are several modules that handle the different
variants. The first two letters of the module name specify the types
of the keys and values in mappings. For example, the
:mod:`BTrees.IOBTree` module provides a mapping with 32-bit integer
keys and arbitrary objects as values.

.. list-table:: Data Type Notation
   :widths: auto
   :class: wrapped
   :header-rows: 1

   * - Letter
     - Mnemonic Device
     - Data Type
     - Notes
   * - O
     - "Object"
     - Any sortable Python object
     -
   * - I
     - "Integer"
     - 32-bit signed integer
     - Values from ``-2**31 - 1`` through ``2**31 - 1`` (about plus or
       minus two billion)
   * - L
     - "Long integer"
     - 64-bit signed integer
     - Values from ``-2**63 - 1`` through
       ``2**63 - 1`` (about plus or minus nine quintillion)
   * - F
     - "Float"
     - 32-bit C-language ``float``
     - New in ZODB 3.4
   * - U
     - "Unsigned"
     - 32-bit unsigned integer
     - (New in BTrees 4.7.0) Values from 0 through ``2**32`` (about four billion)
   * - Q
     - "Quad"
     - 64-bit unsigned integer
     - Values from 0 through ``2**64`` (about 18 quintillion) (New in BTrees 4.7.0)


The four data structures provide by each module are a BTree, a Bucket,
a TreeSet, and a Set. The BTree and Bucket types are mappings and
support all the usual mapping methods, e.g.
:func:`~BTrees.Interfaces.ISetMutable.update` and
:func:`~BTrees.Interfaces.IKeyed.keys`. The TreeSet and Set types are
similar to mappings but they have no values; they support the methods
that make sense for a mapping with no keys, e.g.
:func:`~BTrees.Interfaces.IKeyed.keys` but not
:func:`~BTrees.Interfaces.IMinimalDictionary.items`. The Bucket and
Set types are the individual building blocks for BTrees and TreeSets,
respectively. A Bucket or Set can be used when you are sure that it
will have few elements. If the data structure will grow large, you
should use a BTree or TreeSet. Like Python lists, Buckets and Sets are
allocated in one contiguous piece, and insertions and deletions can
take time proportional to the number of existing elements. Also like
Python lists, a Bucket or Set is a single object, and is pickled and
unpickled in its entirety. BTrees and TreeSets are multi-level tree
structures with much better (logarithmic) worst- case time bounds, and
the tree structure is built out of multiple objects, which ZODB can
load individually as needed.

The two letter prefixes are repeated in the data types names. For
example, the
:mod:`BTrees.OOBTree` module defines the following types:
:class:`BTrees.OOBTree.OOBTree`, :class:`BTrees.OOBTree.OOBucket`,
:class:`BTrees.OOBTree.OOSet`, and
:class:`BTrees.OOBTree.OOTreeSet`. Similarly, the other modules
each define their own variants of those four types.

For convenience, BTrees groups the most closely related data
structures together into a "family" (defined by
:class:`BTrees.Interfaces.IBTreeFamily`). :obj:`BTrees.family32`
groups 32-bit data structures, while :obj:`BTrees.family64` contains
64-bit data structures. It is a common practice for code that creates
BTrees to be parameterized on the family so that the caller can choose
the desired characteristics.


Behaviour
=========

The `keys`, :func:`values`, and :func:`items` methods on BTree and
TreeSet types do not materialize a list with all of the data.  Instead,
they return lazy sequences that fetch data from the BTree as needed.  They
also support optional arguments to specify the minimum and maximum values
to return, often called "range searching".  Because all these types are
stored in sorted order, range searching is very efficient.

The :func:`keys`, :func:`values`, and :func:`items` methods on Bucket and
Set types do return lists with all the data. Starting in ZODB 3.3, there
are also :func:`iterkeys`, :func:`itervalues`, and :func:`iteritems`
methods that return iterators (in the Python 2.2 sense).  Those methods
also apply to BTree and TreeSet objects.

A BTree object supports all the methods you would expect of a mapping, with
a few extensions that exploit the fact that the keys are sorted. The
example below demonstrates how some of the methods work.  The extra methods
are :func:`minKey` and :func:`maxKey`, which find the minimum and maximum
key value subject to an optional bound argument, and :func:`byValue`, which
should probably be ignored (it's hard to explain exactly what it does, and
as a result it's almost never used -- best to consider it deprecated).  The
various methods for enumerating keys, values and items also accept minimum
and maximum key arguments ("range search"), and (new in ZODB 3.3) optional
Boolean arguments to control whether a range search is inclusive or
exclusive of the range's endpoints.

.. doctest::

   >>> from BTrees.OOBTree import OOBTree
   >>> t = OOBTree()
   >>> t.update({1: "red", 2: "green", 3: "blue", 4: "spades"})
   >>> len(t)
   4
   >>> t[2]
   'green'
   >>> s = t.keys() # this is a "lazy" sequence object
   >>> s
   <...TreeItems object at ...>
   >>> len(s)  # it acts like a Python list
   4
   >>> s[-2]
   3
   >>> list(s) # materialize the full list
   [1, 2, 3, 4]
   >>> list(t.values())
   ['red', 'green', 'blue', 'spades']
   >>> list(t.values(1, 2)) # values at keys in 1 to 2 inclusive
   ['red', 'green']
   >>> list(t.values(2))    # values at keys >= 2
   ['green', 'blue', 'spades']
   >>> list(t.values(min=1, max=4))  # keyword args new in ZODB 3.3
   ['red', 'green', 'blue', 'spades']
   >>> list(t.values(min=1, max=4, excludemin=True, excludemax=True))
   ['green', 'blue']
   >>> t.minKey()     # smallest key
   1
   >>> t.minKey(1.5)  # smallest key >= 1.5
   2
   >>> [k for k in t.keys()]
   [1, 2, 3, 4]
   >>> [k for k in t]    # new in ZODB 3.3
   [1, 2, 3, 4]
   >>> [pair for pair in t.iteritems()]  # new in ZODB 3.3
   [(1, 'red'), (2, 'green'), (3, 'blue'), (4, 'spades')]
   >>> t.has_key(4)  # returns a true value
   True
   >>> t.has_key(5)
   False
   >>> 4 in t  # new in ZODB 3.3
   True
   >>> 5 in t  # new in ZODB 3.3
   False
   >>>


Each of the modules also defines some functions that operate on BTrees --
:func:`~BTrees.Interfaces.IMerge.difference`, :func:`~BTrees.Interfaces.IMerge.union`, and :func:`~BTrees.Interfaces.IMerge.intersection`.  The
:func:`~BTrees.Interfaces.IMerge.difference` function returns a Bucket, while the other two methods return
a Set. If the keys are integers, then the module also defines
:func:`~BTrees.Interfaces.IMergeIntegerKey.multiunion`.  If the values are integers or floats, then the module also
defines :func:`~BTrees.Interfaces.IIMerge.weightedIntersection` and :func:`~BTrees.Interfaces.IIMerge.weightedUnion`.  The function
doc strings describe each function briefly.

.. % XXX I'm not sure all of the following is actually correct.  The
.. % XXX set functions have complicated behavior.

:mod:`~BTrees.Interfaces` defines the operations, and is the official
documentation.  Note that the interfaces don't define the concrete types
returned by most operations, and you shouldn't rely on the concrete types that
happen to be returned:  stick to operations guaranteed by the interface.  In
particular, note that the interfaces don't specify anything about comparison
behavior, and so nothing about it is guaranteed.  In ZODB 3.3, for example, two
BTrees happen to use Python's default object comparison, which amounts to
comparing the (arbitrary but fixed) memory addresses of the BTrees. This may or
may not be true in future releases. If the interfaces don't specify a behavior,
then whether that behavior appears to work, and exactly happens if it does
appear to work, are undefined and should not be relied on.

.. _ordered:

Total Ordering and Persistence
==============================

The BTree-based data structures differ from Python dicts in several fundamental
ways.  One of the most important is that while dicts require that keys support
hash codes and equality comparison, the BTree-based structures don't use hash
codes and require a total ordering on keys.

Total ordering means three things:

#. Reflexive.  For each *x*, ``x == x`` is true.

#. Trichotomy.  For each *x* and *y*, exactly one of ``x < y``, ``x == y``, and
   ``x > y`` is true.

#. Transitivity.  Whenever ``x <= y`` and ``y <= z``, it's also true that ``x <=
   z``.

The default comparison functions for most objects that come with Python satisfy
these rules, with some crucial cautions explained later.  Complex numbers are an
example of an object whose default comparison function does not satisfy these
rules:  complex numbers only support ``==`` and ``!=`` comparisons, and raise an
exception if you try to compare them in any other way.  They don't satisfy the
trichotomy rule, and must not be used as keys in BTree-based data structures
(although note that complex numbers can be used as keys in Python dicts, which
do not require a total ordering).

Examples of objects that are wholly safe to use as keys in BTree-based
structures include ints, longs, floats, 8-bit strings, Unicode strings, and
tuples composed (possibly recursively) of objects of wholly safe types.

It's important to realize that even if two types satisfy the rules on their own,
mixing objects of those types may not.  For example, 8-bit strings and Unicode
strings both supply total orderings, but mixing the two loses trichotomy; e.g.,
``'x' < chr(255)`` and ``u'x' == 'x'``, but trying to compare ``chr(255)`` to
``u'x'`` raises an exception.  Partly for this reason (another is given later),
it can be dangerous to use keys with multiple types in a single BTree-based
structure.  Don't try to do that, and you don't have to worry about it.

Another potential problem is mutability:  when a key is inserted in a BTree-
based structure, it must retain the same order relative to the other keys over
time.  This is easy to run afoul of if you use mutable objects as keys.  For
example, lists supply a total ordering, and then

.. doctest::

   >>> L1, L2, L3 = [1], [2], [3]
   >>> from BTrees.OOBTree import OOSet
   >>> s = OOSet((L2, L3, L1))  # this is fine, so far
   >>> list(s.keys())           # note that the lists are in sorted order
   [[1], [2], [3]]
   >>> s.has_key([3])           # and [3] is in the set
   True
   >>> L2[0] = 5                # horrible -- the set is insane now
   >>> s.has_key([3])           # for example, it's insane this way
   False
   >>> s.__class__
   <class 'BTrees.OOBTree.OOSet'>
   >>> list(s)
   [[1], [5], [3]]

Key lookup relies on that the keys remain in sorted order (an efficient form of
binary search is used).  By mutating key L2 after inserting it, we destroyed the
invariant that the OOSet is sorted.  As a result, all future operations on this
set are unpredictable.

A subtler variant of this problem arises due to persistence:  by default, Python
does several kinds of comparison by comparing the memory addresses of two
objects.  Because Python never moves an object in memory, this does supply a
usable (albeit arbitrary) total ordering across the life of a program run (an
object's memory address doesn't change).  But if objects compared in this way
are used as keys of a BTree-based structure that's stored in a database, when
the objects are loaded from the database again they will almost certainly wind
up at different memory addresses.  There's no guarantee then that if key K1 had
a memory address smaller than the memory address of key K2 at the time K1 and K2
were inserted in a BTree, K1's address will also be smaller than K2's when that
BTree is loaded from a database later.  The result will be an insane BTree,
where various operations do and don't work as expected, seemingly at random.

Now each of the types identified above as "wholly safe to use" never compares
two instances of that type by memory address, so there's nothing to worry about
here if you use keys of those types.  The most common mistake is to use keys
that are instances of a user-defined class that doesn't supply its own
:meth:`__cmp__` method.  Python compares such instances by memory address.  This
is fine if such instances are used as keys in temporary BTree-based structures
used only in a single program run.  It can be disastrous if that BTree-based
structure is stored to a database, though.

.. doctest::
   :options: +SKIP

   >>> class C:
   ...     pass
   ...
   >>> a, b = C(), C()
   >>> print(a < b)   # this may print 0 if you try it
   True
   >>> del a, b
   >>> a, b = C(), C()
   >>> print(a < b)   # and this may print 0 or 1
   False
   >>>

That example illustrates that comparison of instances of classes that don't
define :meth:`__cmp__` yields arbitrary results (but consistent results within a
single program run).

Another problem occurs with instances of classes that do define :meth:`__cmp__`,
but define it incorrectly.  It's possible but rare for a custom :meth:`__cmp__`
implementation to violate one of the three required formal properties directly.
It's more common for it to "fall back" to address-based comparison by mistake.
For example,

.. doctest::

   >>> class Mine:
   ...     def __cmp__(self, other):
   ...         if other.__class__ is Mine:
   ...             return cmp(self.data, other.data)
   ...         else:
   ...             return cmp(self.data, other)

It's quite possible there that the :keyword:`else` clause allows a result to be
computed based on memory address.  The bug won't show up until a BTree-based
structure uses objects of class :class:`Mine` as keys, and also objects of other
types as keys, and the structure is loaded from a database, and a sequence of
comparisons happens to execute the :keyword:`else` clause in a case where the
relative order of object memory addresses happened to change.

This is as difficult to track down as it sounds, so best to stay far away from
the possibility.

You'll stay out of trouble by follwing these rules, violating them only with
great care:

#. Use objects of simple immutable types as keys in BTree-based data structures.

#. Within a single BTree-based data structure, use objects of a single type as
   keys.  Don't use multiple key types in a single structure.

#. If you want to use class instances as keys, and there's any possibility that
   the structure may be stored in a database, it's crucial that the class define a
   :meth:`__cmp__` method, and that the method is carefully implemented.

   Any part of a comparison implementation that relies (explicitly or implicitly)
   on an address-based comparison result will eventually cause serious failure.

#. Do not use :class:`~persistent.Persistent` objects as keys, or objects of a subclass of
   :class:`~persistent.Persistent`.

That last item may be surprising.  It stems from details of how conflict
resolution is implemented:  the states passed to conflict resolution do not
materialize persistent subobjects (if a persistent object P is a key in a BTree,
then P is a subobject of the bucket containing P).  Instead, if an object O
references a persistent subobject P directly, and O is involved in a conflict,
the states passed to conflict resolution contain an instance of an internal
:class:`~persistent.PersistentReference` stub class everywhere O references P. Two
:class:`~persistent.PersistentReference` instances compare equal if and only if they
"represent" the same persistent object; when they're not equal, they compare by
memory address, and, as explained before, memory-based comparison must never
happen in a sane persistent BTree.  Note that it doesn't help in this case if
your :class:`~persistent.Persistent` subclass defines a sane :meth:`__cmp__` method:
conflict resolution doesn't know about your class, and so also doesn't know
about its :meth:`__cmp__` method.  It only sees instances of the internal
:class:`~persistent.PersistentReference` stub class.


Iteration and Mutation
======================

As with a Python dictionary or list, you should not mutate a BTree-based data
structure while iterating over it, except that it's fine to replace the value
associated with an existing key while iterating.  You won't create internal
damage in the structure if you try to remove, or add new keys, while iterating,
but the results are undefined and unpredictable.  A weak attempt is made to
raise :exc:`RuntimeError` if the size of a BTree-based structure changes while
iterating, but it doesn't catch most such cases, and is also unreliable.
Example

.. doctest::
   :options: +SKIP

   >>> from BTrees.IIBTree import IISet
   >>> s = IISet(range(10))
   >>> list(s)
   [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
   >>> for i in s:  # the output is undefined
   ...     print(i)
   ...     s.remove(i)
   0
   2
   4
   6
   8
   Traceback (most recent call last):
     File "<stdin>", line 1, in ?
   RuntimeError: the bucket being iterated changed size
   >>> list(s)      # this output is also undefined
   [1, 3, 5, 7, 9]
   >>>

Also as with Python dictionaries and lists, the safe and predictable way to
mutate a BTree-based structure while iterating over it is to iterate over a copy
of the keys.  Example

.. doctest::

   >>> from BTrees.IIBTree import IISet
   >>> s = IISet(range(10))
   >>> for i in list(s.keys()):  # this is well defined
   ...     print(i)
   ...     s.remove(i)
   0
   1
   2
   3
   4
   5
   6
   7
   8
   9
   >>> list(s)
   []
   >>>

BTree node sizes
================

BTrees (and TreeSets) are made up of a tree of Buckets (and Sets) and
internal nodes.  There are maximum sizes of these notes configured for
the various key and value types (unsigned and quad unsigned follow
integer and long, respectively):

======== ========== ========================== =============================
Key Type Value Type Maximum Bucket or Set Size Maximum BTree or TreeSet Size
======== ========== ========================== =============================
Integer  Float      120                        500
Integer  Integer    120                        500
Integer  Object     60                         500
Long     Float      120                        500
Long     Long       120                        500
Long     Object     60                         500
Object   Integer    60                         250
Object   Long       60                         250
Object   Object     30                         250
======== ========== ========================== =============================

For your application, especially when using object keys or values, you
may want to override the default sizes.  You can do this by
subclassing any of the BTree (or TreeSet) classes and specifying new
values for ``max_leaf_size`` or ``max_internal_size`` in your subclass::

     >>> import BTrees.OOBTree

     >>> class MyBTree(BTrees.OOBTree.BTree):
     ...     max_leaf_size = 500
     ...     max_internal_size = 1000

As of version 4.9, you can also set these values directly on an
existing BTree class if you wish to tune them across your entire application.

``max_leaf_size`` is used for leaf nodes in a BTree, either Buckets or
Sets.  ``max_internal_size`` is used for internal nodes, either BTrees
or TreeSets.

BTree Diagnostic Tools
======================

A BTree (or TreeSet) is a complex data structure, really a graph of variable-
size nodes, connected in multiple ways via three distinct kinds of C pointers.
There are some tools available to help check internal consistency of a BTree as
a whole.

Most generally useful is the :mod:`~BTrees.check` module.  The
:func:`~BTrees.check.check` function examines a BTree (or Bucket, Set, or TreeSet) for
value-based consistency, such as that the keys are in strictly increasing order.
See the function docstring for details. The :func:`~BTrees.check.display` function
displays the internal structure of a BTree.

BTrees and TreeSets also have a :meth:`_check` method.  This verifies that the
(possibly many) internal pointers in a BTree or TreeSet are mutually consistent,
and raises :exc:`AssertionError` if they're not.

If a :func:`~BTrees.check.check` or :meth:`_check` call fails, it may point to a bug in
the implementation of BTrees or conflict resolution, or may point to database
corruption.

Repairing a damaged BTree is usually best done by making a copy of it. For
example, if *self.data* is bound to a corrupted IOBTree,

.. doctest::
   :options: +SKIP

   >>> self.data = IOBTree(self.data)

usually suffices.  If object identity needs to be preserved,

.. doctest::
   :options: +SKIP

   >>> acopy = IOBTree(self.data)
   >>> self.data.clear()
   >>> self.data.update(acopy)

does the same, but leaves *self.data* bound to the same object.
