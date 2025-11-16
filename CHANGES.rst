Change log
==========

6.3 (2025-11-16)
----------------

- Move all supported package metadata into ``pyproject.toml``.


6.2 (2025-10-28)
----------------

- Drop support for Python 3.8, 3.9.

- Add support for Python 3.14.


6.1 (2024-09-17)
----------------

- Add final support for Python 3.13.


6.0 (2024-05-30)
----------------

- Drop support for Python 3.7.

- Build Windows wheels on GHA.


5.2 (2024-02-07)
----------------

- Add preliminary support for Python 3.13 as of 3.13a3.


5.1 (2023-10-05)
----------------

- Drop using ``setup_requires`` due to constant problems on GHA.

- Add support for Python 3.12.


5.0 (2023-02-10)
----------------

- Build Linux binary wheels for Python 3.11.

- Drop support for Python 2.7, 3.5, 3.6.


4.11.3 (2022-11-17)
-------------------

- point release to rebuild full set of wheels


4.11.2 (2022-11-16)
-------------------

- Add support for building arm64 wheels on macOS.


4.11.1 (2022-11-09)
-------------------

- Fix macOS wheel build issues on GitHub Actions

- We no longer provide 32bit wheels for the Windows platform, only x86_64.


4.11.0 (2022-11-03)
-------------------

- Add support for Python 3.11.


4.10.1 (2022-09-12)
-------------------

- Disable unsafe math optimizations in C code.
  (`#184 <https://github.com/zopefoundation/BTrees/pull/184>`_)


4.10.0 (2022-03-09)
-------------------

- Add support for Python 3.10.


4.9.2 (2021-06-09)
------------------

- Fix ``fsBTree.TreeSet`` and ``fsBTree.BTree`` raising
  ``SystemError``. See `issue 170 <https://github.com/zopefoundation/BTrees/issues/170>`_.

- Fix all the ``fsBTree`` objects to provide the correct interfaces
  and be instances of the appropriate collection ABCs. This was done
  for the other modules in release 4.8.0.

- Fix the ``multiunion``, ``union``, ``intersection``, and
  ``difference`` functions when used with arbitrary iterables.
  Previously, the iterable had to be pre-sorted, meaning only
  sequences like ``list`` and ``tuple`` could reliably be used; this
  was not documented though. If the iterable wasn't sorted, the
  function would produce garbage output. Now, if the function detects
  an arbitrary iterable, it automatically sorts a copy.


4.9.1 (2021-05-27)
------------------

- Fix setting unknown class attributes on subclasses of BTrees when
  using the C extension. This prevented subclasses from being
  decorated with ``@component.adapter()``. See `issue 168
  <https://github.com/zopefoundation/BTrees/issues/168>`_.


4.9.0 (2021-05-26)
------------------

- Fix the C implementation to match the Python implementation and
  allow setting custom node sizes for an entire application directly
  by changing ``BTree.max_leaf_size`` and ``BTree.max_internal_size``
  attributes, without having to create a new subclass. These
  attributes can now also be read from the classes in the C
  implementation. See `issue 166
  <https://github.com/zopefoundation/BTrees/issues/166>`_.

- Add various small performance improvements for storing
  zope.interface attributes on ``BTree`` and ``TreeSet`` as well as
  deactivating persistent objects from this package.


4.8.0 (2021-04-14)
------------------

- Make Python 2 forbid the use of type objects as keys (unless a
  custom metaclass is used that implements comparison as required by
  BTrees.) On Python 3, types are not orderable so they were already
  forbidden, but on Python 2 types can be ordered by memory address,
  which makes them unsuitable for use as keys. See `issue
  <https://github.com/zopefoundation/BTrees/issues/153>`_.

- Make the ``multiunion``, ``union``, ``intersection``, and
  ``difference`` functions accept arbitrary Python iterables (that
  iterate across the correct types). Previously, the Python
  implementation allowed this, but the C implementation only allowed
  objects (like ``TreeSet`` or ``Bucket``) defined in the same module
  providing the function. See `issue 24
  <https://github.com/zopefoundation/BTrees/issues/24>`_.

- Fix persistency bug in the Python version
  (`#118 <https://github.com/zopefoundation/BTrees/issues/118>`_).

- Fix ``Tree.__setstate__`` to no longer accept children besides
  tree or bucket types to prevent crashes. See `PR 143
  <https://github.com/zopefoundation/BTrees/pull/143>`_ for details.

