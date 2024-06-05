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

#define BTREEITEMSTEMPLATE_C "$Id$\n"

/* A BTreeItems struct is returned from calling .items(), .keys() or
 * .values() on a BTree-based data structure, and is also the result of
 * taking slices of those.  It represents a contiguous slice of a BTree.
 *
 * The start of the slice is in firstbucket, at offset first.  The end of
 * the slice is in lastbucket, at offset last.  Both endpoints are inclusive.
 * It must possible to get from firstbucket to lastbucket via following
 * bucket 'next' pointers zero or more times.  firstbucket, first, lastbucket,
 * and last are readonly after initialization.  An empty slice is represented
 * by  firstbucket == lastbucket == currentbucket == NULL.
 *
 * 'kind' determines whether this slice represents 'k'eys alone, 'v'alues
 * alone, or 'i'items (key+value pairs).  'kind' is also readonly after
 * initialization.
 *
 * The combination of currentbucket, currentoffset and pseudoindex acts as
 * a search finger.  Offset currentoffset in bucket currentbucket is at index
 * pseudoindex, where pseudoindex==0 corresponds to offset first in bucket
 * firstbucket, and pseudoindex==-1 corresponds to offset last in bucket
 * lastbucket.  The function BTreeItems_seek() can be used to set this combo
 * correctly for any in-bounds index, and uses this combo on input to avoid
 * needing to search from the start (or end) on each call.  Calling
 * BTreeItems_seek() with consecutive larger positions is very efficent.
 * Calling it with consecutive smaller positions is more efficient than if
 * a search finger weren't being used at all, but is still quadratic time
 * in the number of buckets in the slice.
 */
typedef struct
{
    PyObject_HEAD
    Bucket *firstbucket;    /* First bucket                    */
    Bucket *currentbucket;  /* Current bucket (search finger) */
    Bucket *lastbucket;     /* Last bucket                    */
    int currentoffset;      /* Offset in currentbucket        */
    int pseudoindex;        /* search finger index            */
    int first;              /* Start offset in firstbucket    */
    int last;               /* End offset in lastbucket       */
    char kind;              /* 'k', 'v', 'i'                  */
} BTreeItems;

#define ITEMS(O)((BTreeItems*)(O))

static PyObject *
newBTreeItems(PyObject* module, char kind,
              Bucket *lowbucket, int lowoffset,
              Bucket *highbucket, int highoffset
              );

static void
BTreeItems_dealloc(BTreeItems *self)
{
    PyObject* obj_self = (PyObject*)self;
    PyTypeObject* tp = Py_TYPE(self);
#if USE_HEAP_ALLOCATED_TYPES
    PyObject_GC_UnTrack(obj_self);
#endif
    Py_CLEAR(self->firstbucket);
    Py_CLEAR(self->lastbucket);
    Py_CLEAR(self->currentbucket);
    tp->tp_free(obj_self);
#if USE_HEAP_ALLOCATED_TYPES
    Py_DECREF(tp);
#endif
}

static Py_ssize_t
BTreeItems_length_or_nonzero(BTreeItems *self, int nonzero)
{
    PyObject* obj_self = (PyObject*)self;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    Py_ssize_t r;
    Bucket *b;
    Bucket *next;

    b = self->firstbucket;
    if (b == NULL)
        return 0;

    r = self->last + 1 - self->first;

    if (nonzero && r > 0)
    /* Short-circuit if all we care about is nonempty */
        return 1;

    if (b == self->lastbucket)
        return r;

    Py_INCREF(b);
    if (!per_use((cPersistentObject*)b, capi_struct))
        return -1;
    while ((next = b->next))
    {
        r += b->len;
        if (nonzero && r > 0)
            /* Short-circuit if all we care about is nonempty */
            break;

        if (next == self->lastbucket)
            break; /* we already counted the last bucket */

        Py_INCREF(next);
        per_allow_deactivation((cPersistentObject*)b);
        capi_struct->accessed((cPersistentObject*)b);
        Py_DECREF(b);
        b = next;
        if (!per_use((cPersistentObject*)b, capi_struct))
            return -1;
    }
    per_allow_deactivation((cPersistentObject*)b);
    capi_struct->accessed((cPersistentObject*)b);
    Py_DECREF(b);

    return r >= 0 ? r : 0;
}

