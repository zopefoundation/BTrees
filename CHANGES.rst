``BTrees`` Changelog
====================

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
  `issue 106 <https://github.com/zopefoundation/BTrees/issue/106>`_.


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

- Added ``setup_requires==['persistent']``.


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
################

- Dropped support for Python < 2.6.

- Factored ``BTrees`` as a separate distribution.

Testing Changes
###############

- All covered platforms tested under ``tox``.

- Added support for continuous integration using ``tox`` and ``jenkins``.

- Added ``setup.py dev`` alias (installs ``nose`` and ``coverage``).

- Dropped dependency on ``zope.testing`` / ``zope.testrunner``:  tests now
  run with ``setup.py test``.

Documentation Changes
#####################

- Added API reference, generated via Spinx' autodoc.

- Added Sphinx documentation based on ZODB Guide (snippets are exercised
  via 'tox').

- Added ``setup.py docs`` alias (installs ``Sphinx`` and
  ``repoze.sphinx.autointerface``).