- Make BTrees, TreeSet, Set and Buckets implements the ``__and__``,
  ``__or__`` and ``__sub__`` special methods as shortcuts for
  ``BTrees.Interfaces.IMerge.intersection``,
  ``BTrees.Interfaces.IMerge.union`` and
  ``BTrees.Interfaces.IMerge.difference``.

- Add support for Python 3.9.

- Build and upload aarch64 wheels.

- Make a value of ``0`` in the ``PURE_PYTHON`` environment variable
  require the C extensions (except on PyPy). Previously, and if this
  variable is unset, missing or unusable C extensions would be
  silently ignored. With this variable set to ``0``, an
  ``ImportError`` will be raised if the C extensions are unavailable.
  See `issue 156
  <https://github.com/zopefoundation/BTrees/issues/156>`_.

- Make the BTree objects (``BTree``, ``TreeSet``, ``Set``, ``Bucket``)
  of each module actually provide the interfaces defined in
  ``BTrees.Interfaces``. Previously, they provided no interfaces.

- Make all the BTree and Bucket objects instances of
  ``collections.abc.MutableMapping`` (that is, ``isinstance(btree,
  MutableMapping)`` is now true; no actual inheritance has changed).
  As part of this, they now provide the ``popitem()`` method.

- Make all the TreeSet and Set objects instances of
  ``collections.abc.MutableSet`` (that is, ``isinstance(tree_set,
  MutableSet)`` is now true; no actual inheritance has changed).
  As part of this, they now provide several more methods, including
  ``isdisjoint``, ``discard``, and ``pop``, and support in-place
  mutation operators such as ``tree_set |= other``, ``tree_set +=
  other``, ``tree_set -= other`` and ``tree_set ^= other``. See `issue
  121 <https://github.com/zopefoundation/BTrees/issues/121>`_.

- Update the definitions of ``ISized`` and ``IReadSequence`` to simply
  be ``zope.interface.common.collections.ISized`` and
  ``zope.interface.common.sequence.IMinimalSequence`` respectively.

- Remove the ``__nonzero__`` interface method from ``ICollection``. No
  objects actually implemented such a method; instead, the boolean value
  is typically taken from ``__len__``.

- Adjust the definition of ``ISet`` to produce the same resolution
  order under the C3 and legacy orderings. This means that the legacy
  order has changed slightly, but that this package emits no warnings
  when ``ZOPE_INTERFACE_LOG_CHANGED_IRO=1``. Note that the legacy
  order was not being used for these objects because the C3 ordering
  was still consistent; it could only be obtained using
  ``ZOPE_INTERFACE_USE_LEGACY_IRO=1``. See `PR 159
  <https://github.com/zopefoundation/BTrees/pull/159>`_ for all the
  interface updates.

- Fix the ``get``, ``setdefault`` and ``pop`` methods, as well as the
  ``in`` operator, to not suppress ``POSKeyError`` if the object or
  subobjects are corrupted. Previously, such errors were logged by
  ZODB, but not propagated. See `issue 161
  <https://github.com/zopefoundation/BTrees/issues/161>`_.


4.7.2 (2020-04-07)
------------------

- Fix more cases of C and Python inconsistency. The C implementation
  now behaves like the Python implementation when it comes to integer
  overflow for the integer keys for ``in``, ``get`` and ``has_key``.
  Now they return False, the default value, and False, respectively in
  both versions if the tested value would overflow or underflow.
  Previously, the C implementation would raise ``OverflowError`` or
  ``KeyError``, while the Python implementation functioned as
  expected. See `issue 140
  <https://github.com/zopefoundation/BTrees/issues/140>`_.

  .. note::
     The unspecified true return values of ``has_key``
     have changed.


4.7.1 (2020-03-22)
------------------

- Fix the definitions of ``__all__`` in modules. In 4.7.0, they
  incorrectly left out names. See `PR 132
  <https://github.com/zopefoundation/BTrees/pull/132>`_.

- Ensure the interface resolution order of all objects is consistent.
  See `issue 137 <https://github.com/zopefoundation/BTrees/issues/137>`_.


4.7.0 (2020-03-17)
------------------

- Add unsigned variants of the trees. These use the initial "U" for
  32-bit data and "Q" for 64-bit data (for "quad", which is similar to
  what the C ``printf`` function uses and the Python struct module
  uses).

- Fix the value for ``BTrees.OIBTree.using64bits`` when using the pure Python
  implementation (PyPy and when ``PURE_PYTHON`` is in the environment).

- Make the errors that are raised when values are out of range more
  consistent between Python 2 and Python 3 and between 32-bit and
  64-bit variants.