static Py_ssize_t
BTreeItems_length(BTreeItems *self)
{
    return BTreeItems_length_or_nonzero(self, 0);
}

/*
** BTreeItems_seek
**
** Find the ith position in the BTreeItems.
**
** Arguments:      self    The BTree
**        i    the index to seek to, in 0 .. len(self)-1, or in
**                      -len(self) .. -1, as for indexing a Python sequence.
**
**
** Returns 0 if successful, -1 on failure to seek (like out-of-bounds).
** Upon successful return, index i is at offset self->currentoffset in bucket
** self->currentbucket.
*/
static int
BTreeItems_seek(BTreeItems *self, Py_ssize_t i)
{
    PyObject* obj_self = (PyObject*)self;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    Bucket *b;
    Bucket *currentbucket;
    int delta;
    int pseudoindex;
    int currentoffset;
    int error;

    pseudoindex = self->pseudoindex;
    currentoffset = self->currentoffset;
    currentbucket = self->currentbucket;
    if (currentbucket == NULL)
        goto no_match;

    delta = i - pseudoindex;
    while (delta > 0) /* move right */
    {
        int max;
        /* Want to move right delta positions; the most we can move right in
         * this bucket is currentbucket->len - currentoffset - 1 positions.
         */
        if (!per_use((cPersistentObject*)currentbucket, capi_struct))
            return -1;
        max = currentbucket->len - currentoffset - 1;
        b = currentbucket->next;
        per_allow_deactivation((cPersistentObject*)currentbucket);
        capi_struct->accessed((cPersistentObject*)currentbucket);
        if (delta <= max)
        {
            currentoffset += delta;
            pseudoindex += delta;
            if (currentbucket == self->lastbucket
                && currentoffset > self->last)
                goto no_match;
            break;
        }
        /* Move to start of next bucket. */
        if (currentbucket == self->lastbucket || b == NULL)
            goto no_match;
        currentbucket = b;
        pseudoindex += max + 1;
        delta -= max + 1;
        currentoffset = 0;
    }
    while (delta < 0) /* move left */
    {
        int status;
        /* Want to move left -delta positions; the most we can move left in
         * this bucket is currentoffset positions.
         */
        if ((-delta) <= currentoffset)
        {
            currentoffset += delta;
            pseudoindex += delta;
            if (currentbucket == self->firstbucket
                && currentoffset < self->first)
                goto no_match;
            break;
        }
        /* Move to end of previous bucket. */
        if (currentbucket == self->firstbucket)
            goto no_match;
        status = PreviousBucket(&currentbucket, self->firstbucket);
        if (status == 0)
            goto no_match;
        else if (status < 0)
            return -1;
        pseudoindex -= currentoffset + 1;
        delta += currentoffset + 1;
        if (!per_use((cPersistentObject*)currentbucket, capi_struct))
            return -1;
        currentoffset = currentbucket->len - 1;
        per_allow_deactivation((cPersistentObject*)currentbucket);
        capi_struct->accessed((cPersistentObject*)currentbucket);
    }

    assert(pseudoindex == i);

    /* Alas, the user may have mutated the bucket since the last time we
     * were called, and if they deleted stuff, we may be pointing into
     * trash memory now.
     */
    if (!per_use((cPersistentObject*)currentbucket, capi_struct))
        return -1;
    error = currentoffset < 0 || currentoffset >= currentbucket->len;
    per_allow_deactivation((cPersistentObject*)currentbucket);
    capi_struct->accessed((cPersistentObject*)currentbucket);
    if (error)
    {
        PyErr_SetString(PyExc_RuntimeError,
                        "the bucket being iterated changed size");
        return -1;
    }

    Py_INCREF(currentbucket);
    Py_DECREF(self->currentbucket);
    self->currentbucket = currentbucket;
    self->currentoffset = currentoffset;
    self->pseudoindex = pseudoindex;
    return 0;

no_match:
    IndexError(i);
    return -1;
}


