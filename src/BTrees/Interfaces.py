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

from zope.interface import Attribute
from zope.interface import Interface
from zope.interface.common.collections import IMapping
from zope.interface.common.collections import ISized
from zope.interface.common.sequence import IMinimalSequence


class ICollection(Interface):
    """
    A collection of zero or more objects.

    In a boolean context, objects implementing this interface are
    `True` if the collection is non-empty, and `False` if the
    collection is empty.
    """

    def clear():
        """Remove all of the items from the collection."""


# Backwards compatibility alias. To be removed in 5.0.
# Docs deprecated only in docs/api.rst.
IReadSequence = IMinimalSequence


class IKeyed(ICollection):

    def has_key(key):
        """Check whether the object has an item with the given key.

        Return a true value if the key is present, else a false value.
        """

    def keys(min=None, max=None, excludemin=False, excludemax=False):
        """
        Return an :mod:`IMinimalSequence <zope.interface.common.sequence>`
        containing the keys in the collection.

        The type of the ``IMinimalSequence`` is not specified. It
        could be a `list` or a `tuple` or some other type.

        All arguments are optional, and may be specified as keyword
        arguments, or by position.

        If a *min* is specified, then output is constrained to keys
        greater than or equal to the given min, and, if *excludemin*
        is specified and true, is further constrained to keys strictly
        greater than *min*. A *min* value of `None` is ignored. If
        *min* is `None` or not specified, and *excludemin* is true,
        the smallest key is excluded.

        If a *max* is specified, then output is constrained to keys
        less than or equal to the given *max*, and, if *excludemax* is
        specified and true, is further constrained to keys strictly
        less than *max*. A *max* value of `None` is ignored. If *max*
        is `None` or not specified, and *excludemax* is true, the
        largest key is excluded.
        """

    def maxKey(key=None):
        """Return the maximum key.

        If a key argument if provided and not None, return the largest key
        that is less than or equal to the argument.  Raise an exception if
        no such key exists.
        """

    def minKey(key=None):
        """Return the minimum key.

        If a key argument if provided and not None, return the smallest key
        that is greater than or equal to the argument.  Raise an exception
        if no such key exists.
        """


class ISetMutable(IKeyed):

    def insert(key):
        """Add the key (value) to the set.

        If the key was already in the set, return 0, otherwise return 1.
        """

    def remove(key):
        """Remove the key from the set.

        Raises :class:`KeyError` if key is not in the set.
        """

    def update(seq):
        """Add the items from the given sequence to the set."""

    def __and__(other):
        """
        Shortcut for :meth:`~BTrees.Interfaces.IMerge.intersection`

        .. versionadded:: 4.8.0
        """

    def __iand__(other):
        """
        As for :meth:`set.intersection_update`: Update this object,
        keeping only elements found in both it and other.

        .. versionadded:: 4.8.0
        """

    def __or__(other):
        """
        Shortcut for :meth:`~BTrees.Interfaces.IMerge.union`

        .. versionadded:: 4.8.0
        """

    def __ior__(other):
        """
        As for :meth:`set.update`: Update this object, adding
        elements from *other*.

        .. versionadded:: 4.8.0
        """

    def __sub__(other):
        """
        Shortcut for :meth:`~BTrees.Interfaces.IMerge.difference`

        .. versionadded:: 4.8.0
        """

    def __isub__(other):
        """
        As for :meth:`set.difference_update`: Update this object,
        removing elements found in *other*.

        .. versionadded:: 4.8.0
        """

    def isdisjoint(other):
        """
        As for :meth:`set.isdisjoint`: Return True if the set has no
        elements in common with other.

        .. versionadded:: 4.8.0
        """

    def discard(key):
        """
        As for :meth:`set.discard`: Remove the *key* from the set,
        but only if it is present.

        .. versionadded:: 4.8.0
        """

    def pop():
        """
        As for :meth:`set.pop`: Remove and return an arbitrary element;
        raise :exc:`KeyError` if the object is empty.

        .. versionadded:: 4.8.0
        """

    def __ixor__(other):
        """
        As for :meth:`set.symmetric_difference_update`: Update this object,
        keeping only elements found in either set but not in both.

        .. versionadded:: 4.8.0
        """


