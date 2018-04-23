``BTrees``:  scalable persistent components
===========================================

.. image:: https://travis-ci.org/zopefoundation/BTrees.svg?branch=master
    :target: https://travis-ci.org/zopefoundation/BTrees

.. image:: https://ci.appveyor.com/api/projects/status/github/zopefoundation/BTrees?branch=master&svg=true
    :target: https://ci.appveyor.com/project/mgedmin/BTrees

.. image:: https://coveralls.io/repos/github/zopefoundation/BTrees/badge.svg?branch=master
    :target: https://coveralls.io/github/zopefoundation/BTrees?branch=master

.. image:: https://img.shields.io/pypi/v/BTrees.svg
        :target: https://pypi.org/project/BTrees/
        :alt: Current version on PyPI

.. image:: https://img.shields.io/pypi/pyversions/BTrees.svg
        :target: https://pypi.org/project/BTrees/
        :alt: Supported Python versions


This package contains a set of persistent object containers built around
a modified BTree data structure.  The trees are optimized for use inside
ZODB's "optimistic concurrency" paradigm, and include explicit resolution
of conflicts detected by that mechanism.

Please see `the Sphinx documentation <http://btrees.readthedocs.io/>`_ for further
information.
