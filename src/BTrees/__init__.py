#############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
#############################################################################

import sys
import zope.interface
import BTrees.Interfaces
from ._module_builder import create_module

__all__ = [
    'family32',
    'family64',
]

_FAMILIES = (
    # Signed 32-bit keys
    "IO", # object value
    "II", # self value
    "IF", # float value
    "IU", # opposite sign value
    # Unsigned 32-bit keys
    "UO", # object value
    "UU", # self value
    "UF", # float value
    "UI", # opposite sign value
    # Signed 64-bit keys
    "LO", # object value
    "LL", # self value
    "LF", # float value
    "LQ", # opposite sign value
    # Unsigned 64-bit keys
    "QO", # object value
    "QQ", # self value
    "QF", # float value
    "QL", # opposite sign value
    # Object keys
    "OO", # object
    "OI", # 32-bit signed
    "OU", # 32-bit unsigned
    "OL", # 64-bit signed
    "OQ", # 64-bit unsigned
    # Special purpose
    'fs', # 2-byte -> 6-byte
)

# XXX: Do this without completely ruining
# pylint and other static analysis.
for family in _FAMILIES:
    mod = create_module(family)
    name = vars(mod)['__name__']
    sys.modules[name] = mod
    globals()[name.split('.', 1)[1]] = mod
    __all__.append(name)


@zope.interface.implementer(BTrees.Interfaces.IBTreeFamily)
class _Family:
    from BTrees import OOBTree as OO
    _BITSIZE = 0
    minint = maxint = maxuint = None

    def __init__(self):
        self.maxint = int(2 ** (self._BITSIZE - 1) - 1)
        self.minint = int(-self.maxint - 1)
        self.maxuint = int(2 ** self._BITSIZE - 1)

    def __str__(self):
        return (
            "BTree family using {} bits. "
            "Supports signed integer values from {:,} to {:,} "
            "and maximum unsigned integer value {:,}."
        ).format(self._BITSIZE, self.minint, self.maxint, self.maxuint)

    def __repr__(self):
        return "<%s>" % (
            self
        )

class _Family32(_Family):
    _BITSIZE = 32
    from BTrees import OIBTree as OI
    from BTrees import OUBTree as OU

    from BTrees import IFBTree as IF
    from BTrees import IIBTree as II
    from BTrees import IOBTree as IO
    from BTrees import IUBTree as IU

    from BTrees import UFBTree as UF
    from BTrees import UIBTree as UI
    from BTrees import UOBTree as UO
    from BTrees import UUBTree as UU

    def __reduce__(self):
        return _family32, ()

class _Family64(_Family):
    _BITSIZE = 64
    from BTrees import OLBTree as OI
    from BTrees import OQBTree as OU

    from BTrees import LFBTree as IF
    from BTrees import LLBTree as II
    from BTrees import LOBTree as IO
    from BTrees import LQBTree as IU

    from BTrees import QFBTree as UF
    from BTrees import QLBTree as UI
    from BTrees import QOBTree as UO
    from BTrees import QQBTree as UU

    def __reduce__(self):
        return _family64, ()

def _family32():
    return family32
_family32.__safe_for_unpickling__ = True

def _family64():
    return family64
_family64.__safe_for_unpickling__ = True

#: 32-bit BTree family.
family32 = _Family32()

#: 64-bit BTree family.
family64 = _Family64()

for _family in family32, family64:
    for _mod_name in (
            "OI", "OU",
            'IO', "II", "IF", "IU",
            "UO", "UU", "UF", "UI",
    ):
        getattr(_family, _mod_name).family = _family

# The IMergeBTreeModule interface specifies the ``family`` attribute,
# and fsBTree implements IIntegerObjectBTreeModule, which extends that
# interface. But for fsBTrees, no family makes particular sense, so we
# arbitrarily pick one.
globals()['fsBTree'].family = family64
