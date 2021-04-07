===============
 API Reference
===============


Protocol APIs
=============

.. module:: BTrees.Interfaces

.. versionchanged:: 4.8.0
   Previously, ``ISized`` was defined here, but now it is
   imported from :mod:`zope.interface.common.collections`. The
   definition is the same.

   Similarly, ``IReadSequence``, previously defined here,
   has been replaced with
   :mod:`zope.interface.common.sequence.IMinimalSequence <zope.interface.common.sequence>`.

.. caution::

   Before version 4.8.0, most of these interfaces served as
   documentation only, and were *not* implemented by the classes of
   this package. For example, :class:`BTrees.OOBTree.BTree` did *not*
   implement `IBTree`. (The exceptions were the :class:`IBTreeModule`
   and :class:`IBTreeFamily` families of interfaces and
   implementations.)

   Beginning with version 4.8.0, objects implement the expected
   interface; the ``BTree`` classes implement ``IBTree``, the set
   classes implement the appropriate set interface and so on.


.. autointerface:: ICollection
.. autointerface:: IKeyed
.. autointerface:: ISetMutable
.. autointerface:: IKeySequence
.. autointerface:: IMinimalDictionary
.. autointerface:: IDictionaryIsh
.. autointerface:: IMerge
.. autointerface:: IIMerge
.. autointerface:: IMergeIntegerKey

BTree Family APIs
-----------------
.. autointerface:: ISet
.. autointerface:: ITreeSet
.. autointerface:: IBTree
.. autointerface:: IBTreeFamily

There are two families defined:

.. autodata:: BTrees.family32
.. autodata:: BTrees.family64

Module APIs
-----------
.. autointerface:: IBTreeModule
.. autointerface:: IObjectObjectBTreeModule
.. autointerface:: IIntegerObjectBTreeModule
.. autointerface:: IObjectIntegerBTreeModule
.. autointerface:: IIntegerIntegerBTreeModule
.. autointerface:: IIntegerFloatBTreeModule


Utilities
=========

.. automodule:: BTrees.Length

.. automodule:: BTrees.check


BTree Data Structure Variants
=============================

Integer Keys
------------

Float Values
~~~~~~~~~~~~
.. automodule:: BTrees.IFBTree

Integer Values
~~~~~~~~~~~~~~
.. automodule:: BTrees.IIBTree

Object Values
~~~~~~~~~~~~~
.. automodule:: BTrees.IOBTree

Unsigned Integer Values
~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: BTrees.IUBTree

Long Integer Keys
-----------------

Float Values
~~~~~~~~~~~~
.. automodule:: BTrees.LFBTree

Long Integer Values
~~~~~~~~~~~~~~~~~~~
.. automodule:: BTrees.LLBTree


Object Values
~~~~~~~~~~~~~
.. automodule:: BTrees.LOBTree

Quad Unsigned Integer Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: BTrees.LQBTree


Object Keys
-----------

Integer Values
~~~~~~~~~~~~~~
.. automodule:: BTrees.OIBTree

Long Integer Values
~~~~~~~~~~~~~~~~~~~
.. automodule:: BTrees.OLBTree

Object Values
~~~~~~~~~~~~~
.. automodule:: BTrees.OOBTree

Quad Unsigned Integer Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: BTrees.OQBTree

Unsigned Integer Values
~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: BTrees.OUBTree


Quad Unsigned Integer Keys
--------------------------

Float Values
~~~~~~~~~~~~
.. automodule:: BTrees.QFBTree

Long Integer Values
~~~~~~~~~~~~~~~~~~~
.. automodule:: BTrees.QLBTree

Object Values
~~~~~~~~~~~~~
.. automodule:: BTrees.QOBTree

Quad Unsigned Integer Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: BTrees.QQBTree

Unsigned Integer Keys
---------------------

Float Values
~~~~~~~~~~~~
.. automodule:: BTrees.UFBTree

Integer Values
~~~~~~~~~~~~~~
.. automodule:: BTrees.UIBTree

Object Values
~~~~~~~~~~~~~
.. automodule:: BTrees.UOBTree

Unsigned Integer Values
~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: BTrees.UUBTree
