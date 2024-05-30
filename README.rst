=============================================
 ``BTrees``:  scalable persistent components
=============================================

.. image:: https://github.com/zopefoundation/BTrees/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/zopefoundation/BTrees/actions/workflows/tests.yml

.. image:: https://coveralls.io/repos/github/zopefoundation/BTrees/badge.svg?branch=master
    :target: https://coveralls.io/github/zopefoundation/BTrees?branch=master

.. image:: https://readthedocs.org/projects/btrees/badge/?version=latest
        :target: https://btrees.readthedocs.io/en/latest/
        :alt: Documentation Status

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

Please see `the Sphinx documentation <https://btrees.readthedocs.io/>`_ for
further information.