- Make the Bucket types consistent with the BTree types as updated in
  versions 4.3.2: Querying for keys with default comparisons or that
  are not integers no longer raises ``TypeError``.


4.6.1 (2019-11-07)
------------------

- Add support for Python 3.8.


4.6.0 (2019-07-30)
------------------

- Drop support for Python 3.4.

- Fix tests against persistent 4.4.

- Stop accidentally installing the 'terryfy' package in macOS wheels.
  See `issue 98
  <https://github.com/zopefoundation/BTrees/issues/98>`_.

- Fix segmentation fault in ``bucket_repr()``.  See
  `issue 106 <https://github.com/zopefoundation/BTrees/issues/106>`_.


4.5.1 (2018-08-09)
------------------

- Produce binary wheels for Python 3.7.

- Use pyproject.toml to specify build dependencies. This requires pip
  18 or later to build from source.


4.5.0 (2018-04-23)
------------------

- Add support for Python 3.6 and 3.7.
- Drop support for Python 3.3.
- Raise an ``ImportError`` consistently on Python 3 if the C extension for
  BTrees is used but the ``persistent`` C extension is not available.
  Previously this could result in an odd ``AttributeError``. See
  https://github.com/zopefoundation/BTrees/pull/55
- Fix the possibility of a rare crash in the C extension when
  deallocating items. See https://github.com/zopefoundation/BTrees/issues/75
- Respect the ``PURE_PYTHON`` environment variable at runtime even if
  the C extensions are available. See
  https://github.com/zopefoundation/BTrees/issues/78
- Always attempt to build the C extensions, but make their success
  optional.
- Fix a ``DeprecationWarning`` that could come from I and L objects in
  Python 2 in pure-Python mode. See https://github.com/zopefoundation/BTrees/issues/79


4.4.1 (2017-01-24)
------------------

Fixed a packaging bug that caused extra files to be included (some of
which caused problems in some platforms).


4.4.0 (2017-01-11)
------------------

- Allow None as a special key (sorted smaller than all others).

  This is a bit of a return to BTrees 3 behavior in that Nones are
  allowed as keys again.  Other objects with default ordering are
  still not allowed as keys.


4.3.2 (2017-01-05)
------------------

- Make the CPython implementation consistent with the pure-Python
  implementation and only check object keys for default comparison
  when setting keys. In Python 2 this makes it possible to remove keys
  that were added using a less restrictive version of BTrees. (In
  Python 3 keys that are unorderable still cannot be removed.)
  Likewise, all versions can unpickle trees that already had such
  keys. See: https://github.com/zopefoundation/BTrees/issues/53 and
  https://github.com/zopefoundation/BTrees/issues/51

- Make the Python implementation consistent with the CPython
  implementation and check object key identity before checking
  equality and performing comparisons. This can allow fixing trees
  that have keys that now have broken comparison functions. See
  https://github.com/zopefoundation/BTrees/issues/50

- Make the CPython implementation consistent with the pure-Python
  implementation and no longer raise ``TypeError`` for an object key
  (in object-keyed trees) with default comparison on ``__getitem__``,
  ``get`` or ``in`` operations. Instead, the results will be a
  ``KeyError``, the default value, and ``False``, respectively.
  Previously, CPython raised a ``TypeError`` in those cases, while the
  Python implementation behaved as specified.

  Likewise, non-integer keys in integer-keyed trees
  will raise ``KeyError``, return the default and return ``False``,
  respectively, in both implementations. Previously, pure-Python
  raised a ``KeyError``, returned the default, and raised a
  ``TypeError``, while CPython raised ``TypeError`` in all three cases.


4.3.1 (2016-05-16)
------------------

- Packaging:  fix password used to automate wheel creation on Travis.


4.3.0 (2016-05-10)
------------------

- Fix unexpected ``OverflowError`` when passing 64bit values to long
  keys / values on Win64.  See:
  https://github.com/zopefoundation/BTrees/issues/32

- When testing ``PURE_PYTHON`` environments under ``tox``, avoid poisoning
  the user's global wheel cache.

- Ensure that the pure-Python implementation, used on PyPy and when a C
  compiler isn't available for CPython, pickles identically to the C
  version. Unpickling will choose the best available implementation.
  This change prevents interoperability problems and database corruption if
  both implementations are in use. While it is no longer possible to
  pickle a Python implementation and have it unpickle to the Python
  implementation if the C implementation is available, existing Python
  pickles will still unpickle to the Python implementation (until
  pickled again). See:
  https://github.com/zopefoundation/BTrees/issues/19

