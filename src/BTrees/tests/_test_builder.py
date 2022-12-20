##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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

import unittest

from .common import BTreeTests
from .common import ExtendedSetTests
from .common import I_SetsBase
from .common import InternalKeysMappingTest
from .common import MappingBase
from .common import MappingConflictTestBase
from .common import ModuleTest
from .common import MultiUnion
from .common import NormalSetTests
from .common import SetConflictTestBase
from .common import SetResult
from .common import Weighted
from .common import itemsToSet
from .common import makeMapBuilder
from .common import makeSetBuilder
from .common import TestLongIntKeys
from .common import TestLongIntValues


class _FilteredModuleProxy:
    """
    Accesses either ``<name>`` or ``<name>Py`` from a module.

    This conveniently lets us avoid lots of 'getattr' calls.

    Accessing ``def_<name>`` returns a callable that
    returns ``<name>``. This is suitable for use as class attributes.
    """
    # Lets us easily access by name a particular attribute
    # in either the Python or C implementation, based on the
    # suffix

    def __init__(self, btree_module, suffix):
        self.btree_module = btree_module
        self.suffix = suffix

    def __getattr__(self, name):
        attr_name = name[4:] if name.startswith('def_') else name
        attr_name += self.suffix
        attr = getattr(self.btree_module, attr_name)
        if name.startswith('def_'):
            return staticmethod(lambda: attr)
        return attr


def _flattened(*args):
    def f(tuple_or_klass):
        if isinstance(tuple_or_klass, tuple):
            for x in tuple_or_klass:
                yield from f(x)
        else:
            yield tuple_or_klass

    return tuple(f(args))

