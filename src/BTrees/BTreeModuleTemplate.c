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
/* include structmember.h for offsetof */
#include "structmember.h"
#include "bytesobject.h"

#ifdef PERSISTENT
#include "persistent/cPersistence.h"
#else
#define PER_USE_OR_RETURN(self, NULL)
#define PER_ALLOW_DEACTIVATION(self)
#define PER_PREVENT_DEACTIVATION(self)
#define PER_DEL(self)
#define PER_USE(O) 1
#define PER_ACCESSED(O) 1
#endif

#include "_compat.h"

/* So sue me.  This pair gets used all over the place, so much so that it
 * interferes with understanding non-persistence parts of algorithms.
 * PER_UNUSE can be used after a successul PER_USE or PER_USE_OR_RETURN.
 * It allows the object to become ghostified, and tells the persistence
 * machinery that the object's fields were used recently.
 */
#define PER_UNUSE(OBJ) do {             \
    PER_ALLOW_DEACTIVATION(OBJ);        \
    PER_ACCESSED(OBJ);                  \
} while (0)

/* The tp_name slots of the various BTree types contain the fully
 * qualified names of the types, e.g. zodb.btrees.OOBTree.OOBTree.
 * The full name is usd to support pickling and because it is not
 * possible to modify the __module__ slot of a type dynamically.  (This
 * may be a bug in Python 2.2).
 *
 * The MODULE_NAME here used to be "BTrees._".  We actually want the module
 * name to point to the Python module rather than the C, so the underline
 * is now removed.
 */
#define MODULE_NAME "BTrees." MOD_NAME_PREFIX "BTree."

static PyObject *sort_str, *reverse_str, *__setstate___str;
static PyObject *_bucket_type_str, *max_internal_size_str, *max_leaf_size_str;
static PyObject *__slotnames__str;
static PyObject *ConflictError = NULL;

static void PyVar_Assign(PyObject **v, PyObject *e) { Py_XDECREF(*v); *v=e;}
#define ASSIGN(V,E) PyVar_Assign(&(V),(E))
#define UNLESS(E) if (!(E))
#define OBJECT(O) ((PyObject*)(O))

#define MIN_BUCKET_ALLOC 16

#define SameType_Check(O1, O2) (Py_TYPE((O1))==Py_TYPE((O2)))

#define ASSERT(C, S, R) if (! (C)) { \
  PyErr_SetString(PyExc_AssertionError, (S)); return (R); }


#ifdef NEED_LONG_LONG_SUPPORT
/* Helper code used to support long long instead of int. */

#ifndef PY_LONG_LONG
#error "PY_LONG_LONG required but not defined"
#endif

static int
longlong_handle_overflow(PY_LONG_LONG result, int overflow)
{
    if (overflow)
    {
        PyErr_Clear();
        /* Python 3 tends to have an exception already set.
           We want to consistently raise a TypeError.
        */
        PyErr_SetString(PyExc_TypeError, "couldn't convert integer to C long long");
        return 0;
    }
    else if (result == -1 && PyErr_Occurred())
        /* An exception has already been raised. */
        return 0;
    return 1;
}


#ifdef NEED_LONG_LONG_KEYS

#if defined(ZODB_UNSIGNED_VALUE_INTS) || defined(ZODB_UNSIGNED_KEY_INTS)
static int
ulonglong_check(PyObject *ob)
{
    if (!PyLong_Check(ob))
    {
        return 0;
    }

    if (PyLong_AsUnsignedLongLong(ob) == (unsigned long long)-1 && PyErr_Occurred())
    {
        return 0;
    }
    return 1;
}
#endif /* defined(ZODB_UNSIGNED_VALUE_INTS) || defined(ZODB_UNSIGNED_KEY_INTS) */

static int
longlong_check(PyObject *ob)
{
    if (PyLong_Check(ob)) {
        int overflow;
        PY_LONG_LONG result;
        result = PyLong_AsLongLongAndOverflow(ob, &overflow);
        return longlong_handle_overflow(result, overflow);
    }
    return 0;
}

#endif

#if defined(ZODB_UNSIGNED_VALUE_INTS) || defined(ZODB_UNSIGNED_KEY_INTS)
static PyObject *
ulonglong_as_object(unsigned PY_LONG_LONG val)
{
    if ((val > LONG_MAX))
        return PyLong_FromUnsignedLongLong(val);
    return UINT_FROM_LONG((unsigned long)val);
}