class IKeySequence(IKeyed, ISized):

    def __getitem__(index):
        """Return the key in the given index position.

        This allows iteration with for loops and use in functions,
        like map and list, that read sequences.
        """


class ISet(ISetMutable, IKeySequence):
    """
    A set of unique items stored in a single persistent object.
    """


class ITreeSet(ISetMutable):
    """
    A set of unique items stored in a tree of persistent objects.
    """


class IMinimalDictionary(IKeyed, IMapping):
    """
    Mapping operations.

    .. versionchanged:: 4.8.0
       Now extends :class:`zope.interface.common.collections.IMapping`.
    """

    def get(key, default):
        """Get the value associated with the given key.

        Return the default if :meth:`~BTrees.Interfaces.IKeyed.has_key` is
        false with the given key.
        """

    def __getitem__(key):
        """Get the value associated with the given key.

        Raise :class:`KeyError` if :meth:`~BTrees.Interfaces.IKeyed.has_key`
        is false with the given key.
        """

    def __setitem__(key, value):
        """Set the value associated with the given key."""

    def __delitem__(key):
        """Delete the value associated with the given key.

        Raise class:`KeyError` if :meth:`~BTrees.Interfaces.IKeyed.has_key` is
        false with the given key.
        """

    def values(min=None, max=None, excludemin=False, excludemax=False):
        """ Return a minimal sequence containing the values in the collection.

        Return value is an
        :mod:`IMinimalSequence
        <zope.interface.common.sequence.IMinimalSequence>`.

        The type of the ``IMinimalSequence`` is not specified. It
        could be a `list` or a `tuple` or some other type.

        All arguments are optional, and may be specified as keyword
        arguments, or by position.

        If a *min* is specified, then output is constrained to values
        whose keys are greater than or equal to the given *min*, and, if
        *excludemin* is specified and true, is further constrained to
        values whose keys are strictly greater than *min*. A *min* value
        of `None` is ignored. If *min* is `None` or not specified, and
        *excludemin* is true, the value corresponding to the smallest
        key is excluded.

        If a *max* is specified, then output is constrained to values
        whose keys are less than or equal to the given *max*, and, if
        *excludemax* is specified and true, is further constrained to
        values whose keys are strictly less than *max*. A *max* value of
        `None` is ignored. If *max* is `None` or not specified, and
        *excludemax* is true, the value corresponding to the largest key
        is excluded.
        """

    def items(min=None, max=None, excludemin=False, excludemax=False):
        """
        Return an ``IMinimalSequence`` containing the items in the
        collection.

        An item is a 2-tuple, a ``(key, value)`` pair.

        The type of the ``IMinimalSequence`` is not specified. It
        could be a `list` or a `tuple` or some other type.

        All arguments are optional, and may be specified as keyword
        arguments, or by position.

        If a *min* is specified, then output is constrained to items
        whose keys are greater than or equal to the given *min*, and,
        if *excludemin* is specified and true, is further constrained
        to items whose keys are strictly greater than *min*. A *min*
        value of `None` is ignored. If *min* is `None` or not
        specified, and *excludemin* is true, the item with the
        smallest key is excluded.

        If a *max* is specified, then output is constrained to items
        whose keys are less than or equal to the given *max*, and, if
        *excludemax is specified and true, is further constrained to
        items whose keys are strictly less than *max*. A *max* value
        of `None` is ignored. If *max* is `None` or not specified, and
        *excludemax* is true, the item with the largest key is
        excluded.
        """


class IDictionaryIsh(IMinimalDictionary):

    def update(collection):
        """Add the items from the given collection object to the collection.

        The input collection must be a sequence of (key, value) 2-tuples,
        or an object with an 'items' method that returns a sequence of
        (key, value) pairs.
        """

    def byValue(minValue):
        """Return a sequence of (value, key) pairs, sorted by value.

        Values < minValue are omitted and other values are "normalized" by
        the minimum value.  This normalization may be a noop, but, for
        integer values, the normalization is division.
        """

    def setdefault(key, d):
        """D.setdefault(k, d) -> D.get(k, d), also set D[k]=d if k not in D.

        Return the value like
        :meth:`~BTrees.Interfaces.IMinimalDictionary.get` except that if key
        is missing, d is both returned and inserted into the dictionary as the
        value of k.

        Note that, unlike as for Python's :meth:`dict.setdefault`, d is not
        optional.  Python defaults d to None, but that doesn't make sense
        for mappings that can't have None as a value (for example, an
        :class:`~BTrees.IIBTree.IIBTree` can have only integers as values).
        """

    def pop(key, d):
        """D.pop(k[, d]) -> v, remove key and return the corresponding value.

        If key is not found, d is returned if given, otherwise
        :class:`KeyError` is raised.
        """

    def popitem():
        """
        D.popitem() -> (k, v), remove and return some (key, value) pair
        as a 2-tuple; but raise KeyError if D is empty.

        .. versionadded:: 4.8.0
        """


