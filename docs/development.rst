=======================
 Developer Information
=======================

This document provides information for developers who maintain or extend
`BTrees`.

Macros
======

`BTrees` are defined using a "template", roughly akin to a C++ template.  To
create a new family of `BTrees`, create a source file that defines macros used
to handle differences in key and value types:


Configuration Macros
--------------------

``MASTER_ID``

    A string to hold an RCS/CVS Id key to be included in compiled binaries.

``MOD_NAME_PREFIX``

    A string (like "IO" or "OO") that provides the prefix used for the module.
    This gets used to generate type names and the internal module name string.

Macros for Keys
---------------

``KEY_TYPE``

    The C type declaration for keys (e.g., ``int`` or ``PyObject*``).

``KEY_TYPE_IS_PYOBJECT``

    Define if ``KEY_TYPE`` is a ``PyObject*`, else ``undef``.

``KEY_CHECK(K)``

    Tests whether the ``PyObject* K`` can be converted to the (``C``) key type
    (``KEY_TYPE``).  The macro should return a boolean (zero for false,
    non-zero for true).  When it returns false, its caller should probably set
    a ``TypeError`` exception.

``KEY_CHECK_ON_SET(K)``

    Like ``KEY_CHECK``, but only checked during ``__setitem__``.

``TEST_KEY_SET_OR(V, K, T)``

    Like Python's ``cmp()``.  Compares K(ey) to T(arget), where ``K``
    and ``T`` are ``C`` values of type `KEY_TYPE`.  ``V`` is assigned an `int`
    value depending on the outcome::

       < 0 if K < T
      == 0 if K == T
       > 0 if K > T

    This macro acts like an ``if``, where the following statement is executed
    only if a Python exception has been raised because the values could not be
    compared.

``DECREF_KEY(K)``

    ``K`` is a value of ``KEY_TYPE``.  If ``KEY_TYPE`` is a flavor of
    ``PyObject*``, write this to do ``Py_DECREF(K)``.  Else (e.g.,
    ``KEY_TYPE`` is ``int``) make it a nop.

``INCREF_KEY(K)``

    ``K`` is a value of `KEY_TYPE`.  If `KEY_TYPE` is a flavor of
    ``PyObject*``, write this to do ``Py_INCREF(K)``.  Else (e.g., `KEY_TYPE`
    is ``int``) make it a nop.

``COPY_KEY(K, E)``

    Like ``K=E``.  Copy a key from ``E`` to ``K``, both of ``KEY_TYPE``.  Note
    that this doesn't ``decref K`` or ``incref E`` when ``KEY_TYPE`` is a
    ``PyObject*``; the caller is responsible for keeping refcounts straight.

``COPY_KEY_TO_OBJECT(O, K)``

    Roughly like ``O=K``.  ``O`` is a ``PyObject*``, and the macro must build
    a Python object form of ``K``, assign it to ``O``, and ensure that ``O``
    owns the reference to its new value.  It may do this by creating a new
    Python object based on ``K`` (e.g., ``PyInt_FromLong(K)`` when
    ``KEY_TYPE`` is ``int``), or simply by doing ``Py_INCREF(K)`` if
    ``KEY_TYPE`` is a ``PyObject*``.

``COPY_KEY_FROM_ARG(TARGET, ARG, STATUS)``

    Copy an argument to the target without creating a new reference to
    ``ARG``.  ``ARG`` is a ``PyObject*``, and ``TARGET`` is of type
    ``KEY_TYPE``.  If this can't be done (for example, ``KEY_CHECK(ARG)``
    returns false), set a Python error and set status to ``0``.  If there is
    no error, leave status alone.


Macros for Values
-----------------

``VALUE_TYPE``

    The C type declaration for values (e.g., ``int`` or ``PyObject*``).

``VALUE_TYPE_IS_PYOBJECT``

    Define if ``VALUE_TYPE`` is a ``PyObject*``, else ``undef``.

``TEST_VALUE(X, Y)``

    Like Python's ``cmp()``.  Compares ``X`` to ``Y``, where ``X`` & ``Y`` are
    ``C`` values of type ``VALUE_TYPE``.  The macro returns an ``int``, with
    value::

       < 0 if X < Y
      == 0 if X == Y
       > 0 if X > Y

    Bug: There is no provision for determining whether the comparison attempt
    failed (set a Python exception).

``DECREF_VALUE(K)``

    Like ``DECREF_KEY``, except applied to values of ``VALUE_TYPE``.

``INCREF_VALUE(K)``

    Like ``INCREF_KEY``, except applied to values of ``VALUE_TYPE``.

``COPY_VALUE(K, E)``

    Like ``COPY_KEY``, except applied to values of ``VALUE_TYPE``.

``COPY_VALUE_TO_OBJECT(O, K)``

    Like ``COPY_KEY_TO_OBJECT``, except applied to values of ``VALUE_TYPE``.

``COPY_VALUE_FROM_ARG(TARGET, ARG, STATUS)``

    Like ``COPY_KEY_FROM_ARG``, except applied to values of ``VALUE_TYPE``.

``NORMALIZE_VALUE(V, MIN)``

    Normalize the value, ``V``, using the parameter ``MIN``.  This is almost
    certainly a YAGNI.  It is a no-op for most types. For integers, ``V`` is
    replaced by ``V/MIN`` only if ``MIN > 0``.


Macros for Set Operations
-------------------------

``MERGE_DEFAULT``

    A value of ``VALUE_TYPE`` specifying the value to associate with set
    elements when sets are merged with mappings via weighed union or weighted
    intersection.

``MERGE(O1, w1, O2, w2)``

    Performs a weighted merge of two values, ``O1`` and ``O2``, using weights
    ``w1`` and ``w2``.  The result must be of ``VALUE_TYPE``.  Note that
    weighted unions and weighted intersections are not enabled if this macro
    is left undefined.

``MERGE_WEIGHT(O, w)``

    Computes a weighted value for ``O``.  The result must be of
    ``VALUE_TYPE``.  This is used for "filling out" weighted unions, i.e. to
    compute a weighted value for keys that appear in only one of the input
    mappings.  If left undefined, ``MERGE_WEIGHT`` defaults to::

      #define MERGE_WEIGHT(O, w) (O)

``MULTI_INT_UNION``

    The value doesn't matter.  If defined, `SetOpTemplate.c` compiles code for
    a ``multiunion()`` function (compute a union of many input sets at high
    speed).  This currently makes sense only for structures with integer keys.

Datatypes
=========

There are two tunable values exposed on BTree and TreeSet classes.
Their default values are found in ``_datatypes.py`` and shared across
C and Python.


``max_leaf_size``

    An int giving the maximum bucket size (number of key/value pairs).
    When a bucket gets larger than this due to an insertion *into a
    BTREE*, it splits. Inserting into a bucket directly doesn't split,
    and functions that produce a bucket output (e.g., ``union()``)
    also have no bound on how large a bucket may get. This used to
    come from the C macro ``DEFAULT_MAX_BUCKET_SIZE``.


``max_internal_size``

    An ``int`` giving the maximum size (number of children) of an
    internal btree node. This used to come from the C macro
    ``DEFAULT_MAX_BTREE_SIZE``


BTree Clues
===========

More or less random bits of helpful info.

+ In papers and textbooks, this flavor of BTree is usually called a B+-Tree,
  where "+" is a superscript.

+ All keys and all values live in the bucket leaf nodes.  Keys in interior
  (BTree) nodes merely serve to guide a search efficiently toward the correct
  leaf.

+ When a key is deleted, it's physically removed from the bucket it's in, but
  this doesn't propagate back up the tree: since keys in interior nodes only
  serve to guide searches, it's OK-- and saves time --to leave "stale" keys in
  interior nodes.

+ No attempt is made to rebalance the tree after a deletion, unless a bucket
  thereby becomes entirely empty.  "Classic BTrees" do rebalance, keeping all
  buckets at least half full (provided there are enough keys in the entire
  tree to fill half a bucket).  The tradeoffs are murky.  Pathological cases
  in the presence of deletion do exist.  Pathologies include trees tending
  toward only one key per bucket, and buckets at differing depths (all buckets
  are at the same depth in a classic BTree).

+ ``max_leaf_size`` and ``max_internal_size`` are chosen mostly
  to "even out" pickle sizes in storage.  That's why, e.g., an `IIBTree` has
  larger values than an `OOBTree`: pickles store ints more efficiently than
  they can store arbitrary Python objects.

+ In a non-empty BTree, every bucket node contains at least one key, and every
  BTree node contains at least one child and a non-NULL firstbucket pointer.
  However, a BTree node may not contain any keys.

+ An empty BTree consists solely of a BTree node with ``len==0`` and
  ``firstbucket==NULL``.

+ Although a BTree can become unbalanced under a mix of inserts and deletes
  (meaning both that there's nothing stronger that can be said about buckets
  than that they're not empty, and that buckets can appear at different
  depths), a BTree node always has children of the same kind: they're all
  buckets, or they're all BTree nodes.


The ``BTREE_SEARCH`` Macro
==========================

For notational ease, consider a fixed BTree node ``x``, and let

::

    K(i) mean x->data.key[i]
    C(i) mean all the keys reachable from x->data.child[i]

For each ``i`` in ``0`` to ``x->len-1`` inclusive,

::

    K(i) <= C(i) < K(i+1)

is a BTree node invariant, where we pretend that ``K(0)`` holds a key smaller
than any possible key, and ``K(x->len)`` holds a key larger than any possible
key.  (Note that ``K(x->len)`` doesn't actually exist, and ``K(0)`` is never
used although space for it exists in non-empty BTree nodes.)

When searching for a key ``k``, then, the child pointer we want to follow is
the one at index ``i`` such that ``K(i) <= k < K(i+1)``.  There can be at most
one such ``i``, since the ``K(i)`` are strictly increasing.  And there is at
least one such ``i`` provided the tree isn't empty (so that ``0 < len``).  For
the moment, assume the tree isn't empty (we'll get back to that later).

The macro's chief loop invariant is

::

    K(lo) < k < K(hi)

This holds trivially at the start, since ``lo`` is set to ``0``, and ``hi`` to
``x->len``, and we pretend ``K(0)`` is minus infinity and ``K(len)`` is plus
infinity.  Inside the loop, if ``K(i) < k`` we set ``lo`` to ``i``, and if
``K(i) > k`` we set ``hi`` to ``i``.  These obviously preserve the invariant.
If ``K(i) == k``, the loop breaks and sets the result to ``i``, and since
``K(i) == k`` in that case ``i`` is obviously the correct result.

Other cases depend on how ``i = floor((lo + hi)/2)`` works, exactly.  Suppose
``lo + d = hi`` for some ``d >= 0``.  Then ``i = floor((lo + lo + d)/2) =
floor(lo + d/2) = lo + floor(d/2)``.  So:

a. ``[d == 0] (lo == i == hi)`` if and only if ``(lo == hi)``.
b. ``[d == 1] (lo == i  < hi)`` if and only if ``(lo+1 == hi)``.
c. ``[d  > 1] (lo  < i  < hi)`` if and only if ``(lo+1  < hi)``.

If the node is empty ``(x->len == 0)``, then ``lo==i==hi==0`` at the start,
and the loop exits immediately (the first ``i > lo`` test fails), without
entering the body.

Else ``lo < hi`` at the start, and the invariant ``K(lo) < k < K(hi)`` holds.

If ``lo+1 < hi``, we're in case (c): ``i`` is strictly between ``lo`` and
``hi``, so the loop body is entered, and regardless of whether the body sets
the new ``lo`` or the new ``hi`` to ``i``, the new ``lo`` is strictly less
than the new ``hi``, and the difference between the new ``lo`` and new ``hi``
is strictly less than the difference between the old ``lo`` and old ``hi``.
So long as the new ``lo + 1`` remains < the new ``hi``, we stay in this case.
We can't stay in this case forever, though: because ``hi-lo`` decreases on
each trip but remains > ``0``, ``lo+1 == hi`` must eventually become true.
(In fact, it becomes true quickly, in about ``log2(x->len)`` trips; the point
is more that ``lo`` doesn't equal ``hi`` when the loop ends, it has to end
with ``lo+1==hi`` and ``i==lo``).

Then we're in case (b):  ``i==lo==hi-1`` then, and the loop exits.  The
invariant still holds, with ``lo==i`` and ``hi==lo+1==i+1``::

    K(i) < k < K(i+1)

so ``i`` is again the correct answer.


Optimization points
-------------------

+ Division by 2 is done via shift rather via "/2".  These are signed ints, and
  almost all C compilers treat signed int division as truncating, and shifting
  is not the same as truncation for signed int division.  The compiler has no
  way to know these values aren't negative, so has to generate longer-winded
  code for "/2".  But we know these values aren't negative, and exploit it.

+ The order of _cmp comparisons matters.  We're in an interior BTree node, and
  are looking at only a tiny fraction of all the keys that exist.  So finding
  the key exactly in this node is unlikely, and checking ``_cmp == 0`` is a
  waste of time to the same extent.  It doesn't matter whether we check for
  ``_cmp < 0`` or ``_cmp > 0`` first, so long as we do both before worrying
  about equality.

+ At the start of a routine, it's better to run this macro even if ``x->len``
  is ``0`` (check for that afterwards).  We just called a function and so
  probably drained the pipeline.  If the first thing we do then is read up
  ``self->len`` and check it against ``0``, we just sit there waiting for the
  data to get read up, and then another immediate test-and-branch, and for a
  very unlikely case (BTree nodes are rarely empty).  It's better to get into
  the loop right away so the normal case makes progress ASAP.


The ``BUCKET_SEARCH`` Macro
===========================

This has a different job than ``BTREE_SEARCH``: the key ``0`` slot is
legitimate in a bucket, and we want to find the index at which the key
belongs.  If the key is larger than the bucket's largest key, a new slot at
index len is where it belongs, else it belongs at the smallest ``i`` with
``keys[i]`` >= the key we're looking for.  We also need to know whether or not
the key is present (``BTREE_SEARCH`` didn't care; it only wanted to find the
next node to search).

The mechanics of the search are quite similar, though.  The primary
loop invariant changes to (say we're searching for key ``k``)::

    K(lo-1) < k < K(hi)

where ``K(i)`` means ``keys[i]``, and we pretend ``K(-1)`` is minus infinity
and ``K(len)`` is plus infinity.

If the bucket is empty, ``lo=hi=i=0`` at the start, the loop body is never
entered, and the macro sets ``INDEX`` to 0 and ``ABSENT`` to true.  That's why
``_cmp`` is initialized to 1 (``_cmp`` becomes ``ABSENT``).

Else the bucket is not empty, lo<hi at the start, and the loop body is
entered.  The invariant is obviously satisfied then, as ``lo=0`` and
``hi=len``.

If ``K[i]<k``, ``lo`` is set to ``i+1``, preserving that ``K(lo-1) = K[i] <
k``.

If ``K[i]>k``, ``hi`` is set to ``i``, preserving that ``K[hi] = K[i] > k``.

If the loop exits after either of those, ``_cmp != 0``, so ``ABSENT`` becomes
true.

If ``K[i]=k``, the loop breaks, so that ``INDEX`` becomes ``i``, and
``ABSENT`` becomes false (``_cmp=0`` in this case).

The same case analysis for ``BTREE_SEARCH`` on ``lo`` and ``hi`` holds here:

a. ``(lo == i == hi)`` if and only if ``(lo   == hi)``.
b. ``(lo == i  < hi)`` if and only if ``(lo+1 == hi)``.
c. ``(lo  < i  < hi)`` if and only if ``(lo+1  < hi)``.

So long as ``lo+1 < hi``, we're in case (c), and either break with equality
(in which case the right results are obviously computed) or narrow the range.
If equality doesn't obtain, the range eventually narrows to cases (a) or (b).

To go from (c) to (a), we must have ``lo+2==hi`` at the start, and
``K[i]=K[lo+1]<k``.  Then the new lo gets set to ``i+1 = lo+2 = hi``, and the
loop exits with ``lo=hi=i`` and ``_cmp<0``.  This is correct, because we know
that ``k != K(i)`` (loop invariant! we actually know something stronger, that
``k < K(hi)``; since ``i=hi``, this implies ``k != K(i)``).

Else (c) eventually falls into case (b), ``lo+1==hi`` and ``i==lo``.  The
invariant tells us ``K(lo-1) < k < K(hi) = K(lo+1)``, so if the key is present
it must be at ``K(lo)``.  ``i==lo`` in this case, so we test ``K(lo)`` against
``k``.  As always, if equality obtains we do the right thing, else case #b
becomes case (a).

When (b) becomes (a), the last comparison was non-equal, so ``_cmp`` is
non-zero, and the loop exits because ``lo==hi==i`` in case (a).  The invariant
then tells us ``K(lo-1) < k < K(lo)``, so the key is in fact not present, it's
correct to exit with ``_cmp`` non-zero, and ``i==lo`` is again the index at
which ``k`` belongs.


Optimization points
-------------------

+ As for ``BTREE_SEARCH``, shifting of signed ints is cheaper than division.

+ Unlike as for ``BTREE_SEARCH``, there's nothing special about searching an
  empty bucket, and the macro computes thoroughly sensible results in that
  case.

+ The order of ``_cmp`` comparisons differs from ``BTREE_SEARCH``.  When
  searching a bucket, it's much more likely (than when searching a BTree node)
  that the key is present, so testing ``__cmp==0`` isn't a systematic waste of
  cycles.  At the extreme, if all searches are successful (key present), on
  average this saves one comparison per search, against leaving the
  determination of ``_cmp==0`` implicit (as ``BTREE_SEARCH`` does).  But even
  on successful searches, ``__cmp != 0`` is a more popular outcome than
  ``__cmp == 0`` across iterations (unless the bucket has only a few keys), so
  it's important to check one of the inequality cases first.  It turns out
  it's better on average to check ``K(i) < key`` (than to check ``K(i) >
  key``), because when it pays it narrows the range more (we get a little
  boost from setting ``lo=i+1`` in this case; the other case sets ``hi=i``,
  which isn't as much of a narrowing).
