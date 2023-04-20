/*****************************************************************************

  Copyright (c) 2012 Zope Foundation and Contributors.
  All Rights Reserved.

  This software is subject to the provisions of the Zope Public License,
  Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
  WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
  WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
  FOR A PARTICULAR PURPOSE

 ****************************************************************************/

#ifndef PERSISTENT__COMPAT_H
#define PERSISTENT__COMPAT_H

#include "Python.h"

#define INTERN PyUnicode_InternFromString
#define INTERN_INPLACE PyUnicode_InternInPlace
#define NATIVE_CHECK_EXACT PyUnicode_CheckExact
#define NATIVE_FROM_STRING_AND_SIZE PyUnicode_FromStringAndSize

#define Py_TPFLAGS_HAVE_RICHCOMPARE 0

#define INT_FROM_LONG(x) PyLong_FromLong(x)
#define INT_CHECK(x) PyLong_Check(x)
#define INT_AS_LONG(x) PyLong_AsLong(x)
#define CAPI_CAPSULE_NAME "persistent.cPersistence.CAPI"

#else
#define INTERN PyString_InternFromString
#define INTERN_INPLACE PyString_InternInPlace
#define NATIVE_CHECK_EXACT PyString_CheckExact
#define NATIVE_FROM_STRING_AND_SIZE PyString_FromStringAndSize

#define INT_FROM_LONG(x) PyInt_FromLong(x)
#define INT_CHECK(x) PyInt_Check(x)
#define INT_AS_LONG(x) PyInt_AS_LONG(x)

#endif
