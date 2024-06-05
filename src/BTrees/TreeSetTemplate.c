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
    return PyLong_FromLong(i);
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

    return PyLong_FromLong(n);
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
    PyObject* obj_self = (PyObject*)self;
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);
    int r;

    if (!PyArg_ParseTuple(args,"O",&args))
        return NULL;

    per_prevent_deactivation((cPersistentObject*)self);
    r = _BTree_setstate(self, args, 1);
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);

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

static char TreeSet__name__[] = MODULE_NAME MOD_NAME_PREFIX "TreeSet";
static char TreeSet__doc__[] = "Result set mapped as a tree";

#if USE_STATIC_TYPES

static PyNumberMethods TreeSet_as_number = {
    .nb_subtract                = bucket_sub,
    .nb_bool                    = (inquiry)BTree_nonzero,
    .nb_and                     = bucket_and,
    .nb_xor                     = (binaryfunc)Generic_set_xor,
    .nb_or                      = bucket_or,
    .nb_inplace_subtract        = (binaryfunc)TreeSet_isub,
    .nb_inplace_and             = (binaryfunc)TreeSet_iand,
    .nb_inplace_xor             = (binaryfunc)TreeSet_ixor,
    .nb_inplace_or              = (binaryfunc)TreeSet_ior,
};

static PySequenceMethods TreeSet_as_sequence = {
    .sq_contains                = (objobjproc)BTree_contains,
};

static PyMappingMethods TreeSet_as_mapping = {
    .mp_length                  = (lenfunc)BTree_length,
};

static PyTypeObject TreeSet_type_def =
{
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name                    = TreeSet__name__,
    .tp_doc                     = TreeSet__doc__,
    .tp_basicsize               = sizeof(BTree),
    .tp_flags                   = Py_TPFLAGS_DEFAULT |
                                  Py_TPFLAGS_HAVE_GC |
                                  Py_TPFLAGS_BASETYPE,
    .tp_alloc                   = _pytype_generic_alloc,
    .tp_new                     = _pytype_generic_new,
    .tp_init                    = TreeSet_init,
    .tp_iter                    = (getiterfunc)BTree_getiter,
    .tp_traverse                = (traverseproc)BTree_traverse,
    .tp_clear                   = (inquiry)BTree_tp_clear,
    .tp_dealloc                 = (destructor)BTree_dealloc,
    .tp_methods                 = TreeSet_methods,
    .tp_members                 = BTree_members,
    .tp_as_number               = &TreeSet_as_number,
    .tp_as_sequence             = &TreeSet_as_sequence,
    .tp_as_mapping              = &TreeSet_as_mapping,
};

#else

static PyType_Slot TreeSet_type_slots[] = {
    {Py_tp_doc,                 TreeSet__doc__},
    {Py_tp_alloc,               _pytype_generic_alloc},
    {Py_tp_new,                 _pytype_generic_new},
    {Py_tp_init,                TreeSet_init},
    {Py_tp_iter,                BTree_getiter},
    {Py_tp_traverse,            BTree_traverse},
    {Py_tp_clear,               BTree_tp_clear},
    {Py_tp_dealloc,             BTree_dealloc},
    {Py_tp_methods,             TreeSet_methods},
    {Py_tp_members,             BTree_members},
    {Py_nb_subtract,            bucket_sub},
    {Py_nb_bool,                (inquiry)BTree_nonzero},
    {Py_nb_and,                 bucket_and},
    {Py_nb_xor,                 (binaryfunc)Generic_set_xor},
    {Py_nb_or,                  bucket_or},
    {Py_nb_inplace_subtract,    (binaryfunc)TreeSet_isub},
    {Py_nb_inplace_and,         (binaryfunc)TreeSet_iand},
    {Py_nb_inplace_xor,         (binaryfunc)TreeSet_ixor},
    {Py_nb_inplace_or,          (binaryfunc)TreeSet_ior},
    {Py_sq_contains,            (objobjproc)BTree_contains},
    {Py_mp_length,              (lenfunc)BTree_length},
    {0,                         NULL}
};

static PyType_Spec TreeSet_type_spec = {
    .name                       = TreeSet__name__,
    .basicsize                  = sizeof(BTree),
    .flags                      = Py_TPFLAGS_DEFAULT |
                                  Py_TPFLAGS_HAVE_GC |
                                  Py_TPFLAGS_IMMUTABLETYPE |
                                  Py_TPFLAGS_BASETYPE,
    .slots                      = TreeSet_type_slots
};

#endif