/* Return the right kind ('k','v','i') of entry from bucket b at offset i.
 *  b must be activated.  Returns NULL on error.
 */
static PyObject *
getBucketEntry(Bucket *b, int i, char kind)
{
    PyObject *result = NULL;

    assert(b);
    assert(0 <= i && i < b->len);

    switch (kind)
    {
        case 'k':
            COPY_KEY_TO_OBJECT(result, b->keys[i]);
            break;

        case 'v':
            COPY_VALUE_TO_OBJECT(result, b->values[i]);
            break;

        case 'i':
        {
            PyObject *key;
            PyObject *value;;

            COPY_KEY_TO_OBJECT(key, b->keys[i]);
            if (!key)
                break;

            COPY_VALUE_TO_OBJECT(value, b->values[i]);
            if (!value)
            {
                Py_DECREF(key);
                break;
            }

            result = PyTuple_New(2);
            if (result)
            {
                PyTuple_SET_ITEM(result, 0, key);
                PyTuple_SET_ITEM(result, 1, value);
            }
            else
            {
                Py_DECREF(key);
                Py_DECREF(value);
            }
            break;
        }

        default:
            PyErr_SetString(PyExc_AssertionError,
                            "getBucketEntry: unknown kind");
            break;
    }
    return result;
}

/*
** BTreeItems_item
**
** Arguments:    self    a BTreeItems structure
**        i    Which item to inspect
**
** Returns:    the BTreeItems_item_BTree of self->kind, i
**        (ie pulls the ith item out)
*/
static PyObject *
BTreeItems_item(BTreeItems *self, Py_ssize_t i)
{
    PyObject* obj_self = (PyObject*)self;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    PyObject *result;

    if (BTreeItems_seek(self, i) < 0)
        return NULL;

    if (!per_use((cPersistentObject*)self->currentbucket, capi_struct))
        return NULL;
    result = getBucketEntry(self->currentbucket, self->currentoffset,
                            self->kind);
    per_allow_deactivation((cPersistentObject*)self->currentbucket);
    capi_struct->accessed((cPersistentObject*)self->currentbucket);
    return result;
}

/*
** BTreeItems_slice
**
** Creates a new BTreeItems structure representing the slice
** between the low and high range
**
** Arguments:    self    The old BTreeItems structure
**        ilow    The start index
**        ihigh    The end index
**
** Returns:    BTreeItems item
*/
static PyObject *
BTreeItems_slice(BTreeItems *self, Py_ssize_t ilow, Py_ssize_t ihigh)
{
    PyObject* obj_self = (PyObject*)self;
    Bucket *lowbucket;
    Bucket *highbucket;
    int lowoffset;
    int highoffset;
    Py_ssize_t length = -1;  /* len(self), but computed only if needed */

    PyObject* module = _get_module(Py_TYPE(obj_self));

    if (module == NULL) {
        PyErr_SetString(
            PyExc_RuntimeError, "BTreeItems_slice: module is NULL");
        return NULL;
    }

    /* Complications:
     * A Python slice never raises IndexError, but BTreeItems_seek does.
     * Python did only part of index normalization before calling this:
     *     ilow may be < 0 now, and ihigh may be arbitrarily large.  It's
     *     our responsibility to clip them.
     * A Python slice is exclusive of the high index, but a BTreeItems
     *     struct is inclusive on both ends.
     */

    /* First adjust ilow and ihigh to be legit endpoints in the Python
     * sense (ilow inclusive, ihigh exclusive).  This block duplicates the
     * logic from Python's list_slice function (slicing for builtin lists).
     */
    if (ilow < 0)
        ilow = 0;
    else
    {
        if (length < 0)
            length = BTreeItems_length(self);
        if (ilow > length)
            ilow = length;
    }

    if (ihigh < ilow)
        ihigh = ilow;
    else
    {
        if (length < 0)
            length = BTreeItems_length(self);
        if (ihigh > length)
            ihigh = length;
    }
    assert(0 <= ilow && ilow <= ihigh);
    assert(length < 0 || ihigh <= length);

    /* Now adjust for that our struct is inclusive on both ends.  This is
    * easy *except* when the slice is empty:  there's no good way to spell
    * that in an inclusive-on-both-ends scheme.  For example, if the
    * slice is btree.items([:0]), ilow == ihigh == 0 at this point, and if
    * we were to subtract 1 from ihigh that would get interpreted by
    * BTreeItems_seek as meaning the *entire* set of items.  Setting ilow==1
    * and ihigh==0 doesn't work either, as BTreeItems_seek raises IndexError
    * if we attempt to seek to ilow==1 when the underlying sequence is empty.
    * It seems simplest to deal with empty slices as a special case here.
    */
    if (ilow == ihigh) /* empty slice */
    {
        lowbucket = highbucket = NULL;
        lowoffset = 1;
        highoffset = 0;
    }
    else
    {
        assert(ilow < ihigh);
        --ihigh;  /* exclusive -> inclusive */

        if (BTreeItems_seek(self, ilow) < 0)
            return NULL;
        lowbucket = self->currentbucket;
        lowoffset = self->currentoffset;

        if (BTreeItems_seek(self, ihigh) < 0)
            return NULL;

        highbucket = self->currentbucket;
        highoffset = self->currentoffset;
    }
    return newBTreeItems(module, self->kind,
                         lowbucket, lowoffset,
                         highbucket, highoffset
                        );
}