class IBTree(IDictionaryIsh):

    def insert(key, value):
        """Insert a key and value into the collection.

        If the key was already in the collection, then there is no
        change and 0 is returned.

        If the key was not already in the collection, then the item is
        added and 1 is returned.

        This method is here to allow one to generate random keys and
        to insert and test whether the key was there in one operation.

        A standard idiom for generating new keys will be::

          key = generate_key()
          while not t.insert(key, value):
              key=generate_key()
        """

    def __and__(other):
        """Shortcut for :meth:`~BTrees.Interfaces.IMerge.intersection`"""

    def __or__(other):
        """Shortcut for :meth:`~BTrees.Interfaces.IMerge.union`"""

    def __sub__(other):
        """Shortcut for :meth:`~BTrees.Interfaces.IMerge.difference`"""


class IMerge(Interface):
    """Object with methods for merging sets, buckets, and trees.

    These methods are supplied in modules that define collection
    classes with particular key and value types. The operations apply
    only to collections from the same module.  For example, the
    :meth:`BTrees.IIBTree.IIBTree.union` can only be used with
    :class:`~BTrees.IIBTree.IIBTree`, :class:`~BTrees.IIBTree.IIBucket`,
    :class:`~BTrees.IIBTree.IISet`, and :class:`~BTrees.IIBTree.IITreeSet`.

    The number protocols methods ``__and__``, ``__or__`` and ``__sub__`` are
    provided by all the data structures. They are shortcuts for
    :meth:`~BTrees.Interfaces.IMerge.intersection`,
    :meth:`~BTrees.Interfaces.IMerge.union` and
    :meth:`~BTrees.Interfaces.IMerge.difference`.

    The implementing module has a value type. The
    :class:`~BTrees.IOBTree.IOBTree` and :class:`~BTrees.OOBTree.OOBTree`
    modules have object value type. The :class:`~BTrees.IIBTree.IIBTree` and
    :class:`~BTrees.OIBTree.OIBTree` modules have integer value types. Other
    modules may be defined in the future that have other value types.

    The individual types are classified into set (Set and TreeSet) and
    mapping (Bucket and BTree) types.
    """

    def difference(c1, c2):
        """Return the keys or items in c1 for which there is no key in c2.

        If c1 is None, then None is returned.  If c2 is None, then c1
        is returned.

        If neither c1 nor c2 is None, the output is a Set if c1 is a Set or
        TreeSet, and is a Bucket if c1 is a Bucket or BTree.

        While *c1* must be one of those types, *c2* can be any Python iterable
        returning the correct types of objects.

        .. versionchanged:: 4.8.0
           Add support for *c2* to be an arbitrary iterable.
        """

    def union(c1, c2):
        """Compute the Union of c1 and c2.

        If c1 is None, then c2 is returned, otherwise, if c2 is None,
        then c1 is returned.

        The output is a Set containing keys from the input
        collections.

        *c1* and *c2* can be any Python iterables returning the
        correct type of objects.

        .. versionchanged:: 4.8.0
           Add support for arbitrary iterables.
        """

    def intersection(c1, c2):
        """Compute the intersection of c1 and c2.

        If c1 is None, then c2 is returned, otherwise, if c2 is None,
        then c1 is returned.

        The output is a Set containing matching keys from the input
        collections.

        *c1* and *c2* can be any Python iterables returning the
        correct type of objects.

        .. versionchanged:: 4.8.0
           Add support for arbitrary iterables.
        """


