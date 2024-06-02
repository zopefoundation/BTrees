/*****************************************************************************

  Copyright (c) 2001, 2002 Zope Foundation and Contributors.
  All Rights Reserved.

  This software is subject to the provisions of the Zope Public License,
  Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
  WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
  WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
  FOR A PARTICULAR PURPOSE

 ****************************************************************************/
#include "Python.h"

#define SETTEMPLATE_C "$Id$\n"

static PyObject *
Set_insert(Bucket *self, PyObject *args)
{
    PyObject *key;
    int i;

    UNLESS (PyArg_ParseTuple(args, "O", &key))
        return NULL;
    if ( (i=_bucket_set(self, key, Py_None, 1, 1, 0)) < 0)
        return NULL;
    return PyLong_FromLong(i);
}

/* _Set_update and _TreeSet_update are identical except for the
   function they call to add the element to the set.
*/

static int
_Set_update(Bucket *self, PyObject *seq)
{
    int n=0, ind=0;
    PyObject *iter, *v;

    iter = PyObject_GetIter(seq);
    if (iter == NULL)
        return -1;

    while (1) {
        v = PyIter_Next(iter);
        if (v == NULL) {
            if (PyErr_Occurred())
                goto err;
            else
                break;
        }
        ind = _bucket_set(self, v, Py_None, 1, 1, 0);
        Py_DECREF(v);
        if (ind < 0)
            goto err;
        else
            n += ind;
    }

err:
    Py_DECREF(iter);
    if (ind < 0)
        return -1;
    return n;
}

static PyObject *
Set_update(Bucket *self, PyObject *args)
{
    PyObject *seq = NULL;
    int n = 0;

    if (!PyArg_ParseTuple(args, "|O:update", &seq))
        return NULL;

    if (seq) {
        n = _Set_update(self, seq);
        if (n < 0)
            return NULL;
    }

    return PyLong_FromLong(n);
}

