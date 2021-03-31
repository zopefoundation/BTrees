##############################################################################
#
# Copyright (c) 2020 Zope Foundation and Contributors.
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
"""
This module dynamically creates test modules and suites for
all expected BTree families that do not have their own test file on disk.
"""


import unittest
import importlib
import sys
import types

from BTrees import _FAMILIES

from ._test_builder import update_module

# If there is no .py file on disk, create the module in memory.
# This is helpful during early development. However, it
# doesn't work with zope-testrunner's ``-m`` filter.
_suite = unittest.TestSuite()
for family in _FAMILIES:
    mod_qname = "BTrees.tests.test_" + family + 'BTree'
    try:
        importlib.import_module(mod_qname)
    except ImportError:
        btree = importlib.import_module("BTrees." + family + 'BTree')
        mod = types.ModuleType(mod_qname)
        update_module(vars(mod), btree)
        sys.modules[mod_qname] = mod
        globals()[mod_qname.split('.', 1)[1]] = mod
        _suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(mod))

def test_suite():
    # zope.testrunner protocol
    return _suite

def load_tests(loader, standard_tests, pattern): # pylint:disable=unused-argument
    # Pure unittest protocol.
    return test_suite()
