##############################################################################
#
# Copyright Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Support functions to eliminate the boilerplate involved in defining
BTree modules.
"""
import sys

from zope.interface import classImplements
from zope.interface import directlyProvides


def _create_classes(
        module_name, key_datatype, value_datatype,
):
    from ._base import MERGE  # Won't always want this.
    from ._base import Bucket
    from ._base import Set
    from ._base import Tree
    from ._base import TreeSet
    from ._base import _TreeItems as TreeItems
    from ._base import _TreeIterator

    classes = {}

    prefix = key_datatype.prefix_code + value_datatype.prefix_code

    classes['TreeItems'] = classes['TreeItemsPy'] = TreeItems
    for base in (
            Bucket,
            Set,
            (Tree, 'BTree'),
            TreeSet,
            (_TreeIterator, 'TreeIterator'),
    ):
        if isinstance(base, tuple):
            base, base_name = base
        else:
            base_name = base.__name__

        # XXX: Consider defining these with their natural names
        # now and only aliasing them to 'Py' instead of the
        # opposite. That should make pickling easier.
        name = prefix + base_name + 'Py'
        cls = type(name, (base,), dict(
            _to_key=key_datatype,
            _to_value=value_datatype,
            MERGE=MERGE,
            MERGE_WEIGHT=value_datatype.apply_weight,
            MERGE_DEFAULT=value_datatype.multiplication_identity,
            # max_leaf_size and max_internal_size are set
            # for BTree and TreeSet later, when we do the same thing
            # for C.
        ))
        cls.__module__ = module_name
        key_datatype.add_extra_methods(base_name, cls)

        classes[cls.__name__] = cls
        # Importing the C extension does this for the non-py
        # classes.
        # TODO: Unify that.
        classes[base_name + 'Py'] = cls

    for cls in classes.values():
        cls._mapping_type = classes['BucketPy']
        cls._set_type = classes['SetPy']

        if 'Set' in cls.__name__:
            cls._bucket_type = classes['SetPy']
        else:
            cls._bucket_type = classes['BucketPy']

    return classes


def _create_set_operations(module_name, key_type, value_type, set_type):
    from ._base import difference
    from ._base import intersection
    from ._base import multiunion
    from ._base import set_operation
    from ._base import union
    from ._base import weightedIntersection
    from ._base import weightedUnion

    ops = {
        op.__name__ + 'Py': set_operation(op, set_type)
        for op in (
            difference, intersection,
            union,
        ) + (
            (weightedIntersection, weightedUnion,)
            if value_type.supports_value_union()
            else ()
        ) + (
            (multiunion,)
            if key_type.supports_value_union()
            else ()
        )
    }

    for key, op in ops.items():
        op.__module__ = module_name
        op.__name__ = key

    # TODO: Pickling. These things should be looked up by name.
    return ops


def _create_globals(module_name, key_datatype, value_datatype):
    classes = _create_classes(module_name, key_datatype, value_datatype)
    set_type = classes['SetPy']
    set_ops = _create_set_operations(
        module_name, key_datatype, value_datatype, set_type,
    )

    classes.update(set_ops)
    return classes


def populate_module(mod_globals,
                    key_datatype, value_datatype,
                    interface, module=None):
    import collections.abc

    from . import Interfaces as interfaces
    from ._base import _fix_pickle
    from ._compat import import_c_extension

    module_name = mod_globals['__name__']
    # Define the Python implementations
    mod_globals.update(
        _create_globals(module_name, key_datatype, value_datatype)
    )
    # Import the C versions, if possible. Whether or not this is possible,
    # this currently makes the non-`Py' suffixed names available. This should
    # change if we start defining the Python classes with their natural name,
    # only aliased to the 'Py` suffix (which simplifies pickling)
    import_c_extension(mod_globals)

    # Next, define __all__ after all the name aliasing is done.
    # XXX: Maybe derive this from the values we create.
    mod_all = (
        'Bucket', 'Set', 'BTree', 'TreeSet',
        'union', 'intersection', 'difference',
        'weightedUnion', 'weightedIntersection', 'multiunion',
    )
    prefix = key_datatype.prefix_code + value_datatype.prefix_code

    mod_all += tuple(prefix + c for c in ('Bucket', 'Set', 'BTree', 'TreeSet'))

    mod_globals['__all__'] = tuple(c for c in mod_all if c in mod_globals)

    mod_globals['using64bits'] = (
        key_datatype.using64bits or value_datatype.using64bits
    )

    # XXX: We can probably do better than fix_pickle now;
    # we can know if we're going to be renaming classes
    # ahead of time. See above.
    _fix_pickle(mod_globals, module_name)

    # Apply interface definitions.
    directlyProvides(module or sys.modules[module_name], interface)
    for cls_name, iface in {
            'BTree': interfaces.IBTree,
            'Bucket': interfaces.IMinimalDictionary,
            'Set': interfaces.ISet,
            'TreeSet': interfaces.ITreeSet,
            'TreeItems': interfaces.IMinimalSequence,
    }.items():
        classImplements(mod_globals[cls_name], iface)
        classImplements(mod_globals[cls_name + 'Py'], iface)

    for cls_name, abc in {
            'BTree': collections.abc.MutableMapping,
            'Bucket': collections.abc.MutableMapping,
            'Set': collections.abc.MutableSet,
            'TreeSet': collections.abc.MutableSet,
    }.items():
        abc.register(mod_globals[cls_name])
        # Because of some quirks in the implementation of
        # ABCMeta.__instancecheck__, and the shenanigans we currently do to
        # make Python classes pickle without the 'Py' suffix, it's not actually
        # necessary to register the Python version of the class. Specifically,
        # ABCMeta asks for the object's ``__class__`` instead of using
        # ``type()``, and our objects have a ``@property`` for ``__class__``
        # that returns the C version.
        #
        # That's too many coincidences to rely on though.
        abc.register(mod_globals[cls_name + 'Py'])

    # Set node sizes.
    for cls_name in ('BTree', 'TreeSet'):

        for suffix in ('', 'Py'):
            cls = mod_globals[cls_name + suffix]
            cls.max_leaf_size = key_datatype.bucket_size_for_value(
                value_datatype
            )
            cls.max_internal_size = key_datatype.tree_size


def create_module(prefix):
    import types

    from . import Interfaces
    from . import _datatypes as datatypes

    mod = types.ModuleType('BTrees.' + prefix + 'BTree')

    key_type = getattr(datatypes, prefix[0])()
    val_type = getattr(datatypes, prefix[1])().as_value_type()

    iface_name = 'I' + key_type.long_name + val_type.long_name + 'BTreeModule'

    iface = getattr(Interfaces, iface_name)

    populate_module(vars(mod), key_type, val_type, iface, mod)
    return mod