static PyObject *
Set_remove(Bucket *self, PyObject *args)
{
    PyObject *key;

    UNLESS (PyArg_ParseTuple(args, "O", &key))
        return NULL;
    if (_bucket_set(self, key, NULL, 0, 1, 0) < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
Set_discard(Bucket* self, PyObject* args)
{
    PyObject *key;

    UNLESS (PyArg_ParseTuple(args, "O", &key))
        return NULL;

    if (_bucket_set(self, key, NULL, 0, 1, 0) < 0) {
        if (BTree_ShouldSuppressKeyError()) {
            PyErr_Clear();
        }
        else if (PyErr_ExceptionMatches(PyExc_TypeError)) {
            /* Failed to compare, so it can't be in the tree. */
            PyErr_Clear();
        }
        else {
            return NULL;
        }
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
Set_pop(Bucket* self, PyObject* args)
{
    PyObject* result = NULL;
    PyObject* key = NULL;
    PyObject* remove_args = NULL;
    PyObject* remove_result = NULL;

    if (PyTuple_Size(args) != 0) {
        PyErr_SetString(PyExc_TypeError, "pop(): Takes no arguments.");
        return NULL;
    }

    key = Bucket_minKey(self, args); /* reuse existing empty tuple */
    if (!key) {
        PyErr_Clear();
        PyErr_SetString(PyExc_KeyError, "pop(): empty bucket.");
        return NULL;
    }

    remove_args = PyTuple_Pack(1, key);
    if (remove_args) {
        remove_result = Set_remove(self, remove_args);
        Py_DECREF(remove_args);
        if (remove_result) {
            Py_INCREF(key);
            result = key;
            Py_DECREF(remove_result);
        }
    }

    return result;
}

static PyObject*
Set_isdisjoint(Bucket* self, PyObject* other)
{
    PyObject* iter = NULL;
    PyObject* result = NULL;
    PyObject* v = NULL;
    int contained = 0;

    if (other == (PyObject*)self) {
        if (self->len == 0) {
            Py_RETURN_TRUE;
        }
        else {
            Py_RETURN_FALSE;
        }
    }


    iter = PyObject_GetIter(other);
    if (iter == NULL) {
        return NULL;
    }

    while (1) {
        if (result != NULL) {
            break;
        }

        v = PyIter_Next(iter);
        if (v == NULL) {
            if (PyErr_Occurred()) {
                goto err;
            }
            else {
                break;
            }
        }
        contained = bucket_contains(self, v);
        if (contained == -1) {
            goto err;
        }
        if (contained == 1) {
            result = Py_False;
        }
        Py_DECREF(v);
    }

    if (result == NULL) {
        result = Py_True;
    }
    Py_INCREF(result);

err:
    Py_DECREF(iter);
    return result;
}

static int
_set_setstate(Bucket *self, PyObject *args)
{
    PyObject *k, *items;
    Bucket *next=0;
    int i, l, copied=1;
    KEY_TYPE *keys;

    UNLESS (PyArg_ParseTuple(args, "O|O", &items, &next))
        return -1;

    if (!PyTuple_Check(items)) {
        PyErr_SetString(PyExc_TypeError,
                        "tuple required for first state element");
        return -1;
    }

    if ((l=PyTuple_Size(items)) < 0)
        return -1;

    for (i=self->len; --i >= 0; )
    {
        DECREF_KEY(self->keys[i]);
    }
    self->len=0;

    if (self->next)
    {
        Py_DECREF(self->next);
        self->next=0;
    }

    if (l > self->size)
    {
        UNLESS (keys=BTree_Realloc(self->keys, sizeof(KEY_TYPE)*l))
            return -1;
        self->keys=keys;
        self->size=l;
    }

    for (i=0; i<l; i++)
    {
        k=PyTuple_GET_ITEM(items, i);
        COPY_KEY_FROM_ARG(self->keys[i], k, copied);
        UNLESS (copied)
            return -1;
        INCREF_KEY(self->keys[i]);
    }

    self->len=l;

    if (next)
    {
        self->next=next;
        Py_INCREF(next);
    }

    return 0;
}

static PyObject *
set_setstate(Bucket *self, PyObject *args)
{
    int r;

    UNLESS (PyArg_ParseTuple(args, "O", &args))
        return NULL;

    PER_PREVENT_DEACTIVATION(self);
    r=_set_setstate(self, args);
    PER_UNUSE(self);

    if (r < 0)
        return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}

static struct PyMethodDef Set_methods[] = {
    {"__getstate__", (PyCFunction) bucket_getstate, METH_VARARGS,
     "__getstate__()\nReturn the picklable state of the object"},

    {"__setstate__", (PyCFunction) set_setstate, METH_VARARGS,
     "__setstate__()\nSet the state of the object"},

    {"keys", (PyCFunction) bucket_keys, METH_VARARGS | METH_KEYWORDS,
     "keys()\nReturn the keys"},

    {"has_key", (PyCFunction) bucket_has_key, METH_O,
     "has_key(key)\nTest whether the bucket contains the given key"},

    {"clear", (PyCFunction) bucket_clear, METH_VARARGS,
     "clear()\nRemove all of the items from the bucket"},

    {"maxKey", (PyCFunction) Bucket_maxKey, METH_VARARGS,
     "maxKey([key])\nFind the maximum key\n\n"
     "If an argument is given, find the maximum <= the argument"},

    {"minKey", (PyCFunction) Bucket_minKey, METH_VARARGS,
     "minKey([key])\nFind the minimum key\n\n"
     "If an argument is given, find the minimum >= the argument"},

#ifdef PERSISTENT
    {"_p_resolveConflict",
     (PyCFunction) bucket__p_resolveConflict, METH_VARARGS,
     "_p_resolveConflict()\nReinitialize from a newly created copy"},

    {"_p_deactivate",
     (PyCFunction) bucket__p_deactivate, METH_VARARGS | METH_KEYWORDS,
     "_p_deactivate()\nReinitialize from a newly created copy"},
#endif

    {"add", (PyCFunction)Set_insert, METH_VARARGS,
     "add(id)\nAdd a key to the set"},

    {"insert", (PyCFunction)Set_insert, METH_VARARGS,
     "insert(id)\nAdd a key to the set"},

    {"update", (PyCFunction)Set_update,    METH_VARARGS,
     "update(seq)\nAdd the items from the given sequence to the set"},

    {"remove",    (PyCFunction)Set_remove,    METH_VARARGS,
     "remove(id)\nRemove an id from the set"},

    {"discard", (PyCFunction)Set_discard, METH_VARARGS,
     "Remove an element from a set if it is a member.\n\n"
     "If the element is not a member, do nothing."},

    {"isdisjoint", (PyCFunction)Set_isdisjoint, METH_O,
     "Return True if two sets have a null intersection."},

    {"pop", (PyCFunction)Set_pop, METH_VARARGS,
     "Remove and return an arbitrary item."},

    {NULL, NULL}        /* sentinel */
};

static int
Set_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *v = NULL;

    if (!PyArg_ParseTuple(args, "|O:" MOD_NAME_PREFIX "Set", &v))
        return -1;

    if (v)
        return _Set_update((Bucket *)self, v);
    else
        return 0;
}



static PyObject *
set_repr(Bucket *self)
{
    static PyObject *format;
    PyObject *r, *t;

    if (!format)
        format = PyUnicode_FromString(MOD_NAME_PREFIX "Set(%s)");
    UNLESS (t = PyTuple_New(1))
        return NULL;
    UNLESS (r = bucket_keys(self, NULL, NULL))
        goto err;
    PyTuple_SET_ITEM(t, 0, r);
    r = t;
    ASSIGN(r, PyUnicode_Format(format, r));
    return r;
err:
    Py_DECREF(t);
    return NULL;
}

static Py_ssize_t
set_length(Bucket *self)
{
    int r;

    PER_USE_OR_RETURN(self, -1);
    r = self->len;
    PER_UNUSE(self);

    return r;
}

static PyObject *
set_item(Bucket *self, Py_ssize_t index)
{
    PyObject *r=0;

    PER_USE_OR_RETURN(self, NULL);
    if (index >= 0 && index < self->len)
    {
        COPY_KEY_TO_OBJECT(r, self->keys[index]);
    }
    else
        IndexError(index);

    PER_UNUSE(self);

    return r;
}

/*
 * In-place operators.
 * The implementation is identical with TreeSet, with the only
 * differences being the calls to insert/remove items and clear
 * the object.
 *
 * This implementation is naive and matches the Python versions, accepting
 * nearly any iterable.
 */

static PyObject*
set_isub(Bucket* self, PyObject* other)
{
    PyObject* iter = NULL;
    PyObject* result = NULL;
    PyObject* v = NULL;

    if (other == (PyObject*)self) {
        v = bucket_clear(self, NULL);
        if (v == NULL) {
            goto err;
        }
        Py_DECREF(v);
    }
    else {
        iter = PyObject_GetIter(other);
        if (iter == NULL) {
            PyErr_Clear();
            Py_INCREF(Py_NotImplemented);
            return Py_NotImplemented;
        }

        while (1) {
            v = PyIter_Next(iter);
            if (v == NULL) {
                if (PyErr_Occurred()) {
                    goto err;
                }
                else {
                    break;
                }
            }
            if (_bucket_set(self, v, NULL, 0, 1, 0) < 0) {
                if (BTree_ShouldSuppressKeyError()) {
                    PyErr_Clear();
                }
                else {
                    Py_DECREF(v);
                    goto err;
                }
            }
            Py_DECREF(v);
        }
    }

    Py_INCREF(self);
    result = (PyObject*)self;

err:
    Py_XDECREF(iter);
    return result;
}

static PyObject*
set_ior(Bucket* self, PyObject* other)
{
    PyObject* update_args = NULL;
    PyObject* result = NULL;

    update_args = PyTuple_Pack(1, other);
    if (!update_args) {
        return NULL;
    }

    result = Set_update(self, update_args);
    Py_DECREF(update_args);
    if (!result) {
        return NULL;
    }

    Py_DECREF(result);
    Py_INCREF(self);
    return (PyObject*)self;
}

static PyObject*
set_ixor(Bucket* self, PyObject* other)
{
    PyObject* iter = NULL;
    PyObject* result = NULL;
    PyObject* v = NULL;
    int contained = 0;

    if (other == (PyObject*)self) {
        v = bucket_clear(self, NULL);
        if (v == NULL) {
            goto err;
        }
        Py_DECREF(v);
    }
    else {
        iter = PyObject_GetIter(other);
        if (iter == NULL) {
            PyErr_Clear();
            Py_INCREF(Py_NotImplemented);
            return Py_NotImplemented;
        }

        while (1) {
            v = PyIter_Next(iter);
            if (v == NULL) {
                if (PyErr_Occurred()) {
                    goto err;
                }
                else {
                    break;
                }
            }
            /* contained is also used as an error flag for the removal/addition */
            contained = bucket_contains(self, v);
            if (contained != -1) {
                /* If not present (contained == 0), add it, otherwise remove it. */
                contained = _bucket_set(self, v,
                                        contained == 0 ? Py_None : NULL,
                                        contained == 0 ? 1 : 0,
                                        1, 0);
            }
            Py_DECREF(v);
            if (contained < 0) {
                goto err;
            }
        }
    }

    Py_INCREF(self);
    result = (PyObject*)self;

err:
    Py_XDECREF(iter);
    return result;
}

static PyObject*
Generic_set_xor(PyObject* self, PyObject* other)
{
    PyObject* set_self = NULL;
    PyObject* set_other = NULL;
    PyObject* set_xor = NULL;
    PyObject* result = NULL;

    set_self = PySet_New(self);
    set_other = PySet_New(other);
    if (set_self == NULL || set_other == NULL) {
        goto err;
    }

    set_xor = PyNumber_Xor(set_self, set_other);
    if (set_xor == NULL) {
        goto err;
    }

    result = PyObject_CallFunctionObjArgs((PyObject*)Py_TYPE(self), set_xor, NULL);

err:
    Py_XDECREF(set_self);
    Py_XDECREF(set_other);
    Py_XDECREF(set_xor);
    return result;
}

static PyObject*
set_iand(Bucket* self, PyObject* other)
{
    PyObject* iter = NULL;
    PyObject* v = NULL;
    PyObject* result = NULL;
    PyObject* tmp_list = NULL;
    int contained = 0;

    tmp_list = PyList_New(0);
    if (tmp_list == NULL) {
        return NULL;
    }

    iter = PyObject_GetIter(other);
    if (iter == NULL) {
        PyErr_Clear();
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }

    while (1) {
        v = PyIter_Next(iter);
        if (v == NULL) {
            if (PyErr_Occurred()) {
                goto err;
            }
            else {
                break;
            }
        }
        contained = bucket_contains(self, v);
        if (contained == 1) {
            /* Yay, we had it and get to keep it. */
            if (PyList_Append(tmp_list, v) < 0) {
                Py_DECREF(v);
                goto err;
            }
        }
        /* Done with the sequence value now
           Either it was already in the set, which is fine,
           or there was an error.
        */
        Py_DECREF(v);
        if (contained == -1) {
            goto err;
        }
    }

    /* Replace our contents with the list of keys we built. */
    v = bucket_clear(self, NULL);
    if (v == NULL) {
        goto err;
    }
    Py_DECREF(v);
    if (_Set_update(self, tmp_list) < 0) {
        goto err;
    }

    Py_INCREF(self);
    result = (PyObject*)self;

err:
    Py_DECREF(iter);
    Py_DECREF(tmp_list);

    return result;
}

static PySequenceMethods set_as_sequence = {
    (lenfunc)set_length,                /* sq_length */
    (binaryfunc)0,                      /* sq_concat */
    (ssizeargfunc)0,                    /* sq_repeat */
    (ssizeargfunc)set_item,             /* sq_item */
    (ssizessizeargfunc)0,               /* sq_slice */
    (ssizeobjargproc)0,                 /* sq_ass_item */
    (ssizessizeobjargproc)0,            /* sq_ass_slice */
    (objobjproc)bucket_contains,        /* sq_contains */
    0,                                  /* sq_inplace_concat */
    0,                                  /* sq_inplace_repeat */
};

static PyNumberMethods set_as_number = {
     (binaryfunc)0,                     /* nb_add */
     bucket_sub,                        /* nb_subtract */
     (binaryfunc)0,                     /* nb_multiply */
     (binaryfunc)0,                     /* nb_remainder */
     (binaryfunc)0,                     /* nb_divmod */
     (ternaryfunc)0,                    /* nb_power */
     (unaryfunc)0,                      /* nb_negative */
     (unaryfunc)0,                      /* nb_positive */
     (unaryfunc)0,                      /* nb_absolute */
     (inquiry)0,                        /* nb_bool */
     (unaryfunc)0,                      /* nb_invert */
     (binaryfunc)0,                     /* nb_lshift */
     (binaryfunc)0,                     /* nb_rshift */
     bucket_and,                        /* nb_and */
     (binaryfunc)Generic_set_xor,       /* nb_xor */
     bucket_or,                         /* nb_or */
     0,                                 /*nb_int*/
     0,                                 /*nb_reserved*/
     0,                                 /*nb_float*/
     0,                                 /*nb_inplace_add*/
     (binaryfunc)set_isub,              /*nb_inplace_subtract*/
     0,                                 /*nb_inplace_multiply*/
     0,                                 /*nb_inplace_remainder*/
     0,                                 /*nb_inplace_power*/
     0,                                 /*nb_inplace_lshift*/
     0,                                 /*nb_inplace_rshift*/
     (binaryfunc)set_iand,              /*nb_inplace_and*/
     (binaryfunc)set_ixor,              /*nb_inplace_xor*/
     (binaryfunc)set_ior,               /*nb_inplace_or*/
};

static PyTypeObject SetType = {
    PyVarObject_HEAD_INIT(NULL, 0)      /* PyPersist_Type */
    MODULE_NAME MOD_NAME_PREFIX "Set",  /* tp_name */
    sizeof(Bucket),                     /* tp_basicsize */
    0,                                  /* tp_itemsize */
    (destructor)bucket_dealloc,         /* tp_dealloc */
    0,                                  /* tp_print */
    0,                                  /* tp_getattr */
    0,                                  /* tp_setattr */
    0,                                  /* tp_compare */
    (reprfunc)set_repr,                 /* tp_repr */
    &set_as_number,                     /* tp_as_number */
    &set_as_sequence,                   /* tp_as_sequence */
    0,                                  /* tp_as_mapping */
    0,                                  /* tp_hash */
    0,                                  /* tp_call */
    0,                                  /* tp_str */
    0,                                  /* tp_getattro */
    0,                                  /* tp_setattro */
    0,                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT |
    Py_TPFLAGS_HAVE_GC |
    Py_TPFLAGS_BASETYPE,                /* tp_flags */
    0,                                  /* tp_doc */
    (traverseproc)bucket_traverse,      /* tp_traverse */
    (inquiry)bucket_tp_clear,           /* tp_clear */
    0,                                  /* tp_richcompare */
    0,                                  /* tp_weaklistoffset */
    (getiterfunc)Bucket_getiter,        /* tp_iter */
    0,                                  /* tp_iternext */
    Set_methods,                        /* tp_methods */
    Bucket_members,                     /* tp_members */
    0,                                  /* tp_getset */
    0,                                  /* tp_base */
    0,                                  /* tp_dict */
    0,                                  /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    Set_init,                           /* tp_init */
    0,                                  /* tp_alloc */
    0, /*PyType_GenericNew,*/           /* tp_new */
};

static int
nextSet(SetIteration *i)
{

    if (i->position >= 0)
    {
        UNLESS(PER_USE(BUCKET(i->set)))
            return -1;

        if (i->position)
        {
          DECREF_KEY(i->key);
        }

        if (i->position < BUCKET(i->set)->len)
        {
          COPY_KEY(i->key, BUCKET(i->set)->keys[i->position]);
          INCREF_KEY(i->key);
          i->position ++;
        }
        else
        {
          i->position = -1;
          PER_ACCESSED(BUCKET(i->set));
        }

      PER_ALLOW_DEACTIVATION(BUCKET(i->set));
    }


  return 0;
}