static int
ulonglong_convert(PyObject *ob, unsigned PY_LONG_LONG *value)
{
    unsigned PY_LONG_LONG val;

    if (!PyLong_Check(ob))
    {
        PyErr_SetString(PyExc_TypeError, "expected integer key");
        return 0;
    }

    val = PyLong_AsUnsignedLongLong(ob);
    if (val == (unsigned long long)-1 && PyErr_Occurred())
    {
        if (PyErr_ExceptionMatches(PyExc_OverflowError))
        {
            PyErr_Clear();
            PyErr_SetString(PyExc_TypeError, "overflow error converting int to C long long");
        }
        return 0;
    }
    (*value) = val;
    return 1;
}
#endif /* defined(ZODB_UNSIGNED_VALUE_INTS) || defined(ZODB_UNSIGNED_KEY_INTS) */

static PyObject *
longlong_as_object(PY_LONG_LONG val)
{
    if ((val > LONG_MAX) || (val < LONG_MIN))
        return PyLong_FromLongLong(val);
    return INT_FROM_LONG((long)val);
}

static int
longlong_convert(PyObject *ob, PY_LONG_LONG *value)
{
    PY_LONG_LONG val;
    int overflow;

    if (!PyLong_Check(ob))
    {
        PyErr_SetString(PyExc_TypeError, "expected integer key");
        return 0;
    }
    val = PyLong_AsLongLongAndOverflow(ob, &overflow);
    if (!longlong_handle_overflow(val, overflow))
    {
        return 0;
    }
    (*value) = val;
    return 1;
}

#endif  /* NEED_LONG_LONG_SUPPORT */


/* Various kinds of BTree and Bucket structs are instances of
 * "sized containers", and have a common initial layout:
 *     The stuff needed for all Python objects, or all Persistent objects.
 *     int size:  The maximum number of things that could be contained
 *                without growing the container.
 *     int len:   The number of things currently contained.
 *
 * Invariant:  0 <= len <= size.
 *
 * A sized container typically goes on to declare one or more pointers
 * to contiguous arrays with 'size' elements each, the initial 'len' of
 * which are currently in use.
 */
#ifdef PERSISTENT
#define sizedcontainer_HEAD         \
    cPersistent_HEAD                \
    int size;                       \
    int len;
#else
#define sizedcontainer_HEAD         \
    PyObject_HEAD                   \
    int size;                       \
    int len;
#endif

/* Nothing is actually of type Sized, but (pointers to) BTree nodes and
 * Buckets can be cast to Sized* in contexts that only need to examine
 * the members common to all sized containers.
 */
typedef struct Sized_s {
    sizedcontainer_HEAD
} Sized;

#define SIZED(O) ((Sized*)(O))

/* A Bucket wraps contiguous vectors of keys and values.  Keys are unique,
 * and stored in sorted order.  The 'values' pointer may be NULL if the
 * Bucket is used to implement a set.  Buckets serving as leafs of BTrees
 * are chained together via 'next', so that the entire BTree contents
 * can be traversed in sorted order quickly and easily.
 */
typedef struct Bucket_s {
  sizedcontainer_HEAD
  struct Bucket_s *next;    /* the bucket with the next-larger keys */
  KEY_TYPE *keys;           /* 'len' keys, in increasing order */
  VALUE_TYPE *values;       /* 'len' corresponding values; NULL if a set */
} Bucket;

#define BUCKET(O) ((Bucket*)(O))

/* A BTree is complicated.  See Maintainer.txt.
 */

typedef struct BTreeItem_s {
  KEY_TYPE key;
  Sized *child; /* points to another BTree, or to a Bucket of some sort */
} BTreeItem;

typedef struct BTree_s {
  sizedcontainer_HEAD

  /* firstbucket points to the bucket containing the smallest key in
   * the BTree.  This is found by traversing leftmost child pointers
   * (data[0].child) until reaching a Bucket.
   */
  Bucket *firstbucket;

  /* The BTree points to 'len' children, via the "child" fields of the data
   * array.  There are len-1 keys in the 'key' fields, stored in increasing
   * order.  data[0].key is unused.  For i in 0 .. len-1, all keys reachable
   * from data[i].child are >= data[i].key and < data[i+1].key, at the
   * endpoints pretending that data[0].key is minus infinity and
   * data[len].key is positive infinity.
   */
  BTreeItem *data;
  long max_internal_size;
  long max_leaf_size;
} BTree;

