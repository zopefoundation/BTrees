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
import sys

if sys.version_info[0] < 3: #pragma NO COVER Python2

    PY2 = True
    PY3 = False

    from StringIO import StringIO
    BytesIO = StringIO

    int_types = int, long
    xrange = xrange
    cmp = cmp

    _bytes = str
    def _ascii(x):
        return bytes(x)

    def _u(s, encoding='unicode_escape'):
        return unicode(s, encoding)

else: #pragma NO COVER Python3

    PY2 = False
    PY3 = True

    from io import StringIO
    from io import BytesIO

    int_types = int,
    xrange = range

    def cmp(x, y):
        return (x > y) - (y > x)

    _bytes = bytes
    def _ascii(x):
        return bytes(x, 'ascii')

    def _u(s, encoding=None):
        if encoding is None:
            return s
        return str(s, encoding)
