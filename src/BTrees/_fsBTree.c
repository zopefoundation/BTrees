/*############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################*/

#define MASTER_ID "$Id$\n"

/* fsBTree - FileStorage index BTree

   This BTree implements a mapping from 2-character strings
   to six-character strings. This allows us to efficiently store
   a FileStorage index as a nested mapping of 6-character oid prefix
   to mapping of 2-character oid suffix to 6-character (byte) file
   positions.
*/

typedef unsigned char char2[2];
typedef unsigned char char6[6];

/* Setup template macros */

#define PERSISTENT

#define MOD_NAME_PREFIX "fs"




#include "_compat.h"
/*#include "intkeymacros.h"*/

#define KEYMACROS_H "$Id$\n"
#define KEY_TYPE char2
#undef KEY_TYPE_IS_PYOBJECT
#define KEY_CHECK(K) (PyBytes_Check(K) && PyBytes_GET_SIZE(K)==2)
#define TEST_KEY_SET_OR(V, K, T) if ( ( (V) = ((*(K) < *(T) || (*(K) == *(T) && (K)[1] < (T)[1])) ? -1 : ((*(K) == *(T) && (K)[1] == (T)[1]) ? 0 : 1)) ), 0 )
#define DECREF_KEY(KEY)
#define INCREF_KEY(k)
#define COPY_KEY(KEY, E) (*(KEY)=*(E), (KEY)[1]=(E)[1])
#define COPY_KEY_TO_OBJECT(O, K) O=PyBytes_FromStringAndSize((const char*)K,2)
#define COPY_KEY_FROM_ARG(TARGET, ARG, STATUS) \
  if (KEY_CHECK(ARG)) memcpy(TARGET, PyBytes_AS_STRING(ARG), 2); else { \
      PyErr_SetString(PyExc_TypeError, "expected two-character string key"); \
      (STATUS)=0; }

/*#include "intvaluemacros.h"*/
#define VALUEMACROS_H "$Id$\n"
#define VALUE_TYPE char6
#undef VALUE_TYPE_IS_PYOBJECT
#define TEST_VALUE(K, T) memcmp(K,T,6)
#define DECREF_VALUE(k)
#define INCREF_VALUE(k)
#define COPY_VALUE(V, E) (memcpy(V, E, 6))
#define COPY_VALUE_TO_OBJECT(O, K) O=PyBytes_FromStringAndSize((const char*)K,6)
#define COPY_VALUE_FROM_ARG(TARGET, ARG, STATUS) \
  if ((PyBytes_Check(ARG) && PyBytes_GET_SIZE(ARG)==6)) \
      memcpy(TARGET, PyBytes_AS_STRING(ARG), 6); else { \
      PyErr_SetString(PyExc_TypeError, "expected six-character string key"); \
      (STATUS)=0; }

#define NORMALIZE_VALUE(V, MIN)

#include "Python.h"

static PyObject *bucket_toBytes(PyObject *self);

static PyObject *bucket_fromBytes(PyObject *self, PyObject *state);

#define EXTRA_BUCKET_METHODS \
    {"toBytes", (PyCFunction) bucket_toBytes,	METH_NOARGS, \
     "toBytes() -- Return the state as a bytes array"}, \
    {"fromBytes", (PyCFunction) bucket_fromBytes,	METH_O, \
     "fromSBytes(s) -- Set the state of the object from a bytes array"}, \
    {"toString", (PyCFunction) bucket_toBytes,	METH_NOARGS, \
     "toString() -- Deprecated alias for 'toBytes'"}, \
    {"fromString", (PyCFunction) bucket_fromBytes,	METH_O, \
     "fromString(s) -- Deprecated alias for 'fromBytes'"}, \

#define INITMODULE PyInit__fsBTree
#include "BTreeModuleTemplate.c"

static PyObject *
bucket_toBytes(PyObject *oself)
{
  Bucket *self = (Bucket *)oself;
  PyObject *items = NULL;
  int len;

  PER_USE_OR_RETURN(self, NULL);

  len = self->len;

  items = PyBytes_FromStringAndSize(NULL, len*8);
  if (items == NULL)
    goto err;
  memcpy(PyBytes_AS_STRING(items),       self->keys,   len*2);
  memcpy(PyBytes_AS_STRING(items)+len*2, self->values, len*6);

  PER_UNUSE(self);
  return items;

 err:
  PER_UNUSE(self);
  Py_XDECREF(items);
  return NULL;
}

static PyObject *
bucket_fromBytes(PyObject *oself, PyObject *state)
{
  Bucket *self = (Bucket *)oself;
  int len;
  KEY_TYPE *keys;
  VALUE_TYPE *values;

  len = PyBytes_Size(state);
  if (len < 0)
    return NULL;

  if (len%8)
    {
      PyErr_SetString(PyExc_ValueError, "state string of wrong size");
      return NULL;
    }
  len /= 8;

  if (self->next) {
    Py_DECREF(self->next);
    self->next = NULL;
  }

  if (len > self->size) {
    keys = BTree_Realloc(self->keys, sizeof(KEY_TYPE)*len);
    if (keys == NULL)
      return NULL;
    values = BTree_Realloc(self->values, sizeof(VALUE_TYPE)*len);
    if (values == NULL)
      return NULL;
    self->keys = keys;
    self->values = values;
    self->size = len;
  }

  memcpy(self->keys,   PyBytes_AS_STRING(state),       len*2);
  memcpy(self->values, PyBytes_AS_STRING(state)+len*2, len*6);

  self->len = len;

  Py_INCREF(self);
  return (PyObject *)self;
}