static PyTypeObject BTreeTypeType;
static PyTypeObject BTreeType;
static PyTypeObject BucketType;

#define BTREE(O) ((BTree*)(O))

/* Use BTREE_SEARCH to find which child pointer to follow.
 * RESULT   An int lvalue to hold the index i such that SELF->data[i].child
 *          is the correct node to search next.
 * SELF     A pointer to a BTree node.
 * KEY      The key you're looking for, of type KEY_TYPE.
 * ONERROR  What to do if key comparison raises an exception; for example,
 *          perhaps 'return NULL'.
 *
 * See Maintainer.txt for discussion:  this is optimized in subtle ways.
 * It's recommended that you call this at the start of a routine, waiting
 * to check for self->len == 0 after.
 */
#define BTREE_SEARCH(RESULT, SELF, KEY, ONERROR) {          \
    int _lo = 0;                                            \
    int _hi = (SELF)->len;                                  \
    int _i, _cmp;                                           \
    for (_i = _hi >> 1; _i > _lo; _i = (_lo + _hi) >> 1) {  \
        TEST_KEY_SET_OR(_cmp, (SELF)->data[_i].key, (KEY))  \
            ONERROR;                                        \
        if      (_cmp < 0) _lo = _i;                        \
        else if (_cmp > 0) _hi = _i;                        \
        else   /* equal */ break;                           \
    }                                                       \
    (RESULT) = _i;                                          \
}

/* SetIteration structs are used in the internal set iteration protocol.
 * When you want to iterate over a set or bucket or BTree (even an
 * individual key!),
 * 1. Declare a new iterator:
 *        SetIteration si = {0,0,0};
 *    Using "{0,0,0}" or "{0,0}" appear most common.  Only one {0} is
 *    necssary.  At least one must be given so that finiSetIteration() works
 *    correctly even if you don't get around to calling initSetIteration().
 * 2. Initialize it via
 *        initSetIteration(&si, PyObject *s, useValues)
 *    It's an error if that returns an int < 0.  In case of error on the
 *    init call, calling finiSetIteration(&si) is optional.  But if the
 *    init call succeeds, you must eventually call finiSetIteration(),
 *    and whether or not subsequent calls to si.next() fail.
 * 3. Get the first element:
 *        if (si.next(&si) < 0) { there was an error }
 *    If the set isn't empty, this sets si.position to an int >= 0,
 *    si.key to the element's key (of type KEY_TYPE), and maybe si.value to
 *    the element's value (of type VALUE_TYPE).  si.value is defined
 *    iff si.usesValue is true.
 * 4. Process all the elements:
 *        while (si.position >= 0) {
 *            do something with si.key and/or si.value;
 *            if (si.next(&si) < 0) { there was an error; }
 *        }
 * 5. Finalize the SetIterator:
 *        finiSetIteration(&si);
 *    This is mandatory!  si may contain references to iterator objects,
 *    keys and values, and they must be cleaned up else they'll leak.  If
 *    this were C++ we'd hide that in the destructor, but in C you have to
 *    do it by hand.
 */
typedef struct SetIteration_s
{
  PyObject *set;    /* the set, bucket, BTree, ..., being iterated */
  int position;     /* initialized to 0; set to -1 by next() when done */
  int usesValue;    /* true iff 'set' has values & we iterate them */
  KEY_TYPE key;     /* next() sets to next key */
  VALUE_TYPE value; /* next() may set to next value */
  int (*next)(struct SetIteration_s*);  /* function to get next key+value */
} SetIteration;

/* Finish the set iteration protocol.  This MUST be called by everyone
 * who starts a set iteration, unless the initial call to initSetIteration
 * failed; in that case, and only that case, calling finiSetIteration is
 * optional.
 */
static void
finiSetIteration(SetIteration *i)
{
    assert(i != NULL);
    if (i->set == NULL)
        return;
    Py_DECREF(i->set);
    i->set = NULL;      /* so it doesn't hurt to call this again */

    if (i->position > 0) {
        /* next() was called at least once, but didn't finish iterating
         * (else position would be negative).  So the cached key and
         * value need to be cleaned up.
         */
        DECREF_KEY(i->key);
        if (i->usesValue) {
            DECREF_VALUE(i->value);
        }
    }
    i->position = -1;   /* stop any stray next calls from doing harm */
}

