``BTrees`` Changelog
====================


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
