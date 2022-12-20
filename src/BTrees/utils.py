##############################################################################
#
# Copyright (c) 2001-2012 Zope Foundation and Contributors.
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
# Copied from ZODB/utils.py

from binascii import hexlify


def non_negative(int_val):
    if int_val < 0:
        # Coerce to non-negative.
        int_val &= 0x7FFFFFFFFFFFFFFF
    return int_val


def positive_id(obj): # pragma: no cover
    """Return id(obj) as a non-negative integer."""
    return non_negative(id(obj))


def oid_repr(oid):
    if isinstance(oid, bytes) and len(oid) == 8:
        # Convert to hex and strip leading zeroes.
        as_hex = hexlify(oid).lstrip(b'0')
        # Ensure two characters per input byte.
        chunks = [b'0x']
        if len(as_hex) & 1:
            chunks.append(b'0')
        elif as_hex == b'':
            as_hex = b'00'
        chunks.append(as_hex)
        return b''.join(chunks)
    else:
        return repr(oid)


class Lazy:
    """
    A simple version of ``Lazy`` from ``zope.cachedescriptors``
    """

    __slots__ = ('func',)

    def __init__(self, func):
        self.func = func

    def __get__(self, inst, class_):
        if inst is None:
            return self

        func = self.func
        value = func(inst)
        inst.__dict__[func.__name__] = value
        return value