static PyObject *
IndexError(int i)
{
    PyObject *v;

    v = INT_FROM_LONG(i);
    if (!v) {
        v = Py_None;
        Py_INCREF(v);
    }
    PyErr_SetObject(PyExc_IndexError, v);
    Py_DECREF(v);
    return NULL;
}

/* Search for the bucket immediately preceding *current, in the bucket chain
 * starting at first.  current, *current and first must not be NULL.
 *
 * Return:
 *     1    *current holds the correct bucket; this is a borrowed reference
 *     0    no such bucket exists; *current unaltered
 *    -1    error; *current unaltered
 */
static int
PreviousBucket(Bucket **current, Bucket *first)
{
    Bucket *trailing = NULL;    /* first travels; trailing follows it */
    int result = 0;

    assert(current && *current && first);
    if (first == *current)
        return 0;

    do {
        trailing = first;
        PER_USE_OR_RETURN(first, -1);
        first = first->next;

        ((trailing)->state==cPersistent_STICKY_STATE
        &&
        ((trailing)->state=cPersistent_UPTODATE_STATE));

        PER_ACCESSED(trailing);

        if (first == *current) {
            *current = trailing;
            result = 1;
            break;
        }
    } while (first);

    return result;
}

static void *
BTree_Malloc(size_t sz)
{
    void *r;

    ASSERT(sz > 0, "non-positive size malloc", NULL);

    r = malloc(sz);
    if (r)
        return r;

    PyErr_NoMemory();
    return NULL;
}

static void *
BTree_Realloc(void *p, size_t sz)
{
    void *r;

    ASSERT(sz > 0, "non-positive size realloc", NULL);

    if (p)
        r = realloc(p, sz);
    else
        r = malloc(sz);

    UNLESS (r)
        PyErr_NoMemory();

    return r;
}

/* Shared keyword-argument list for BTree/Bucket
 * (iter)?(keys|values|items)
 */
static char *search_keywords[] = {"min", "max",
                                  "excludemin", "excludemax",
                                  0};

/**
 * Call this instead of using `PyErr_ExceptionMatches(PyExc_KeyError)`
 * when you intend to suppress the KeyError.
 *
 * We want to match only exactly ``PyExc_KeyError``, and not subclasses
 * such as ``ZODB.POSException.POSKeyError``.
 */
static int
BTree_ShouldSuppressKeyError()
{
    PyObject* exc_type = PyErr_Occurred(); /* Returns borrowed reference. */
    if (exc_type && exc_type == PyExc_KeyError) {
        return 1;
    }
    return 0;
}

#include "BTreeItemsTemplate.c"
#include "BucketTemplate.c"
#include "SetTemplate.c"
#include "BTreeTemplate.c"
#include "TreeSetTemplate.c"
#include "SetOpTemplate.c"
#include "MergeTemplate.c"

static struct PyMethodDef module_methods[] = {
  {"difference", (PyCFunction) difference_m,    METH_VARARGS,
   "difference(o1, o2)\n"
   "compute the difference between o1 and o2"
  },
  {"union", (PyCFunction) union_m,      METH_VARARGS,
   "union(o1, o2)\ncompute the union of o1 and o2\n"
  },
  {"intersection", (PyCFunction) intersection_m,        METH_VARARGS,
   "intersection(o1, o2)\n"
   "compute the intersection of o1 and o2"
  },
#ifdef MERGE
  {"weightedUnion", (PyCFunction) wunion_m,     METH_VARARGS,
   "weightedUnion(o1, o2 [, w1, w2])\ncompute the union of o1 and o2\n"
   "\nw1 and w2 are weights."
  },
  {"weightedIntersection", (PyCFunction) wintersection_m,       METH_VARARGS,
   "weightedIntersection(o1, o2 [, w1, w2])\n"
   "compute the intersection of o1 and o2\n"
   "\nw1 and w2 are weights."
  },
#endif
#ifdef MULTI_INT_UNION
  {"multiunion", (PyCFunction) multiunion_m, METH_VARARGS,
   "multiunion(seq)\ncompute union of a sequence of integer sets.\n"
   "\n"
   "Each element of seq must be an integer set, or convertible to one\n"
   "via the set iteration protocol.  The union returned is an IISet."
  },
#endif
  {NULL,                NULL}           /* sentinel */
};

