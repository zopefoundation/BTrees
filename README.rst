``BTrees``:  scalable persistent components
===========================================

.. image:: https://travis-ci.org/zopefoundation/BTrees.svg?branch=master
    :target: https://travis-ci.org/zopefoundation/BTrees

.. image:: https://ci.appveyor.com/api/projects/status/github/zopefoundation/BTrees?branch=master&svg=true
    :target: https://ci.appveyor.com/project/mgedmin/BTrees

This package contains a set of persistent object containers built around
a modified BTree data structure.  The trees are optimized for use inside
ZODB's "optimistic concurrency" paradigm, and include explicit resolution
of conflicts detected by that mechannism.

Please see the Sphinx documentation (``docs/index.rst``) for further
information.