class IBTreeModule(Interface):
    """These are available in all modules (IOBTree, OIBTree, OOBTree, IIBTree,
    IFBTree, LFBTree, LOBTree, OLBTree, and LLBTree).
    """

    BTree = Attribute(
        """The IBTree for this module.

        Also available as [prefix]BTree, as in IOBTree.""")

    Bucket = Attribute(
        """The leaf-node data buckets used by the BTree.

        (IBucket is not currently defined in this file, but is essentially
        IDictionaryIsh, with the exception of __nonzero__, as of this
        writing.)

        Also available as [prefix]Bucket, as in IOBucket.""")

    TreeSet = Attribute(
        """The ITreeSet for this module.

        Also available as [prefix]TreeSet, as in IOTreeSet.""")

    Set = Attribute(
        """The ISet for this module: the leaf-node data buckets used by the
        TreeSet.

        Also available as [prefix]BTree, as in IOSet.""")


class IIMerge(IMerge):
    """Merge collections with integer value type.

    A primary intent is to support operations with no or integer
    values, which are used as "scores" to rate indiviual keys. That
    is, in this context, a BTree or Bucket is viewed as a set with
    scored keys, using integer scores.
    """

    def weightedUnion(c1, c2, weight1=1, weight2=1):
        """Compute the weighted union of c1 and c2.

        If c1 and c2 are None, the output is (0, None).

        If c1 is None and c2 is not None, the output is (weight2, c2).

        If c1 is not None and c2 is None, the output is (weight1, c1).

        Else, and hereafter, c1 is not None and c2 is not None.

        If c1 and c2 are both sets, the output is 1 and the (unweighted)
        union of the sets.

        Else the output is 1 and a Bucket whose keys are the union of c1 and
        c2's keys, and whose values are::

          v1*weight1 + v2*weight2

          where:

            v1 is 0        if the key is not in c1
                  1        if the key is in c1 and c1 is a set
                  c1[key]  if the key is in c1 and c1 is a mapping

            v2 is 0        if the key is not in c2
                  1        if the key is in c2 and c2 is a set
                  c2[key]  if the key is in c2 and c2 is a mapping

        Note that c1 and c2 must be collections.
        """

    def weightedIntersection(c1, c2, weight1=1, weight2=1):
        """Compute the weighted intersection of c1 and c2.

        If c1 and c2 are None, the output is (0, None).

        If c1 is None and c2 is not None, the output is (weight2, c2).

        If c1 is not None and c2 is None, the output is (weight1, c1).

        Else, and hereafter, c1 is not None and c2 is not None.

        If c1 and c2 are both sets, the output is the sum of the weights
        and the (unweighted) intersection of the sets.

        Else the output is 1 and a Bucket whose keys are the intersection of
        c1 and c2's keys, and whose values are::

          v1*weight1 + v2*weight2

          where:

            v1 is 1        if c1 is a set
                  c1[key]  if c1 is a mapping

            v2 is 1        if c2 is a set
                  c2[key]  if c2 is a mapping

        Note that c1 and c2 must be collections.
        """


class IMergeIntegerKey(IMerge):
    """:class:`~BTrees.Interfaces.IMerge`-able objects with integer keys.

    Concretely, this means the types in :class:`~BTree.IOBTree.IOBTree` and
    :class:`~BTrees.IIBTree.IIBTree`.
    """

    def multiunion(seq):
        """Return union of (zero or more) integer sets, as an integer set.

        seq is a sequence of objects each convertible to an integer set.
        These objects are convertible to an integer set:

        + An integer, which is added to the union.

        + A Set or TreeSet from the same module (for example, an
          :class:`BTrees.IIBTree.TreeSet` for
          :meth:`BTrees.IIBTree.multiunion`).  The elements of the set are
          added to the union.

        + A Bucket or BTree from the same module (for example, an
          :class:`BTrees.IOBTree.IOBTree` for
          :meth:`BTrees.IOBTree.multiunion`).  The keys of the mapping are
          added to the union.

        + Any iterable Python object that iterates across integers. This
          will be slower than the above types.

        The union is returned as a Set from the same module (for example,
        :meth:`BTrees.IIBTree.multiunion` returns an
        :class:`BTrees.IIBTree.IISet`).

        The point to this method is that it can run much faster than doing a
        sequence of two-input :meth:`~BTrees.Interfaces.IMerge.union` calls.
        Under the covers, all the integers in all the inputs are sorted via a
        single linear-time radix sort, then duplicates are removed in a second
        linear-time pass.

        .. versionchanged:: 4.8.0
           Add support for arbitrary iterables of integers.
        """


