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

import zope.interface
import BTrees.Interfaces


@zope.interface.implementer(BTrees.Interfaces.IBTreeFamily)
class _Family(object):
    from BTrees import OOBTree as OO
    _BITSIZE = 0
    minint = maxint = maxuint = 0

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

    maxuint = int(2**32)
    maxint = int(2**31-1)
    minint = -maxint - 1

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

    maxuint = 2**64
    maxint = 2**63-1
    minint = -maxint - 1

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
