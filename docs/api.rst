===============
 API Reference
===============


Protocol APIs
=============

.. module:: BTrees.Interfaces

.. autointerface:: ICollection
.. autointerface:: IReadSequence
.. autointerface:: IKeyed
.. autointerface:: ISetMutable
.. autointerface:: ISized
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