static PyObject *
BTreeItems_subscript(BTreeItems *self, PyObject* subscript)
{
    Py_ssize_t len = BTreeItems_length_or_nonzero(self, 0);

    if (PyIndex_Check(subscript))
    {
        Py_ssize_t i = PyNumber_AsSsize_t(subscript, PyExc_IndexError);
        if (i == -1 && PyErr_Occurred())
            return NULL;
        if (i < 0)
            i += len;
        return BTreeItems_item(self, i);
    }
    if (PySlice_Check(subscript))
    {
        Py_ssize_t start, stop, step, slicelength;

#define SLICEOBJ(x) (x)

        if (PySlice_GetIndicesEx(SLICEOBJ(subscript), len,
                                 &start, &stop, &step, &slicelength) < 0)
        {
            return NULL;
        }

        if (step != 1)
        {
            PyErr_SetString(PyExc_RuntimeError,
                            "slices must have step size of 1");
            return NULL;
        }
        return BTreeItems_slice(self, start, stop);
    }
    PyErr_SetString(PyExc_RuntimeError,
                    "Unknown index type:  must be int or slice");
    return NULL;
}

static int
BTreeItems_nonzero(BTreeItems *self)
{
    return BTreeItems_length_or_nonzero(self, 1);
}

static char BTreeItems__name__[] = MODULE_NAME MOD_NAME_PREFIX "BTreeItems";
static char BTreeItems__doc__[] =
    "Sequence type used to iterate over BTree items.";


#if USE_STATIC_TYPES

static PyNumberMethods BTreeItems_as_number_for_nonzero = {
    .nb_bool                    = (inquiry)BTreeItems_nonzero,
};

static PySequenceMethods BTreeItems_as_sequence =
{
    .sq_length                  = (lenfunc) BTreeItems_length,
    .sq_item                    = (ssizeargfunc) BTreeItems_item,
};

/* Py3K doesn't honor sequence slicing, so implement via mapping */
static PyMappingMethods BTreeItems_as_mapping = {
    .mp_length                  = (lenfunc)BTreeItems_length,
    .mp_subscript               = (binaryfunc)BTreeItems_subscript,
};

static PyTypeObject BTreeItems_type_def = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name                    = BTreeItems__name__,
    .tp_doc                     = BTreeItems__doc__,
    .tp_basicsize               = sizeof(BTreeItems),
    .tp_flags                   = Py_TPFLAGS_DEFAULT,
    .tp_alloc                   = _pytype_generic_alloc,
    .tp_new                     = _pytype_generic_new,
    .tp_dealloc                 = (destructor)BTreeItems_dealloc,
    .tp_as_number               = &BTreeItems_as_number_for_nonzero,
    .tp_as_sequence             = &BTreeItems_as_sequence,
    .tp_as_mapping              = &BTreeItems_as_mapping,
};