static char BTree_module_documentation[] =
"\n"
MASTER_ID
BTREEITEMSTEMPLATE_C
"$Id$\n"
BTREETEMPLATE_C
BUCKETTEMPLATE_C
KEYMACROS_H
MERGETEMPLATE_C
SETOPTEMPLATE_C
SETTEMPLATE_C
TREESETTEMPLATE_C
VALUEMACROS_H
BTREEITEMSTEMPLATE_C
;

static int
init_type_with_meta_base(PyTypeObject *type, PyTypeObject* meta, PyTypeObject* base)
{
    int result;
    PyObject* slotnames;
    ((PyObject*)type)->ob_type = meta;
    type->tp_base = base;

    if (PyType_Ready(type) < 0)
        return 0;
    /*
      persistent looks for __slotnames__ in the dict at deactivation time,
      and if it's not present, calls ``copyreg._slotnames``, which itself
      looks in the dict again. Then it does some computation, and tries to
      store the object in the dict --- which for built-in types, it can't.
      So we can save some runtime if we store an empty slotnames for these classes.
    */
    slotnames = PyTuple_New(0);
    if (!slotnames) {
        return 0;
    }
    result = PyDict_SetItem(type->tp_dict, __slotnames__str, slotnames);
    Py_DECREF(slotnames);
    return result < 0 ? 0 : 1;
}

int /* why isn't this static? */
init_persist_type(PyTypeObject* type)
{
    return init_type_with_meta_base(type, &PyType_Type, cPersistenceCAPI->pertype);
}

static int init_tree_type(PyTypeObject* type, PyTypeObject* bucket_type)
{
    if (!init_type_with_meta_base(type, &BTreeTypeType, cPersistenceCAPI->pertype)) {
        return 0;
    }
    if (PyDict_SetItem(type->tp_dict, _bucket_type_str, (PyObject*)bucket_type) < 0) {
        return 0;
    }
    return 1;
}

static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "_" MOD_NAME_PREFIX "BTree",    /* m_name */
        BTree_module_documentation,     /* m_doc */
        -1,                             /* m_size */
        module_methods,                 /* m_methods */
        NULL,                           /* m_reload */
        NULL,                           /* m_traverse */
        NULL,                           /* m_clear */
        NULL,                           /* m_free */
    };