class ClassBuilder:

    # Use TestAuto as a prefix to avoid clashing with manual tests
    TESTCASE_PREFIX = 'TestAuto'

    def __init__(self, btree_module, btree_tests_base=BTreeTests):
        self.btree_module = btree_module
        # These will be instances of _datatypes.DataType
        self.key_type = btree_module.BTreePy._to_key
        self.value_type = btree_module.BTreePy._to_value

        class _BoundsMixin:
            # For test purposes, we can only support negative keys if they are ordered like
            # integers. Our int -> 2 byte conversion for fsBTree doesn't do this.
            # -1 is \xff\xff which is the largest possible key.
            SUPPORTS_NEGATIVE_KEYS = (
                self.key_type.get_lower_bound() != 0
                and self.key_type.coerce(-1) < self.key_type.coerce(0)
            )
            SUPPORTS_NEGATIVE_VALUES = self.value_type.get_lower_bound() != 0
            if SUPPORTS_NEGATIVE_KEYS:
                KEY_RANDRANGE_ARGS = (-2000, 2001)
            else:
                KEY_RANDRANGE_ARGS = (0, 4002)

            coerce_to_key = self.key_type.coerce
            coerce_to_value = self.value_type.coerce
            KEYS = tuple(self.key_type.coerce(x) for x in range(2001))
            VALUES = tuple(self.value_type.coerce(x) for x in range(2001))

        self.bounds_mixin = _BoundsMixin


        self.btree_tests_base = btree_tests_base

        self.prefix = btree_module.__name__.split('.', )[-1][:2]
        self.test_module = 'BTrees.tests.test_' + self.prefix + 'BTree'

        self.test_classes = {}
        # Keep track of tested classes so that we don't
        # double test in PURE_PYTHON mode (e.g., BTreePy is BTree)
        self.tested_classes = set()

    def _store_class(self, test_cls):
        assert test_cls.__name__ not in self.test_classes, (test_cls, self.test_classes)
        assert isinstance(test_cls, type)
        assert issubclass(test_cls, unittest.TestCase)
        self.test_classes[test_cls.__name__] = test_cls

    def _fixup_and_store_class(self, btree_module, fut, test_cls):
        base = [x for x in test_cls.__bases__
                if x.__module__ != __name__ and x.__module__ != 'unittest'][0]

        test_name = self._name_for_test(btree_module, fut, base)
        test_cls.__name__ = test_name
        test_cls.__module__ = self.test_module
        test_cls.__qualname__ = self.test_module + '.' + test_name
        self._store_class(test_cls)

    def _name_for_test(self, btree_module, fut, test_base):
        fut = getattr(fut, '__name__', fut)
        fut = str(fut)
        if isinstance(test_base, tuple):
            test_base = test_base[0]
        test_name = (
            self.TESTCASE_PREFIX
            + (self.prefix if not fut.startswith(self.prefix) else '')
            + fut
            + test_base.__name__
            + btree_module.suffix
        )
        return test_name

    def _needs_test(self, fut, test_base):
        key = (fut, test_base)
        if key in self.tested_classes:
            return False
        self.tested_classes.add(key)
        return True

    def _create_set_op_test(self, btree_module, base):
        tree = btree_module.BTree
        if not self._needs_test(tree, base):
            return

        class Test(self.bounds_mixin, base, unittest.TestCase):
            # There are two set operation tests,
            # Weighted and MultiUnion.

            # These attributes are used in both
            mkbucket = btree_module.Bucket
            # Weighted uses union as a factory, self.union()(...).
            # MultiUnion calls it directly.
            __union = btree_module.def_union

            def union(self, *args):
                if args:
                    return self.__union()(*args)
                return self.__union()

            intersection = btree_module.def_intersection
            # These are specific to Weighted; modules that
            # don't have weighted values can'd do them.
            if base is Weighted:
                weightedUnion = btree_module.def_weightedUnion
                weightedIntersection = btree_module.def_weightedIntersection


            # These are specific to MultiUnion, and may not exist
            # in key types that don't support unions (``'O'``)
            multiunion = getattr(btree_module, 'multiunion', None)
            mkset = btree_module.Set
            mktreeset = btree_module.TreeSet
            mkbtree = tree

            def builders(self):
                return (
                    btree_module.Bucket,
                    btree_module.BTree,
                    itemsToSet(btree_module.Set),
                    itemsToSet(btree_module.TreeSet)
                )

        self._fixup_and_store_class(btree_module, '', Test)

    def _create_set_result_test(self, btree_module):
        tree = btree_module.BTree
        base = SetResult
        if not self._needs_test(tree, base):
            return

        class Test(self.bounds_mixin, base, unittest.TestCase):
            union = btree_module.union
            intersection = btree_module.intersection
            difference = btree_module.difference

            def builders(self):
                return (
                    makeSetBuilder(self, btree_module.Set),
                    makeSetBuilder(self, btree_module.TreeSet),
                    makeMapBuilder(self, btree_module.BTree),
                    makeMapBuilder(self, btree_module.Bucket)
                )

        self._fixup_and_store_class(btree_module, '', Test)

    def _create_module_test(self):
        from BTrees import Interfaces as interfaces
        mod = self.btree_module
        iface = getattr(interfaces, 'I' + self.key_type.long_name + self.value_type.long_name
                        + 'BTreeModule')
        class Test(ModuleTest, unittest.TestCase):
            prefix = self.prefix
            key_type = self.key_type
            value_type = self.value_type

            _getModule = lambda self: mod
            _getInterface = lambda self: iface

        self._fixup_and_store_class(_FilteredModuleProxy(self.btree_module, ''), '', Test)

    def _create_type_tests(self, btree_module, type_name, test_bases):
        from BTrees import Interfaces as interfaces
        tree = getattr(btree_module, type_name)
        iface = {
            'BTree': interfaces.IBTree,
            'Bucket': interfaces.IMinimalDictionary,
            'Set': interfaces.ISet,
            'TreeSet': interfaces.ITreeSet
        }[type_name]

        for test_base in test_bases:
            if not self._needs_test(tree, test_base):
                continue

            test_name = self._name_for_test(btree_module, tree, test_base)
            bases = _flattened(self.bounds_mixin, test_base, unittest.TestCase)
            test_cls = type(test_name, bases, {
                '__module__': self.test_module,
                '_getTargetClass': lambda _, t=tree: t,
                '_getTargetInterface': lambda _, i=iface: i,
                'getTwoKeys': self.key_type.getTwoExamples,
                'getTwoValues': self.value_type.getTwoExamples,
                'key_type': self.key_type,
                'value_type': self.value_type,
            })
            self._store_class(test_cls)

    def create_classes(self):
        self._create_module_test()

        btree_tests_base = (self.btree_tests_base,)
        if self.key_type.using64bits:
            btree_tests_base += (TestLongIntKeys,)
        if self.value_type.using64bits:
            btree_tests_base += (TestLongIntValues,)

        set_ops = ()
        if self.key_type.supports_value_union():
            set_ops += (MultiUnion,)
        if self.value_type.supports_value_union():
            set_ops += (Weighted,)

        for suffix in ('', 'Py'):
            btree_module = _FilteredModuleProxy(self.btree_module, suffix)

            for type_name, test_bases in (
                    ('BTree', (InternalKeysMappingTest,
                               MappingConflictTestBase,
                               btree_tests_base)),
                    ('Bucket', (MappingBase,
                                MappingConflictTestBase,)),
                    ('Set', (ExtendedSetTests,
                             I_SetsBase,
                             SetConflictTestBase,)),
                    ('TreeSet', (I_SetsBase,
                                 NormalSetTests,
                                 SetConflictTestBase,))
            ):
                self._create_type_tests(btree_module, type_name, test_bases)


            for test_base in set_ops:
                self._create_set_op_test(btree_module, test_base)

            self._create_set_result_test(btree_module)


def update_module(test_module_globals, btree_module, *args, **kwargs):
    builder = ClassBuilder(btree_module, *args, **kwargs)
    builder.create_classes()
    test_module_globals.update(builder.test_classes)