#else

/* With static types, the BTreeItems type does not need to participate
 * in GC, but we *do* need to play right when allocating from the heap.
 */

static int
BTreeItems_traverse(BTreeItems *self, visitproc visit, void *arg)
{
    PyObject* obj_self = (PyObject*)self;
    PyTypeObject* tp = Py_TYPE(obj_self);
    Py_VISIT(tp);
    Py_VISIT((PyObject*)(self->firstbucket));
    Py_VISIT((PyObject*)(self->currentbucket));
    Py_VISIT((PyObject*)(self->lastbucket));

    return 0;
}

static int
BTreeItems_clear(BTreeItems *self)
{
    Py_CLEAR(self->firstbucket);
    Py_CLEAR(self->currentbucket);
    Py_CLEAR(self->lastbucket);

    return 0;
}

static PyType_Slot BTreeItems_type_slots[] = {
    {Py_tp_doc,                 BTreeItems__doc__},
    {Py_tp_alloc,               _pytype_generic_alloc},
    {Py_tp_new,                 _pytype_generic_new},
    {Py_tp_traverse,            (traverseproc)BTreeItems_traverse},
    {Py_tp_clear,               (inquiry)BTreeItems_clear},
    {Py_tp_dealloc,             (destructor)BTreeItems_dealloc},
    {Py_nb_bool,                (inquiry)BTreeItems_nonzero},
    {Py_sq_length,              (lenfunc)BTreeItems_length},
    {Py_sq_item,                (ssizeargfunc)BTreeItems_item},
    {Py_mp_length,              (lenfunc)BTreeItems_length},
    {Py_mp_subscript,           (binaryfunc)BTreeItems_subscript},
    {0,                         NULL}
};

static PyType_Spec BTreeItems_type_spec = {
    .name                       = BTreeItems__name__,
    .basicsize                  = sizeof(BTreeItems),
    .flags                      = Py_TPFLAGS_DEFAULT |
                                  Py_TPFLAGS_IMMUTABLETYPE |
                                  Py_TPFLAGS_HAVE_GC |
                                  Py_TPFLAGS_BASETYPE,
    .slots                      = BTreeItems_type_slots
};

#endif

/* Returns a new BTreeItems object representing the contiguous slice from
 * offset lowoffset in bucket lowbucket through offset highoffset in bucket
 * highbucket, inclusive.  Pass lowbucket == NULL for an empty slice.
 * The currentbucket is set to lowbucket, currentoffset ot lowoffset, and
 * pseudoindex to 0.  kind is 'k', 'v' or 'i' (see BTreeItems struct docs).
 */
static PyObject *
newBTreeItems(PyObject* module, char kind,
              Bucket *lowbucket, int lowoffset,
              Bucket *highbucket, int highoffset
             )
{
    if (module == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "newBTreeItems: module is NULL");
        return NULL;
    }
    PyTypeObject* btree_items_type = _get_btree_items_type(module);
    BTreeItems *self;

    self = (BTreeItems*)btree_items_type->tp_alloc(btree_items_type, 0);
    if (self == NULL)
        return NULL;

    self->kind=kind;

    self->first=lowoffset;
    self->last=highoffset;

    if (! lowbucket || ! highbucket
        || (lowbucket == highbucket && lowoffset > highoffset))
    {
        self->firstbucket   = 0;
        self->lastbucket    = 0;
        self->currentbucket = 0;
    }
    else
    {
        Py_INCREF(lowbucket);
        self->firstbucket = lowbucket;
        Py_INCREF(highbucket);
        self->lastbucket = highbucket;
        Py_INCREF(lowbucket);
        self->currentbucket = lowbucket;
    }

    self->currentoffset = lowoffset;
    self->pseudoindex = 0;

    return OBJECT(self);
}