static PyObject*
module_init(void)
{
    PyObject *module, *mod_dict, *interfaces, *conflicterr;

#ifdef KEY_TYPE_IS_PYOBJECT
    object_ = PyTuple_GetItem(Py_TYPE(Py_None)->tp_bases, 0);
    if (object_ == NULL)
      return NULL;
#endif

    sort_str = INTERN("sort");
    if (!sort_str)
        return NULL;
    reverse_str = INTERN("reverse");
    if (!reverse_str)
        return NULL;
    __setstate___str = INTERN("__setstate__");
    if (!__setstate___str)
        return NULL;
    _bucket_type_str = INTERN("_bucket_type");
    if (!_bucket_type_str)
        return NULL;

    max_internal_size_str = INTERN("max_internal_size");
    if (! max_internal_size_str)
        return NULL;
    max_leaf_size_str = INTERN("max_leaf_size");
    if (! max_leaf_size_str)
        return NULL;
    __slotnames__str = INTERN("__slotnames__");
    if (!__slotnames__str)
        return NULL;

    BTreeType_setattro_allowed_names = PyTuple_Pack(
        5,
        /* BTree attributes  */
        max_internal_size_str,
        max_leaf_size_str,
        /* zope.interface attributes */
        /*
          Technically, INTERNING directly here leaks references,
          but since we can't be unloaded, it's not a problem.
        */
        INTERN("__implemented__"),
        INTERN("__providedBy__"),
        INTERN("__provides__")
    );

    /* Grab the ConflictError class */
    interfaces = PyImport_ImportModule("BTrees.Interfaces");
    if (interfaces != NULL)
    {
        conflicterr = PyObject_GetAttrString(interfaces, "BTreesConflictError");
        if (conflicterr != NULL)
            ConflictError = conflicterr;
        Py_DECREF(interfaces);
    }

    if (ConflictError == NULL)
    {
        Py_INCREF(PyExc_ValueError);
        ConflictError=PyExc_ValueError;
    }

    /* Initialize the PyPersist_C_API and the type objects. */
    cPersistenceCAPI = (cPersistenceCAPIstruct *)PyCapsule_Import(
                "persistent.cPersistence.CAPI", 0);
    if (cPersistenceCAPI == NULL) {
       /* The Capsule API attempts to import 'persistent' and then
        * walk down to the specified attribute using getattr. If the C
        * extensions aren't available, this can result in an
        * AttributeError being raised. Let that percolate up as an
        * ImportError so it can be caught in the expected way.
        */
       if (PyErr_Occurred() && !PyErr_ExceptionMatches(PyExc_ImportError)) {
           PyErr_SetString(PyExc_ImportError, "persistent C extension unavailable");
       }
        return NULL;
   }

#define _SET_TYPE(typ) ((PyObject*)(&typ))->ob_type = &PyType_Type
    _SET_TYPE(BTreeItemsType);
    _SET_TYPE(BTreeIter_Type);
    BTreeIter_Type.tp_getattro = PyObject_GenericGetAttr;
    BucketType.tp_new = PyType_GenericNew;
    SetType.tp_new = PyType_GenericNew;
    BTreeType.tp_new = PyType_GenericNew;
    TreeSetType.tp_new = PyType_GenericNew;

    if (!init_persist_type(&BucketType))
            return NULL;

    if (!init_type_with_meta_base(&BTreeTypeType, &PyType_Type, &PyType_Type)) {
        return NULL;
    }

    if (!init_tree_type(&BTreeType, &BucketType)) {
        return NULL;
    }

    if (!init_persist_type(&SetType))
        return NULL;

    if (!init_tree_type(&TreeSetType, &SetType)) {
        return NULL;
    }

    /* Create the module and add the functions */
    module = PyModule_Create(&moduledef);

    /* Add some symbolic constants to the module */
    mod_dict = PyModule_GetDict(module);

    if (PyDict_SetItemString(mod_dict, MOD_NAME_PREFIX "Bucket",
                             (PyObject *)&BucketType) < 0)
        return NULL;
    if (PyDict_SetItemString(mod_dict, MOD_NAME_PREFIX "BTree",
                             (PyObject *)&BTreeType) < 0)
        return NULL;
    if (PyDict_SetItemString(mod_dict, MOD_NAME_PREFIX "Set",
                             (PyObject *)&SetType) < 0)
        return NULL;
    if (PyDict_SetItemString(mod_dict, MOD_NAME_PREFIX "TreeSet",
                             (PyObject *)&TreeSetType) < 0)
        return NULL;
    if (PyDict_SetItemString(mod_dict, MOD_NAME_PREFIX "TreeIterator",
                             (PyObject *)&BTreeIter_Type) < 0)
        return NULL;
        /* We also want to be able to access these constants without the prefix
         * so that code can more easily exchange modules (particularly the integer
         * and long modules, but also others).  The TreeIterator is only internal,
         * so we don't bother to expose that.
     */
    if (PyDict_SetItemString(mod_dict, "Bucket",
                             (PyObject *)&BucketType) < 0)
        return NULL;
    if (PyDict_SetItemString(mod_dict, "BTree",
                             (PyObject *)&BTreeType) < 0)
        return NULL;
    if (PyDict_SetItemString(mod_dict, "Set",
                             (PyObject *)&SetType) < 0)
        return NULL;
    if (PyDict_SetItemString(mod_dict, "TreeSet",
                             (PyObject *)&TreeSetType) < 0)
        return NULL;
    if (PyDict_SetItemString(mod_dict, "TreeItems",
                             (PyObject *)&BTreeItemsType) < 0)
        return NULL;
#if defined(ZODB_64BIT_INTS) && defined(NEED_LONG_LONG_SUPPORT)
    if (PyDict_SetItemString(mod_dict, "using64bits", Py_True) < 0)
        return NULL;
#else
    if (PyDict_SetItemString(mod_dict, "using64bits", Py_False) < 0)
        return NULL;
#endif
    return module;
}

PyMODINIT_FUNC INITMODULE(void)
{
    return module_init();
}