- Avoid creating invalid objects when unpickling empty BTrees in a pure-Python
  environment.

- Drop support for Python 2.6 and 3.2.


4.2.0 (2015-11-13)
------------------

- Add support for Python 3.5.


4.1.4 (2015-06-02)
------------------

- Ensure that pure-Python Bucket and Set objects have a human readable
  ``__repr__`` like the C versions.


4.1.3 (2015-05-19)
------------------

- Fix ``_p_changed`` when removing items from small pure-Python
  BTrees/TreeSets and when adding items to small pure-Python Sets. See:
  https://github.com/zopefoundation/BTrees/issues/13


4.1.2 (2015-04-07)
------------------

- Suppress testing 64-bit values in OLBTrees on 32 bit machines.
  See:  https://github.com/zopefoundation/BTrees/issues/9

- Fix ``_p_changed`` when adding items to small pure-Python
  BTrees/TreeSets. See:
  https://github.com/zopefoundation/BTrees/issues/11


4.1.1 (2014-12-27)
------------------

- Accomodate long values in pure-Python OLBTrees.


4.1.0 (2014-12-26)
------------------

- Add support for PyPy and PyPy3.

- Add support for Python 3.4.

- BTree subclasses can define ``max_leaf_size`` or ``max_internal_size``
  to control maximum sizes for Bucket/Set and BTree/TreeSet nodes.

- Detect integer overflow on 32-bit machines correctly under Python 3.

- Update pure-Python and C trees / sets to accept explicit None to indicate
  max / min value for ``minKey``, ``maxKey``.  (PR #3)

- Update pure-Python trees / sets to accept explicit None to indicate
  open ranges for ``keys``, ``values``, ``items``.  (PR #3)


4.0.8 (2013-05-25)
------------------

- Fix value-based comparison for objects under Py3k:  addresses invalid
  merges of ``[OLI]OBTrees/OBuckets``.

- Ensure that pure-Python implementation of ``OOBTree.byValue`` matches
  semantics (reversed-sort) of C implementation.


4.0.7 (2013-05-22)
------------------

- Issue #2:  compilation error on 32-bit mode of OS/X.

- Test ``PURE_PYTHON`` environment variable support:  if set, the C
  extensions will not be built, imported, or tested.


4.0.6 (2013-05-14)
------------------

- Changed the ``ZODB`` extra to require only the real ``ZODB`` package,
  rather than the ``ZODB3`` metapackage:  depending on the version used,
  the metapackage could pull in stale versions of **this** package and
  ``persistent``.

- Fixed Python version check in ``setup.py``.


4.0.5 (2013-01-15)
------------------

- Fit the ``repr`` of bucket objects, which could contain garbage
  characters.


4.0.4 (2013-01-12)
------------------

- Emulate the (private) iterators used by the C extension modules from
  pure Python.  This change is "cosmetic" only:  it prevents the ZCML
  ``zope.app.security:permission.zcml`` from failing.  The emulated
  classes are **not** functional, and should be considered implementation
  details.

- Accomodate buildout to the fact that we no longer bundle a copy
  of 'persistent.h'.

- Fix test failures on Windows:  no longer rely on overflows from
  ``sys.maxint``.


4.0.3 (2013-01-04)
------------------

- Added ``setup_requires--['persistent']``.


4.0.2 (2013-01-03)
------------------

- Updated Trove classifiers.

- Added explicit support for Python 3.2, Python 3.3, and PyPy.
  Note that the C extensions are not (yet) available on PyPy.

- Python reference implementations now tested separately from the C
  verions on all platforms.

- 100% unit test coverage.


4.0.1 (2012-10-21)
------------------

- Provide local fallback for persistent C header inclusion if the
  persistent distribution isn't installed. This makes the winbot happy.


4.0.0 (2012-10-20)
------------------

Platform Changes
----------------

- Dropped support for Python < 2.6.

- Factored ``BTrees`` as a separate distribution.

Testing Changes
---------------

- All covered platforms tested under ``tox``.

- Added support for continuous integration using ``tox`` and ``jenkins``.

- Added ``setup.py dev`` alias (installs ``nose`` and ``coverage``).

- Dropped dependency on ``zope.testing`` / ``zope.testrunner``:  tests now
  run with ``setup.py test``.

Documentation Changes
---------------------

- Added API reference, generated via Spinx' autodoc.

- Added Sphinx documentation based on ZODB Guide (snippets are exercised
  via 'tox').

- Added ``setup.py docs`` alias (installs ``Sphinx`` and
  ``repoze.sphinx.autointerface``).