static int
nextBTreeItems(SetIteration *i)
{
    PyObject* obj_self = i->set;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    if (i->position >= 0)
    {
        if (i->position)
        {
            DECREF_KEY(i->key);
            DECREF_VALUE(i->value);
        }

        if (BTreeItems_seek(ITEMS(i->set), i->position) >= 0)
        {
            Bucket *currentbucket;

            currentbucket = BUCKET(ITEMS(i->set)->currentbucket);
            UNLESS(per_use((cPersistentObject*)currentbucket, capi_struct))
            {
                /* Mark iteration terminated, so that finiSetIteration doesn't
                * try to redundantly decref the key and value
                */
                i->position = -1;
                return -1;
            }

            COPY_KEY(i->key, currentbucket->keys[ITEMS(i->set)->currentoffset]);
            INCREF_KEY(i->key);

            COPY_VALUE(i->value,
                        currentbucket->values[ITEMS(i->set)->currentoffset]);
            INCREF_VALUE(i->value);

            i->position ++;

            per_allow_deactivation((cPersistentObject*)currentbucket);
            capi_struct->accessed((cPersistentObject*)currentbucket);
        }
        else
        {
            i->position = -1;
            PyErr_Clear();
        }
    }
    return 0;
}

static int
nextTreeSetItems(SetIteration *i)
{
    PyObject* obj_self = i->set;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    if (i->position >= 0)
    {
        if (i->position)
        {
            DECREF_KEY(i->key);
        }

        if (BTreeItems_seek(ITEMS(i->set), i->position) >= 0)
        {
            Bucket *currentbucket;

            currentbucket = BUCKET(ITEMS(i->set)->currentbucket);
            UNLESS(per_use((cPersistentObject*)currentbucket, capi_struct))
            {
                /* Mark iteration terminated, so that finiSetIteration doesn't
                * try to redundantly decref the key and value
                */
                i->position = -1;
                return -1;
            }

            COPY_KEY(i->key, currentbucket->keys[ITEMS(i->set)->currentoffset]);
            INCREF_KEY(i->key);

            i->position ++;

            per_allow_deactivation((cPersistentObject*)currentbucket);
            capi_struct->accessed((cPersistentObject*)currentbucket);
        }
        else
        {
            i->position = -1;
            PyErr_Clear();
        }
    }
    return 0;
}

/* Support for the iteration protocol */

/* The type of iterator objects, returned by e.g. iter(IIBTree()). */
typedef struct
{
    PyObject_HEAD
    /* We use a BTreeItems object because it's convenient and flexible.
     * We abuse it two ways:
     *     1. We set currentbucket to NULL when the iteration is finished.
     *     2. We don't bother keeping pseudoindex in synch.
     */
    BTreeItems *pitems;
} BTreeIter;

/* Return a new iterator object, to traverse the keys and/or values
 * represented by pitems.  pitems must not be NULL.  Returns NULL if error.
 */
static BTreeIter *
newBTreeIter(PyObject* module, BTreeItems *pitems)
{
    PyTypeObject* btree_iter_type = _get_btree_iter_type(module);
    BTreeIter *result;

    assert(pitems != NULL);

    result = (BTreeIter*)btree_iter_type->tp_alloc(btree_iter_type, 0);

    if (result)
    {
        Py_INCREF(pitems);
        result->pitems = pitems;
    }
    return result;
}

/* The iterator's tp_dealloc slot. */
static void
BTreeIter_dealloc(BTreeIter *bi)
{
    PyObject* obj_self = (PyObject*)bi;
    PyTypeObject* tp = Py_TYPE(obj_self);
#if USE_HEAP_ALLOCATED_TYPES
    PyObject_GC_UnTrack(obj_self);
#endif
    Py_CLEAR(bi->pitems);
    tp->tp_free(obj_self);
#if USE_HEAP_ALLOCATED_TYPES
    Py_DECREF(tp);
#endif
}

/* The implementation of the iterator's tp_iternext slot.  Returns "the next"
 * item; returns NULL if error; returns NULL without setting an error if the
 * iteration is exhausted (that's the way to terminate the iteration protocol).
 */