class IBTreeFamily(Interface):
    """the 64-bit or 32-bit family"""
    IF = Attribute('The IIntegerFloatBTreeModule for this family')
    II = Attribute('The IIntegerIntegerBTreeModule for this family')
    IO = Attribute('The IIntegerObjectBTreeModule for this family')
    IU = Attribute('The IIntegerUnsignedBTreeModule for this family')

    UF = Attribute('The IUnsignedFloatBTreeModule for this family')
    UI = Attribute('The IUnsignedIntegerBTreeModule for this family')
    UO = Attribute('The IUnsignedObjectBTreeModule for this family')
    UU = Attribute('The IUnsignedUnsignedBTreeModule for this family')

    OI = Attribute('The IObjectIntegerBTreeModule for this family')
    OO = Attribute('The IObjectObjectBTreeModule for this family')
    OU = Attribute('The IObjectUnsignedBTreeModule for this family')

    maxint = Attribute('The maximum signed integer storable in this family')
    maxuint = Attribute('The maximum unsigned integer storable in this family')
    minint = Attribute('The minimum signed integer storable in this family')


class _IMergeBTreeModule(IBTreeModule, IMerge):
    family = Attribute('The IBTreeFamily of this module')


class IIntegerObjectBTreeModule(_IMergeBTreeModule):
    """Keys, or set values, are signed ints; values are objects.

    Describes IOBTree and LOBTree.
    """


class IUnsignedObjectBTreeModule(_IMergeBTreeModule):
    """Keys, or set values, are unsigned ints; values are objects.

    Describes UOBTree and QOBTree.
    """


class IObjectIntegerBTreeModule(_IMergeBTreeModule):
    """Keys, or set values, are objects; values are signed ints.

    Object keys (and set values) must sort reliably (for instance, *not* on
    object id)!  Homogenous key types recommended.

    Describes OIBTree and OLBTree.
    """


class IObjectUnsignedBTreeModule(_IMergeBTreeModule):
    """Keys, or set values, are objects; values are signed ints.

    Object keys (and set values) must sort reliably (for instance, *not* on
    object id)!  Homogenous key types recommended.

    Describes OUBTree and OQBTree.
    """


class IIntegerIntegerBTreeModule(_IMergeBTreeModule, IMergeIntegerKey):
    """Keys, or set values, are signed integers; values are signed integers.

    Describes IIBTree and LLBTree
    """


class IUnsignedUnsignedBTreeModule(_IMergeBTreeModule, IMergeIntegerKey):
    """Keys, or set values, are unsigned ints; values are unsigned ints.

    Describes UUBTree and QQBTree
    """


class IUnsignedIntegerBTreeModule(_IMergeBTreeModule, IMergeIntegerKey):
    """Keys, or set values, are unsigned ints; values are signed ints.

    Describes UIBTree and QLBTree
    """


class IIntegerUnsignedBTreeModule(_IMergeBTreeModule, IMergeIntegerKey):
    """Keys, or set values, are signed ints; values are unsigned ints.

    Describes IUBTree and LQBTree
    """


class IObjectObjectBTreeModule(IBTreeModule, IMerge):
    """Keys, or set values, are objects; values are also objects.

    Object keys (and set values) must sort reliably (for instance, *not* on
    object id)!  Homogenous key types recommended.

    Note that there's no ``family`` attribute; all families include
    the OO flavor of BTrees.

    Describes OOBTree
    """


class IIntegerFloatBTreeModule(_IMergeBTreeModule):
    """Keys, or set values, are signed ints; values are floats.

    Describes IFBTree and LFBTree
    """


class IUnsignedFloatBTreeModule(_IMergeBTreeModule):
    """Keys, or set values, are unsigned ints; values are floats.

    Describes UFBTree and QFBTree
    """


try:
    from ZODB.POSException import BTreesConflictError
except ImportError:
    class BTreesConflictError(ValueError):
        @property
        def reason(self):
            return self.args[-1]

###############################################################
# IMPORTANT NOTE
#
# Getting the length of a BTree, TreeSet, or output of keys,
# values, or items of same is expensive. If you need to get the
# length, you need to maintain this separately.
#
# Eventually, I need to express this through the interfaces.
#
################################################################
