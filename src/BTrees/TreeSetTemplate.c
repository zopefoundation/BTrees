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
#include "_compat.h"

#define TREESETTEMPLATE_C "$Id$\n"

static PyObject *
TreeSet_insert(BTree *self, PyObject *args)
{
    PyObject *key;
    int i;

    if (!PyArg_ParseTuple(args, "O:insert", &key))
        return NULL;
    i = _BTree_set(self, key, Py_None, 1, 1);
    if (i < 0)
        return NULL;
    return INT_FROM_LONG(i);
}

/* _Set_update and _TreeSet_update are identical except for the
   function they call to add the element to the set.
*/

static int
_TreeSet_update(BTree *self, PyObject *seq)
{
    int n=0, ind=0;
    PyObject *iter, *v;

    iter = PyObject_GetIter(seq);
    if (iter == NULL)
        return -1;

    while (1)
    {
        v = PyIter_Next(iter);
        if (v == NULL)
        {
            if (PyErr_Occurred())
                goto err;
            else
                break;
        }
        ind = _BTree_set(self, v, Py_None, 1, 1);
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
TreeSet_update(BTree *self, PyObject *args)
{
    PyObject *seq = NULL;
    int n = 0;

    if (!PyArg_ParseTuple(args, "|O:update", &seq))
        return NULL;

    if (seq)
    {
        n = _TreeSet_update(self, seq);
        if (n < 0)
            return NULL;
    }

    return INT_FROM_LONG(n);
}


static PyObject *
TreeSet_remove(BTree *self, PyObject *args)
{
    PyObject *key;

    UNLESS (PyArg_ParseTuple(args, "O", &key))
        return NULL;
    if (_BTree_set(self, key, NULL, 0, 1) < 0)
        return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
TreeSet_discard(BTree *self, PyObject *args)
{
    PyObject *key;

    UNLESS (PyArg_ParseTuple(args, "O", &key))
        return NULL;

    if (_BTree_set(self, key, NULL, 0, 1) < 0) {
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
TreeSet_pop(BTree* self, PyObject* args)
{
    PyObject* result = NULL;
    PyObject* key = NULL;
    PyObject* remove_args = NULL;
    PyObject* remove_result = NULL;

    if (PyTuple_Size(args) != 0) {
        PyErr_SetString(PyExc_TypeError, "pop(): Takes no arguments.");
        return NULL;
    }

    key = BTree_minKey(self, args); /* reuse existing empty tuple */
    if (!key) {
        PyErr_Clear();
        PyErr_SetString(PyExc_KeyError, "pop(): empty tree.");
        return NULL;
    }

    remove_args = PyTuple_Pack(1, key);
    if (remove_args) {
        remove_result = TreeSet_remove(self, remove_args);
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
TreeSet_isdisjoint(BTree* self, PyObject* other)
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
        contained = BTree_contains(self, v);
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


static PyObject *
TreeSet_setstate(BTree *self, PyObject *args)
{
    int r;

    if (!PyArg_ParseTuple(args,"O",&args))
        return NULL;

    PER_PREVENT_DEACTIVATION(self);
    r=_BTree_setstate(self, args, 1);
    PER_UNUSE(self);

    if (r < 0)
        return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}

static struct PyMethodDef TreeSet_methods[] =
{
    {"__getstate__", (PyCFunction) BTree_getstate, METH_NOARGS,
     "__getstate__() -> state\n\n"
     "Return the picklable state of the TreeSet."},

    {"__setstate__", (PyCFunction) TreeSet_setstate, METH_VARARGS,
     "__setstate__(state)\n\n"
     "Set the state of the TreeSet."},

    {"has_key", (PyCFunction) BTree_has_key, METH_O,
     "has_key(key)\n\n"
     "Return true if the TreeSet contains the given key."},

    {"keys", (PyCFunction) BTree_keys, METH_VARARGS | METH_KEYWORDS,
     "keys([min, max]) -> list of keys\n\n"
     "Returns the keys of the TreeSet.  If min and max are supplied, only\n"
     "keys greater than min and less than max are returned."},

    {"maxKey", (PyCFunction) BTree_maxKey, METH_VARARGS,
     "maxKey([max]) -> key\n\n"
     "Return the largest key in the BTree.  If max is specified, return\n"
     "the largest key <= max."},

    {"minKey", (PyCFunction) BTree_minKey, METH_VARARGS,
     "minKey([mi]) -> key\n\n"
     "Return the smallest key in the BTree.  If min is specified, return\n"
     "the smallest key >= min."},

    {"clear", (PyCFunction) BTree_clear, METH_NOARGS,
     "clear()\n\nRemove all of the items from the BTree."},

    {"add", (PyCFunction)TreeSet_insert, METH_VARARGS,
     "add(id) -- Add an item to the set"},

    {"insert", (PyCFunction)TreeSet_insert, METH_VARARGS,
     "insert(id) -- Add an item to the set"},

    {"update", (PyCFunction)TreeSet_update, METH_VARARGS,
     "update(collection)\n\n Add the items from the given collection."},

    {"remove", (PyCFunction)TreeSet_remove, METH_VARARGS,
     "remove(id) -- Remove a key from the set"},

    {"discard", (PyCFunction)TreeSet_discard, METH_VARARGS,
     "Remove an element from a set if it is a member.\n\n"
     "If the element is not a member, do nothing."},

    {"pop", (PyCFunction)TreeSet_pop, METH_VARARGS,
     "pop() -- Remove and return a key from the set"},

    {"_check", (PyCFunction) BTree_check, METH_NOARGS,
     "Perform sanity check on TreeSet, and raise exception if flawed."},

#ifdef PERSISTENT
    {"_p_resolveConflict",
     (PyCFunction) BTree__p_resolveConflict, METH_VARARGS,
     "_p_resolveConflict() -- Reinitialize from a newly created copy"},

    {"_p_deactivate",
     (PyCFunction) BTree__p_deactivate, METH_VARARGS | METH_KEYWORDS,
     "_p_deactivate()\n\nReinitialize from a newly created copy."},
#endif

    {"isdisjoint", (PyCFunction)TreeSet_isdisjoint, METH_O,
     "Return True if two sets have a null intersection."},

    {NULL,        NULL}        /* sentinel */
};

static PyMappingMethods TreeSet_as_mapping = {
  (lenfunc)BTree_length,                        /*mp_length*/
};

static PySequenceMethods TreeSet_as_sequence = {
    (lenfunc)0,                                 /* sq_length */
    (binaryfunc)0,                              /* sq_concat */
    (ssizeargfunc)0,                            /* sq_repeat */
    (ssizeargfunc)0,                            /* sq_item */
    (ssizessizeargfunc)0,                       /* sq_slice */
    (ssizeobjargproc)0,                         /* sq_ass_item */
    (ssizessizeobjargproc)0,                    /* sq_ass_slice */
    (objobjproc)BTree_contains,                 /* sq_contains */
    0,                                          /* sq_inplace_concat */
    0,                                          /* sq_inplace_repeat */
};

static int
TreeSet_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *v = NULL;

    if (!PyArg_ParseTuple(args, "|O:" MOD_NAME_PREFIX "TreeSet", &v))
        return -1;

    if (v)
        return _TreeSet_update((BTree *)self, v);
    else
        return 0;
}

/*
 * In-place operators.
 * The implementation is identical with Set, with the only
 * differences being the calls to insert/remove items and clear
 * the object.
 *
 * This implementation is naive and matches the Python versions, accepting
 * nearly any iterable.
 */

static PyObject*
TreeSet_isub(BTree* self, PyObject* other)
{
    PyObject* iter = NULL;
    PyObject* result = NULL;
    PyObject* v = NULL;

    if (other == (PyObject*)self) {
        v = BTree_clear(self);
        if (v == NULL) {
            goto err;
        }
        Py_DECREF(v);
    }
    else {
        iter = PyObject_GetIter(other);
        if (iter == NULL) {
            PyErr_Clear();
            Py_RETURN_NOTIMPLEMENTED;
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
            if (_BTree_set(self, v, NULL, 0, 1) < 0) {
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
TreeSet_ior(BTree* self, PyObject* other)
{
    PyObject* update_args = NULL;
    PyObject* result = NULL;

    update_args = PyTuple_Pack(1, other);
    if (!update_args) {
        return NULL;
    }

    result = TreeSet_update(self, update_args);
    Py_DECREF(update_args);
    if (!result) {
        return NULL;
    }

    Py_DECREF(result);
    Py_INCREF(self);
    return (PyObject*)self;
}

static PyObject*
TreeSet_ixor(BTree* self, PyObject* other)
{
    PyObject* iter = NULL;
    PyObject* result = NULL;
    PyObject* v = NULL;
    int contained = 0;

    if (other == (PyObject*)self) {
        v = BTree_clear(self);
        if (v == NULL) {
            goto err;
        }
        Py_DECREF(v);
    }
    else {
        iter = PyObject_GetIter(other);
        if (iter == NULL) {
            PyErr_Clear();
            Py_RETURN_NOTIMPLEMENTED;
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
            contained = BTree_contains(self, v);
            if (contained != -1) {
                /* If not present (contained == 0), add it, otherwise remove it. */
                contained = _BTree_set(self, v,
                                       contained == 0 ? Py_None : NULL,
                                       contained == 0 ? 1 : 0,
                                       1);
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
TreeSet_iand(BTree* self, PyObject* other)
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
        Py_RETURN_NOTIMPLEMENTED;
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
        contained = BTree_contains(self, v);
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
    v = BTree_clear(self);
    if (v == NULL) {
        goto err;
    }
    Py_DECREF(v);
    if (_TreeSet_update(self, tmp_list) < 0) {
        goto err;
    }

    Py_INCREF(self);
    result = (PyObject*)self;

err:
    Py_DECREF(iter);
    Py_DECREF(tmp_list);

    return result;

}


static PyNumberMethods TreeSet_as_number = {
    0,                                      /* nb_add */
    bucket_sub,                             /* nb_subtract */
    0,                                      /* nb_multiply */
    0,                                      /* nb_remainder */
    0,                                      /* nb_divmod */
    0,                                      /* nb_power */
    0,                                      /* nb_negative */
    0,                                      /* nb_positive */
    0,                                      /* nb_absolute */
    (inquiry)BTree_nonzero,                 /* nb_nonzero */
    (unaryfunc)0,                           /* nb_invert */
    (binaryfunc)0,                          /* nb_lshift */
    (binaryfunc)0,                          /* nb_rshift */
    bucket_and,                             /* nb_and */
    (binaryfunc)Generic_set_xor,            /* nb_xor */
    bucket_or,                              /* nb_or */
     0,                                 /*nb_int*/
     0,                                 /*nb_reserved*/
     0,                                 /*nb_float*/
     0,                                 /*nb_inplace_add*/
     (binaryfunc)TreeSet_isub,          /*nb_inplace_subtract*/
     0,                                 /*nb_inplace_multiply*/
     0,                                 /*nb_inplace_remainder*/
     0,                                 /*nb_inplace_power*/
     0,                                 /*nb_inplace_lshift*/
     0,                                 /*nb_inplace_rshift*/
     (binaryfunc)TreeSet_iand,          /*nb_inplace_and*/
     (binaryfunc)TreeSet_ixor,          /*nb_inplace_xor*/
     (binaryfunc)TreeSet_ior,           /*nb_inplace_or*/
};

static PyTypeObject TreeSetType =
{
    PyVarObject_HEAD_INIT(NULL, 0)
    MODULE_NAME MOD_NAME_PREFIX "TreeSet",      /* tp_name */
    sizeof(BTree),                              /* tp_basicsize */
    0,                                          /* tp_itemsize */
    (destructor)BTree_dealloc,                  /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_compare */
    0,                                          /* tp_repr */
    &TreeSet_as_number,                         /* tp_as_number */
    &TreeSet_as_sequence,                       /* tp_as_sequence */
    &TreeSet_as_mapping,                        /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    0,                                          /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT |
    Py_TPFLAGS_HAVE_GC |
    Py_TPFLAGS_BASETYPE,                        /* tp_flags */
    0,                                          /* tp_doc */
    (traverseproc)BTree_traverse,               /* tp_traverse */
    (inquiry)BTree_tp_clear,                    /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    (getiterfunc)BTree_getiter,                 /* tp_iter */
    0,                                          /* tp_iternext */
    TreeSet_methods,                            /* tp_methods */
    BTree_members,                              /* tp_members */
    0,                                          /* tp_getset */
    0,                                          /* tp_base */
    0,                                          /* tp_dict */
    0,                                          /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    TreeSet_init,                               /* tp_init */
    0,                                          /* tp_alloc */
    0, /*PyType_GenericNew,*/                   /* tp_new */
};