static PyObject *
BTreeIter_next(BTreeIter *bi, PyObject *args)
{
    PyObject* obj_self = (PyObject*)bi;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    PyObject *result = NULL;        /* until proven innocent */
    BTreeItems *items = bi->pitems;
    int i = items->currentoffset;
    Bucket *bucket = items->currentbucket;

    if (bucket == NULL)    /* iteration termination is sticky */
        return NULL;

    if (!per_use((cPersistentObject*)bucket, capi_struct))
        return NULL;
    if (i >= bucket->len)
    {
        /* We never leave this routine normally with i >= len:  somebody
            * else mutated the current bucket.
            */
        PyErr_SetString(PyExc_RuntimeError,
                    "the bucket being iterated changed size");
        /* Arrange for that this error is sticky too. */
        items->currentoffset = INT_MAX;
        goto Done;
    }

    /* Build the result object, from bucket at offset i. */
    result = getBucketEntry(bucket, i, items->kind);

    /* Advance position for next call. */
    if (bucket == items->lastbucket && i >= items->last)
    {
        /* Next call should terminate the iteration. */
        Py_DECREF(items->currentbucket);
        items->currentbucket = NULL;
    }
    else
    {
        ++i;
        if (i >= bucket->len)
        {
            Py_XINCREF(bucket->next);
            items->currentbucket = bucket->next;
            Py_DECREF(bucket);
            i = 0;
        }
        items->currentoffset = i;
    }

Done:
    per_allow_deactivation((cPersistentObject*)bucket);
    capi_struct->accessed((cPersistentObject*)bucket);
    return result;
}

static PyObject *
BTreeIter_getiter(PyObject *it)
{
    Py_INCREF(it);
    return it;
}

static char BTreeIter__name__[] = MODULE_NAME MOD_NAME_PREFIX "TreeIterator";
static char BTreeIter__doc__[] = "Iterator for BTree items";

#if USE_STATIC_TYPES

static PyTypeObject BTreeIter_type_def = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name                    = BTreeIter__name__,
    .tp_doc                     = BTreeIter__doc__,
    .tp_basicsize               = sizeof(BTreeIter),
    .tp_flags                   = Py_TPFLAGS_DEFAULT,
    .tp_alloc                   = _pytype_generic_alloc,
    .tp_new                     = _pytype_generic_new,
    .tp_getattro                = _pyobject_generic_getattr,
    .tp_iter                    = (getiterfunc)BTreeIter_getiter,
    .tp_iternext                = (iternextfunc)BTreeIter_next,
    .tp_dealloc                 = (destructor)BTreeIter_dealloc,
};

#else

/* With static types, the BTreeIiter type does not need to participate
 * in GC, but we *do* need to play right when allocating from the heap.
 */

static int
BTreeIter_traverse(BTreeIter *self, visitproc visit, void *arg)
{
    PyObject* obj_self = (PyObject*)self;
    PyTypeObject* tp = Py_TYPE(obj_self);
    Py_VISIT(tp);
    Py_VISIT((PyObject*)(self->pitems));

    return 0;
}

static int
BTreeIter_clear(BTreeIter *self)
{
    Py_CLEAR(self->pitems);

    return 0;
}

static PyType_Slot BTreeIter_type_slots[] = {
    {Py_tp_doc,                 BTreeIter__doc__},
    {Py_tp_alloc,               _pytype_generic_alloc},
    {Py_tp_new,                 _pytype_generic_new},
    {Py_tp_getattro,            _pyobject_generic_getattr},
    {Py_tp_iter,                (getiterfunc)BTreeIter_getiter},
    {Py_tp_iternext,            (iternextfunc)BTreeIter_next},
    {Py_tp_traverse,            (traverseproc)BTreeIter_traverse},
    {Py_tp_clear,               (inquiry)BTreeIter_clear},
    {Py_tp_dealloc,             (destructor)BTreeIter_dealloc},
    {0,                         NULL}
};

static PyType_Spec BTreeIter_type_spec = {
    .name                       = BTreeIter__name__,
    .basicsize                  = sizeof(BTreeIter),
    .flags                      = Py_TPFLAGS_DEFAULT |
                                  Py_TPFLAGS_HAVE_GC |
                                  Py_TPFLAGS_IMMUTABLETYPE,
    .slots                      = BTreeIter_type_slots
};


#endif
