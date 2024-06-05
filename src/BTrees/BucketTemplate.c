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
#include "SetOpTemplate.h"

#define BUCKETTEMPLATE_C "$Id$\n"

/* Use BUCKET_SEARCH to find the index at which a key belongs.
 * INDEX    An int lvalue to hold the index i such that KEY belongs at
 *          SELF->keys[i].  Note that this will equal SELF->len if KEY
 *          is larger than the bucket's largest key.  Else it's the
 *          smallest i such that SELF->keys[i] >= KEY.
 * ABSENT   An int lvalue to hold a Boolean result, true (!= 0) if the
 *          key is absent, false (== 0) if the key is at INDEX.
 * SELF     A pointer to a Bucket node.
 * KEY      The key you're looking for, of type KEY_TYPE.
 * ONERROR  What to do if key comparison raises an exception; for example,
 *          perhaps 'return NULL'.
 *
 * See Maintainer.txt for discussion:  this is optimized in subtle ways.
 * It's recommended that you call this at the start of a routine, waiting
 * to check for self->len == 0 after (if an empty bucket is special in
 * context; INDEX becomes 0 and ABSENT becomes true if this macro is run
 * with an empty SELF, and that may be all the invoker needs to know).
 */
#define BUCKET_SEARCH(INDEX, ABSENT, SELF, KEY, ONERROR) {  \
    int _lo = 0;                                            \
    int _hi = (SELF)->len;                                  \
    int _i;                                                 \
    int _cmp = 1;                                           \
    for (_i = _hi >> 1; _lo < _hi; _i = (_lo + _hi) >> 1) { \
      TEST_KEY_SET_OR(_cmp, (SELF)->keys[_i], (KEY))        \
        ONERROR;                                            \
      if      (_cmp < 0)  _lo = _i + 1;                     \
      else if (_cmp == 0) break;                            \
      else                _hi = _i;                         \
    }                                                       \
    (INDEX) = _i;                                           \
    (ABSENT) = _cmp;                                        \
  }

/*
** _bucket_get
**
** Search a bucket for a given key.
**
** Arguments
**     self    The bucket
**     keyarg    The key to look for
**     has_key    Boolean; if true, return a true/false result; else return
**              the value associated with the key. When true, ignore the TypeError from
**              a key conversion issue, instead
**              transforming it into a KeyError.
**
** Return
**     If has_key:
**         Returns the Python int 0 if the key is absent, else returns
**         has_key itself as a Python int.  A BTree caller generally passes
**         the depth of the bucket for has_key, so a true result returns
**         the bucket depth then.
**         Note that has_key should be true when searching set buckets.
**     If not has_key:
**         If the key is present, returns the associated value, and the
**         caller owns the reference.  Else returns NULL and sets KeyError.
**     Whether or not has_key:
**         If a comparison sets an exception, returns NULL.
*/
static PyObject *
_bucket_get(Bucket *self, PyObject *keyarg, int has_key)
{
    PyObject* obj_self = (PyObject*)self;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    int i;
    int cmp;
    KEY_TYPE key;
    PyObject *r = NULL;
    int copied = 1;

    COPY_KEY_FROM_ARG(key, keyarg, copied);
    UNLESS (copied)
    {
        if (has_key && PyErr_ExceptionMatches(PyExc_TypeError))
        {
            PyErr_Clear();
            PyErr_SetObject(PyExc_KeyError, keyarg);
        }
        return NULL;
    }

    UNLESS (per_use((cPersistentObject*)self, capi_struct)) return NULL;

    BUCKET_SEARCH(i, cmp, self, key, goto Done);
    if (has_key)
        r = PyLong_FromLong(cmp ? 0 : has_key);
    else
    {
        if (cmp == 0)
        {
            COPY_VALUE_TO_OBJECT(r, self->values[i]);
        }
        else
            PyErr_SetObject(PyExc_KeyError, keyarg);
    }

Done:
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return r;
}

static PyObject *
bucket_getitem(Bucket *self, PyObject *key)
{
    PyObject* result;

    result = _bucket_get(self, key, 0);

    if (result == NULL && PyErr_ExceptionMatches(PyExc_TypeError))
    {
        PyErr_Clear();
        PyErr_SetObject(PyExc_KeyError, key);
    }

    return result;
}

/*
** Bucket_grow
**
** Resize a bucket.
**
** Arguments:   self    The bucket.
**              newsize The new maximum capacity.  If < 0, double the
**                      current size unless the bucket is currently empty,
**                      in which case use MIN_BUCKET_ALLOC.
**              noval   Boolean; if true, allocate only key space and not
**                      value space
**
** Returns:     -1      on error, and MemoryError exception is set
**               0      on success
*/
static int
Bucket_grow(Bucket *self, int newsize, int noval)
{
    KEY_TYPE *keys;
    VALUE_TYPE *values;

    if (self->size)
    {
        if (newsize < 0)
            newsize = self->size * 2;
        if (newsize < 0)    /* int overflow */
            goto Overflow;
        UNLESS (keys = BTree_Realloc(self->keys, sizeof(KEY_TYPE) * newsize))
            return -1;

        UNLESS (noval)
        {
            values = BTree_Realloc(self->values, sizeof(VALUE_TYPE) * newsize);
            if (values == NULL)
            {
                free(keys);
                return -1;
            }
            self->values = values;
        }
        self->keys = keys;
    }
    else
    {
        if (newsize < 0)
            newsize = MIN_BUCKET_ALLOC;
        UNLESS (self->keys = BTree_Malloc(sizeof(KEY_TYPE) * newsize))
            return -1;
        UNLESS (noval)
        {
            self->values = BTree_Malloc(sizeof(VALUE_TYPE) * newsize);
            if (self->values == NULL)
            {
                free(self->keys);
                self->keys = NULL;
                return -1;
            }
        }
    }
    self->size = newsize;
    return 0;

Overflow:
    PyErr_NoMemory();
    return -1;
}

/* So far, bucket_append is called only by multiunion_m(), so is called
 * only when MULTI_INT_UNION is defined.  Flavors of BTree/Bucket that
 * don't support MULTI_INT_UNION don't call bucket_append (yet), and
 * gcc complains if bucket_append is compiled in those cases.  So only
 * compile bucket_append if it's going to be used.
 */
#ifdef MULTI_INT_UNION
/*
 * Append a slice of the "from" bucket to self.
 *
 * self         Append (at least keys) to this bucket.  self must be activated
 *              upon entry, and remains activated at exit.  If copyValues
 *              is true, self must be empty or already have a non-NULL values
 *              pointer.  self's access and modification times aren't updated.
 * from         The bucket from which to take keys, and possibly values.  from
 *              must be activated upon entry, and remains activated at exit.
 *              If copyValues is true, from must have a non-NULL values
 *              pointer.  self and from must not be the same.  from's access
 *              time isn't updated.
 * i, n         The slice from[i : i+n] is appended to self.  Must have
 *              i >= 0, n > 0 and i+n <= from->len.
 * copyValues   Boolean.  If true, copy values from the slice as well as keys.
 *              In this case, from must have a non-NULL values pointer, and
 *              self must too (unless self is empty, in which case a values
 *              vector will be allocated for it).
 * overallocate Boolean.  If self doesn't have enough room upon entry to hold
 *              all the appended stuff, then if overallocate is false exactly
 *              enough room will be allocated to hold the new stuff, else if
 *              overallocate is true an excess will be allocated.  overallocate
 *              may be a good idea if you expect to append more stuff to self
 *              later; else overallocate should be false.
 *
 * CAUTION:  If self is empty upon entry (self->size == 0), and copyValues is
 * false, then no space for values will get allocated.  This can be a trap if
 * the caller intends to copy values itself.
 *
 * Return
 *    -1        Error.
 *     0        OK.
 */
static int
bucket_append(Bucket *self, Bucket *from, int i, int n,
              int copyValues, int overallocate)
{
    int newlen;

    assert(self && from && self != from);
    assert(i >= 0);
    assert(n > 0);
    assert(i+n <= from->len);

    /* Make room. */
    newlen = self->len + n;
    if (newlen > self->size)
    {
        int newsize = newlen;
        if (overallocate)   /* boost by 25% -- pretty arbitrary */
        newsize += newsize >> 2;
        if (Bucket_grow(self, newsize, ! copyValues) < 0)
        return -1;
    }
    assert(newlen <= self->size);

    /* Copy stuff. */
    memcpy(self->keys + self->len, from->keys + i, n * sizeof(KEY_TYPE));
    if (copyValues)
    {
        assert(self->values);
        assert(from->values);
        memcpy(self->values + self->len, from->values + i,
            n * sizeof(VALUE_TYPE));
    }
    self->len = newlen;

    /* Bump refcounts. */
#ifdef KEY_TYPE_IS_PYOBJECT
    {
        int j;
        PyObject **p = from->keys + i;
        for (j = 0; j < n; ++j, ++p)
        {
            Py_INCREF(*p);
        }
    }
#endif
#ifdef VALUE_TYPE_IS_PYOBJECT
    if (copyValues)
    {
        int j;
        PyObject **p = from->values + i;
        for (j = 0; j < n; ++j, ++p)
        {
            Py_INCREF(*p);
        }
    }
#endif
    return 0;
}
#endif /* MULTI_INT_UNION */

/*
** _bucket_set: Assign a value to a key in a bucket, delete a key+value
**  pair, or just insert a key.
**
** Arguments
**     self     The bucket
**     keyarg   The key to look for
**     v        The value to associate with key; NULL means delete the key.
**              If NULL, it's an error (KeyError) if the key isn't present.
**              Note that if this is a set bucket, and you want to insert
**              a new set element, v must be non-NULL although its exact
**              value will be ignored.  Passing Py_None is good for this.
**     unique   Boolean; when true, don't replace the value if the key is
**              already present.
**     noval    Boolean; when true, operate on keys only (ignore values)
**     changed  ignored on input
**
** Return
**     -1       on error
**      0       on success and the # of bucket entries didn't change
**      1       on success and the # of bucket entries did change
**  *changed    If non-NULL, set to 1 on any mutation of the bucket.
*/
static int
_bucket_set(Bucket *self, PyObject *keyarg, PyObject *v,
            int unique, int noval, int *changed)
{
    PyObject* obj_self = (PyObject*)self;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    int i, cmp;
    KEY_TYPE key;

    /* Subtle:  there may or may not be a value.  If there is, we need to
     * check its type early, so that in case of error we can get out before
     * mutating the bucket.  But because value isn't used on all paths, if
     * we don't initialize value then gcc gives a nuisance complaint that
     * value may be used initialized (it can't be, but gcc doesn't know
     * that).  So we initialize it.  However, VALUE_TYPE can be various types,
     * including int, PyObject*, and char[6], so it's a puzzle to spell
     * initialization.  It so happens that {0} is a valid initializer for all
     * these types.
     */
    VALUE_TYPE value = {0};    /* squash nuisance warning */
    int result = -1;    /* until proven innocent */
    int copied = 1;

    COPY_KEY_FROM_ARG(key, keyarg, copied);
    UNLESS(copied)
        return -1;
#ifdef KEY_CHECK_ON_SET
    if (v && !KEY_CHECK_ON_SET(keyarg))
        return -1;
#endif

    /* Copy the value early (if needed), so that in case of error a
     * pile of bucket mutations don't need to be undone.
     */
    if (v && !noval) {
        COPY_VALUE_FROM_ARG(value, v, copied);
        UNLESS(copied)
            return -1;
    }

    UNLESS (per_use((cPersistentObject*)self, capi_struct))
        return -1;

    BUCKET_SEARCH(i, cmp, self, key, goto Done);
    if (cmp == 0)
    {
        /* The key exists, at index i. */
        if (v)
        {
            /* The key exists at index i, and there's a new value.
             * If unique, we're not supposed to replace it.  If noval, or this
             * is a set bucket (self->values is NULL), there's nothing to do.
             */
            if (unique || noval || self->values == NULL)
            {
                result = 0;
                goto Done;
            }

            /* The key exists at index i, and we need to replace the value. */
#ifdef VALUE_SAME
            /* short-circuit if no change */
            if (VALUE_SAME(self->values[i], value))
            {
                result = 0;
                goto Done;
            }
#endif
            if (changed)
                *changed = 1;
            DECREF_VALUE(self->values[i]);
            COPY_VALUE(self->values[i], value);
            INCREF_VALUE(self->values[i]);
            if (capi_struct->changed((cPersistentObject*)self) >= 0)
                result = 0;
            goto Done;
        }

        /* The key exists at index i, and should be deleted. */
        DECREF_KEY(self->keys[i]);
        self->len--;
        if (i < self->len)
            memmove(self->keys + i, self->keys + i+1,
                    sizeof(KEY_TYPE)*(self->len - i));

        if (self->values)
        {
            DECREF_VALUE(self->values[i]);
            if (i < self->len)
                memmove(self->values + i, self->values + i+1,
                        sizeof(VALUE_TYPE)*(self->len - i));
        }

        if (! self->len)
        {
            self->size = 0;
            free(self->keys);
            self->keys = NULL;
            if (self->values)
            {
                free(self->values);
                self->values = NULL;
            }
        }

        if (changed)
            *changed = 1;
        if (capi_struct->changed((cPersistentObject*)self) >= 0)
            result = 1;
        goto Done;
    }

    /* The key doesn't exist, and belongs at index i. */
    if (!v)
    {
        /* Can't delete a non-existent key. */
        PyErr_SetObject(PyExc_KeyError, keyarg);
        goto Done;
    }

    /* The key doesn't exist and should be inserted at index i. */
    if (self->len == self->size && Bucket_grow(self, -1, noval) < 0)
        goto Done;

    if (self->len > i)
    {
        memmove(self->keys + i + 1, self->keys + i,
                sizeof(KEY_TYPE) * (self->len - i));
        if (self->values)
        {
            memmove(self->values + i + 1, self->values + i,
                    sizeof(VALUE_TYPE) * (self->len - i));
        }
    }

    COPY_KEY(self->keys[i], key);
    INCREF_KEY(self->keys[i]);

    if (! noval)
    {
        COPY_VALUE(self->values[i], value);
        INCREF_VALUE(self->values[i]);
    }

    self->len++;
    if (changed)
        *changed = 1;
    if (capi_struct->changed((cPersistentObject*)self) >= 0)
        result = 1;

Done:
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return result;
}

/*
** bucket_setitem
**
** wrapper for _bucket_set (eliminates +1 return code)
**
** Arguments:    self    The bucket
**        key    The key to insert under
**        v    The value to insert
**
** Returns     0     on success
**        -1    on failure
*/
static int
bucket_setitem(Bucket *self, PyObject *key, PyObject *v)
{
    if (_bucket_set(self, key, v, 0, 0, 0) < 0)
        return -1;
    return 0;
}

/**
 ** Accepts a sequence of 2-tuples, or any object with an items()
 ** method that returns an iterable object producing 2-tuples.
 */
static int
update_from_seq(PyObject *map, PyObject *seq)
{
    PyObject *iter, *o, *k, *v;
    int err = -1;

    /* One path creates a new seq object.  The other path has an
        INCREF of the seq argument.  So seq must always be DECREFed on
        the way out.
    */
    /* Use items() if it's not a sequence.  Alas, PySequence_Check()
     * returns true for a PeristentMapping or PersistentDict, and we
     * want to use items() in those cases too.
     */
    if (!PySequence_Check(seq) || /* or it "looks like a dict" */
        PyObject_HasAttrString(seq, "items"))
    {
        PyObject *items;
        items = PyObject_GetAttrString(seq, "items");
        if (items == NULL)
            return -1;
        seq = PyObject_CallObject(items, NULL);
        Py_DECREF(items);
        if (seq == NULL)
            return -1;
    }
    else
        Py_INCREF(seq);

    iter = PyObject_GetIter(seq);
    if (iter == NULL)
        goto err;
    while (1)
    {
        o = PyIter_Next(iter);
        if (o == NULL)
        {
            if (PyErr_Occurred())
                goto err;
            else
                break;
        }
        if (!PyTuple_Check(o) || PyTuple_GET_SIZE(o) != 2)
        {
            Py_DECREF(o);
            PyErr_SetString(PyExc_TypeError,
                        "Sequence must contain 2-item tuples");
            goto err;
        }
        k = PyTuple_GET_ITEM(o, 0);
        v = PyTuple_GET_ITEM(o, 1);
        if (PyObject_SetItem(map, k, v) < 0)
        {
            Py_DECREF(o);
            goto err;
        }
        Py_DECREF(o);
    }

    err = 0;
err:
    Py_DECREF(iter);
    Py_DECREF(seq);
    return err;
}

static PyObject *
Mapping_update(PyObject *self, PyObject *seq)
{
    if (update_from_seq(self, seq) < 0)
        return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}

/*
** bucket_split
**
** Splits one bucket into two
**
** Arguments:    self    The bucket
**        index    the index of the key to split at (O.O.B use midpoint)
**        next    the new bucket to split into
**
** Returns:     0    on success
**        -1    on failure
*/
static int
bucket_split(Bucket *self, int index, Bucket *next)
{
    PyObject* obj_self = (PyObject*)self;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    int next_size;

    ASSERT(self->len > 1, "split of empty bucket", -1);

    if (index < 0 || index >= self->len)
        index = self->len / 2;

    next_size = self->len - index;

    next->keys = BTree_Malloc(sizeof(KEY_TYPE) * next_size);
    if (!next->keys)
        return -1;
    memcpy(next->keys, self->keys + index, sizeof(KEY_TYPE) * next_size);
    if (self->values) {
        next->values = BTree_Malloc(sizeof(VALUE_TYPE) * next_size);
        if (!next->values) {
        free(next->keys);
        next->keys = NULL;
        return -1;
        }
        memcpy(next->values, self->values + index,
            sizeof(VALUE_TYPE) * next_size);
    }
    next->size = next_size;
    next->len = next_size;
    self->len = index;

    next->next = self->next;

    Py_INCREF(next);
    self->next = next;

    if (capi_struct->changed((cPersistentObject*)self) < 0)
        return -1;

    return 0;
}

/* Set self->next to self->next->next, i.e. unlink self's successor from
 * the chain.
 *
 * Return:
 *     -1       error
 *      0       OK
 */
static int
Bucket_deleteNextBucket(Bucket *self)
{
    PyObject* obj_self = (PyObject*)self;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    int result = -1;    /* until proven innocent */
    Bucket *successor;

    if (!per_use((cPersistentObject*)self, capi_struct))
        return -1;
    successor = self->next;
    if (successor)
    {
        Bucket *next;
        /* Before:  self -> successor -> next
        * After:   self --------------> next
        */
        UNLESS (per_use((cPersistentObject*)successor, capi_struct))
            goto Done;
        next = successor->next;
        per_allow_deactivation((cPersistentObject*)successor);
        capi_struct->accessed((cPersistentObject*)successor);

        Py_XINCREF(next);       /* it may be NULL, of course */
        self->next = next;
        Py_DECREF(successor);
        if (capi_struct->changed((cPersistentObject*)self) < 0)
            goto Done;
    }
    result = 0;

Done:
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return result;
}

/*
  Bucket_findRangeEnd -- Find the index of a range endpoint
  (possibly) contained in a bucket.

  Arguments:     self        The bucket
  keyarg      The key to match against
  low         Boolean; true for low end of range, false for high
  exclude_equal  Boolean; if true, don't accept an exact match,
  and if there is one then move right if low and
  left if !low.
  offset      The output offset

  If low true, *offset <- index of the smallest item >= key,
  if low false the index of the largest item <= key.  In either case, if there
  is no such index, *offset is left alone and 0 is returned.

  Return:
  0     No suitable index exists; *offset has not been changed
  1     The correct index was stored into *offset
  -1     Error

  Example:  Suppose the keys are [2, 4], and exclude_equal is false.  Searching
  for 2 sets *offset to 0 and returns 1 regardless of low.  Searching for 4
  sets *offset to 1 and returns 1 regardless of low.
  Searching for 1:
  If low true, sets *offset to 0, returns 1.
  If low false, returns 0.
  Searching for 3:
  If low true, sets *offset to 1, returns 1.
  If low false, sets *offset to 0, returns 1.
  Searching for 5:
  If low true, returns 0.
  If low false, sets *offset to 1, returns 1.

  The 1, 3 and 5 examples are the same when exclude_equal is true.
*/
static int
Bucket_findRangeEnd(Bucket *self, PyObject *keyarg, int low, int exclude_equal,
                    int *offset)
{
    PyObject* obj_self = (PyObject*)self;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    int i;
    int cmp;
    int result = -1;    /* until proven innocent */
    KEY_TYPE key;
    int copied = 1;

    COPY_KEY_FROM_ARG(key, keyarg, copied);
    UNLESS (copied)
        return -1;

    UNLESS (per_use((cPersistentObject*)self, capi_struct))
        return -1;

    BUCKET_SEARCH(i, cmp, self, key, goto Done);
    if (cmp == 0) {
        /* exact match at index i */
        if (exclude_equal)
        {
            /* but we don't want an exact match */
            if (low)
                ++i;
            else
                --i;
        }
    }
    /* Else keys[i-1] < key < keys[i], picturing infinities at OOB indices,
    * and i has the smallest item > key, which is correct for low.
    */
    else if (! low)
        /* i-1 has the largest item < key (unless i-1 is 0OB) */
        --i;

    result = 0 <= i && i < self->len;
    if (result)
        *offset = i;

Done:
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return result;
}

static PyObject *
Bucket_maxminKey(Bucket *self, PyObject *args, int min)
{
    PyObject* obj_self = (PyObject*)self;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    PyObject *key=0;
    int rc;
    int offset = 0;
    int empty_bucket = 1;

    if (args && ! PyArg_ParseTuple(args, "|O", &key))
        return NULL;

    if (!per_use((cPersistentObject*)self, capi_struct))
        return NULL;

    UNLESS (self->len)
        goto empty;

    /* Find the low range */
    if (key && key != Py_None)
    {
        if ((rc = Bucket_findRangeEnd(self, key, min, 0, &offset)) <= 0)
        {
            if (rc < 0)
                return NULL;
            empty_bucket = 0;
            goto empty;
        }
    }
    else if (min)
        offset = 0;
    else
        offset = self->len -1;

    COPY_KEY_TO_OBJECT(key, self->keys[offset]);
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);

    return key;

empty:
    PyErr_SetString(PyExc_ValueError,
                    empty_bucket ? "empty bucket" :
                    "no key satisfies the conditions");
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return NULL;
}

static PyObject *
Bucket_minKey(Bucket *self, PyObject *args)
{
    return Bucket_maxminKey(self, args, 1);
}

static PyObject *
Bucket_maxKey(Bucket *self, PyObject *args)
{
    return Bucket_maxminKey(self, args, 0);
}

static int
Bucket_rangeSearch(Bucket *self, PyObject *args, PyObject *kw,
                   int *low, int *high)
{
    PyObject *min = Py_None;
    PyObject *max = Py_None;
    int excludemin = 0;
    int excludemax = 0;
    int rc;

    if (args)
    {
        if (! PyArg_ParseTupleAndKeywords(args, kw, "|OOii", search_keywords,
                                          &min,
                                          &max,
                                          &excludemin,
                                          &excludemax))
            return -1;
    }

    UNLESS (self->len)
        goto empty;

    /* Find the low range */
    if (min != Py_None)
    {
        rc = Bucket_findRangeEnd(self, min, 1, excludemin, low);
        if (rc < 0)
            return -1;
        if (rc == 0)
            goto empty;
    }
    else
    {
        *low = 0;
        if (excludemin)
        {
            if (self->len < 2)
                goto empty;
            ++*low;
        }
    }

    /* Find the high range */
    if (max != Py_None)
    {
        rc = Bucket_findRangeEnd(self, max, 0, excludemax, high);
        if (rc < 0)
            return -1;
        if (rc == 0)
            goto empty;
    }
    else
    {
        *high = self->len - 1;
        if (excludemax)
        {
            if (self->len < 2)
                goto empty;
            --*high;
        }
    }

    /* If min < max to begin with, it's quite possible that low > high now. */
    if (*low <= *high)
        return 0;

empty:
    *low = 0;
    *high = -1;
    return 0;
}

/*
** bucket_keys
**
** Generate a list of all keys in the bucket
**
** Arguments:    self    The Bucket
**        args    (unused)
**
** Returns:    list of bucket keys
*/
static PyObject *
bucket_keys(Bucket *self, PyObject *args, PyObject *kw)
{
    PyObject* obj_self = (PyObject*)self;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    PyObject *r = NULL;
    PyObject *key;
    int i;
    int low;
    int high;

    if (!per_use((cPersistentObject*)self, capi_struct))
        return NULL;

    if (Bucket_rangeSearch(self, args, kw, &low, &high) < 0)
        goto err;

    r = PyList_New(high-low+1);
    if (r == NULL)
        goto err;

    for (i=low; i <= high; i++)
    {
        COPY_KEY_TO_OBJECT(key, self->keys[i]);
        if (PyList_SetItem(r, i-low , key) < 0)
            goto err;
    }

    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return r;

err:
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    Py_XDECREF(r);
    return NULL;
}

/*
** bucket_values
**
** Generate a list of all values in the bucket
**
** Arguments:    self    The Bucket
**        args    (unused)
**
** Returns    list of values
*/
static PyObject *
bucket_values(Bucket *self, PyObject *args, PyObject *kw)
{
    PyObject* obj_self = (PyObject*)self;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    PyObject *r=0;
    PyObject *v;
    int i;
    int low;
    int high;

    if (!per_use((cPersistentObject*)self, capi_struct))
        return NULL;

    if (Bucket_rangeSearch(self, args, kw, &low, &high) < 0)
        goto err;

    UNLESS (r=PyList_New(high-low+1))
        goto err;

    for (i=low; i <= high; i++)
    {
        COPY_VALUE_TO_OBJECT(v, self->values[i]);
        UNLESS (v)
            goto err;
        if (PyList_SetItem(r, i-low, v) < 0)
            goto err;
    }

    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return r;

err:
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    Py_XDECREF(r);
    return NULL;
}

/*
** bucket_items
**
** Returns a list of all items in a bucket
**
** Arguments:    self    The Bucket
**        args    (unused)
**
** Returns:    list of all items in the bucket
*/
static PyObject *
bucket_items(Bucket *self, PyObject *args, PyObject *kw)
{
    PyObject* obj_self = (PyObject*)self;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    PyObject *r=0;
    PyObject *o=0;
    PyObject *item=0;
    int i;
    int low;
    int high;

    if (!per_use((cPersistentObject*)self, capi_struct))
        return NULL;

    if (Bucket_rangeSearch(self, args, kw, &low, &high) < 0)
        goto err;

    UNLESS (r=PyList_New(high-low+1))
        goto err;

    for (i=low; i <= high; i++)
    {
        UNLESS (item = PyTuple_New(2))
            goto err;

        COPY_KEY_TO_OBJECT(o, self->keys[i]);
        UNLESS (o)
            goto err;
        PyTuple_SET_ITEM(item, 0, o);

        COPY_VALUE_TO_OBJECT(o, self->values[i]);
        UNLESS (o)
            goto err;
        PyTuple_SET_ITEM(item, 1, o);

        if (PyList_SetItem(r, i-low, item) < 0)
            goto err;

        item = 0;
    }

    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return r;

err:
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    Py_XDECREF(r);
    Py_XDECREF(item);
    return NULL;
}

static PyObject *
bucket_byValue(Bucket *self, PyObject *omin)
{
    PyObject* obj_self = (PyObject*)self;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    PyObject *r=0;
    PyObject *o=0;
    PyObject *item=0;
    VALUE_TYPE min;
    VALUE_TYPE v;
    int i;
    int l;
    int copied=1;

    if (!per_use((cPersistentObject*)self, capi_struct))
        return NULL;

    COPY_VALUE_FROM_ARG(min, omin, copied);
    UNLESS(copied)
        return NULL;

    for (i=0, l=0; i < self->len; i++)
        if (TEST_VALUE(self->values[i], min) >= 0)
        l++;

    UNLESS (r=PyList_New(l))
        goto err;

    for (i=0, l=0; i < self->len; i++)
    {
        if (TEST_VALUE(self->values[i], min) < 0)
            continue;

        UNLESS (item = PyTuple_New(2))
            goto err;

        COPY_KEY_TO_OBJECT(o, self->keys[i]);
        UNLESS (o)
            goto err;
        PyTuple_SET_ITEM(item, 1, o);

        COPY_VALUE(v, self->values[i]);
        NORMALIZE_VALUE(v, min);
        COPY_VALUE_TO_OBJECT(o, v);
        DECREF_VALUE(v);
        UNLESS (o)
            goto err;
        PyTuple_SET_ITEM(item, 0, o);

        if (PyList_SetItem(r, l, item) < 0)
            goto err;
        l++;

        item = 0;
    }

    item = PyObject_CallMethodObjArgs(r, str_sort, NULL);
    if(item == NULL)
        goto err;
    Py_DECREF(item); /* Py_None */
    item = PyObject_CallMethodObjArgs(r, str_reverse, NULL);
    if(item == NULL)
        goto err;
    Py_DECREF(item); /* Py_None */

err:
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    Py_XDECREF(r);
    Py_XDECREF(item);
    return NULL;
}


static int
_bucket_clear(Bucket *self)
{
    const int len = self->len;
    /* silence compiler nag when neither keys nor values are objects*/
    (void)len;

    self->len = self->size = 0;

    Py_CLEAR(self->next);

    if (self->keys)
    {
#ifdef KEY_TYPE_IS_PYOBJECT
        for (int i_key = 0; i_key < len; ++i_key)
            /* XXX Should we use 'Py_CLEAR' instead of 'DECREF_KEY'?
             *
             * We *are* just about to free the whole array, but could
             * be be in the dreaded GC-inconsistent state here?
             */
            DECREF_KEY(self->keys[i_key]);
#endif
        free(self->keys);
        self->keys = NULL;
    }

    if (self->values)
    {
#ifdef VALUE_TYPE_IS_PYOBJECT
        for (int i_val = 0; i_val < len; ++i_val)
            /* XXX Should we use 'Py_CLEAR' instead of 'DECREF_VALUE'?
             *
             * We *are* just about to free the whole array, but could
             * be be in the dreaded GC-inconsistent state here?
             */
            DECREF_VALUE(self->values[i_val]);
#endif
        free(self->values);
        self->values = NULL;
    }

    return 0;
}

#ifdef PERSISTENT
static PyObject *
bucket__p_deactivate(Bucket *self, PyObject *args, PyObject *keywords)
{
    PyObject* obj_self = (PyObject*)self;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);

    int ghostify = 1;
    PyObject *force = NULL;

    if (args && PyTuple_GET_SIZE(args) > 0)
    {
        PyErr_SetString(PyExc_TypeError,
                        "_p_deactivate takes no positional arguments");
        return NULL;
    }
    if (keywords)
    {
        int size = PyDict_Size(keywords);
        force = PyDict_GetItemString(keywords, "force");
        if (force)
            size--;
        if (size) {
            PyErr_SetString(PyExc_TypeError,
                        "_p_deactivate only accepts keyword arg force");
            return NULL;
        }
    }

    if (self->jar && self->oid)
    {
        ghostify = self->state == cPersistent_UPTODATE_STATE;
        if (!ghostify && force) {
            if (PyObject_IsTrue(force))
            ghostify = 1;
            if (PyErr_Occurred())
            return NULL;
        }
        if (ghostify) {
            if (_bucket_clear(self) < 0) return NULL;
            capi_struct->ghostify((cPersistentObject*)self);
        }
    }
    Py_INCREF(Py_None);
    return Py_None;
}
#endif

static PyObject *
bucket_clear(Bucket *self, PyObject *args)
{
    PyObject* obj_self = (PyObject*)self;
    PyObject* result = NULL;

    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    if (!per_use((cPersistentObject*)self, capi_struct))
        return NULL;

    if (self->len)
    {
        if (_bucket_clear(self) < 0)
            return NULL;

        if (capi_struct->changed((cPersistentObject*)self) < 0)
            goto done;
    }
    result = Py_None;
    Py_INCREF(result);

done:
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return result;
}

/*
 * Return:
 *
 * For a set bucket (self->values is NULL), a one-tuple or two-tuple.  The
 * first element is a tuple of keys, of length self->len.  The second element
 * is the next bucket, present if and only if next is non-NULL:
 *
 *     (
 *          (keys[0], keys[1], ..., keys[len-1]),
 *          <self->next iff non-NULL>
 *     )
 *
 * For a mapping bucket (self->values is not NULL), a one-tuple or two-tuple.
 * The first element is a tuple interleaving keys and values, of length
 * 2 * self->len.  The second element is the next bucket, present iff next is
 * non-NULL:
 *
 *     (
 *          (keys[0], values[0], keys[1], values[1], ...,
 *                               keys[len-1], values[len-1]),
 *          <self->next iff non-NULL>
 *     )
 */
static PyObject *
bucket_getstate(Bucket *self)
{
    PyObject* obj_self = (PyObject*)self;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    PyObject *o = NULL;
    PyObject *items = NULL;
    PyObject *state;
    int i;
    int len;
    int l;

    if (!per_use((cPersistentObject*)self, capi_struct))
        return NULL;

    len = self->len;

    if (self->values) /* Bucket */
    {
        items = PyTuple_New(len * 2);
        if (items == NULL)
            goto err;
        for (i = 0, l = 0; i < len; i++) {
            COPY_KEY_TO_OBJECT(o, self->keys[i]);
            if (o == NULL)
            goto err;
            PyTuple_SET_ITEM(items, l, o);
            l++;

            COPY_VALUE_TO_OBJECT(o, self->values[i]);
            if (o == NULL)
            goto err;
            PyTuple_SET_ITEM(items, l, o);
            l++;
        }
    }
    else /* Set */
    {
        items = PyTuple_New(len);
        if (items == NULL)
            goto err;
        for (i = 0; i < len; i++) {
            COPY_KEY_TO_OBJECT(o, self->keys[i]);
            if (o == NULL)
            goto err;
            PyTuple_SET_ITEM(items, i, o);
        }
    }

    if (self->next)
        state = Py_BuildValue("OO", items, self->next);
    else
        state = Py_BuildValue("(O)", items);
    Py_DECREF(items);

    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return state;

err:
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    Py_XDECREF(items);
    return NULL;
}

static int
_bucket_setstate(Bucket *self, PyObject *state)
{
    PyObject *k;
    PyObject *v;
    PyObject *items;
    Bucket *next = NULL;
    int i;
    int l;
    int len;
    int copied=1;
    KEY_TYPE *keys;
    VALUE_TYPE *values;

    if (!PyArg_ParseTuple(state, "O|O:__setstate__", &items, &next))
        return -1;

    if (!PyTuple_Check(items)) {
        PyErr_SetString(PyExc_TypeError,
                        "tuple required for first state element");
        return -1;
    }

    len = PyTuple_Size(items);
    ASSERT(len >= 0, "_bucket_setstate: items tuple has negative size", -1);
    len /= 2;

    for (i = self->len; --i >= 0; ) {
        DECREF_KEY(self->keys[i]);
        DECREF_VALUE(self->values[i]);
    }
    self->len = 0;

    Py_CLEAR(self->next);

    if (len > self->size) {
        keys = BTree_Realloc(self->keys, sizeof(KEY_TYPE)*len);
        if (keys == NULL)
            return -1;
        values = BTree_Realloc(self->values, sizeof(VALUE_TYPE)*len);
        if (values == NULL)
            return -1;
        self->keys = keys;
        self->values = values;
        self->size = len;
    }

    for (i=0, l=0; i < len; i++) {
        k = PyTuple_GET_ITEM(items, l);
        l++;
        v = PyTuple_GET_ITEM(items, l);
        l++;

        COPY_KEY_FROM_ARG(self->keys[i], k, copied);
        if (!copied)
            return -1;
        COPY_VALUE_FROM_ARG(self->values[i], v, copied);
        if (!copied)
            return -1;
        INCREF_KEY(self->keys[i]);
        INCREF_VALUE(self->values[i]);
    }

    self->len = len;

    if (next) {
        Py_INCREF(next);
        self->next = next;
    }

    return 0;
}

static PyObject *
bucket_setstate(Bucket *self, PyObject *state)
{
    PyObject* obj_self = (PyObject*)self;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    int r;

    per_prevent_deactivation((cPersistentObject*)self);
    r = _bucket_setstate(self, state);
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);

    if (r < 0)
        return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
bucket_sub(PyObject *self, PyObject *other)
{
    PyObject *args = Py_BuildValue("OO", self, other);
    PyObject *module = _get_module(Py_TYPE(self));
    /* no check here, because 'difference_m' checks if needed. */
    return difference_m(module, args);
}

static PyObject *
bucket_or(PyObject *self, PyObject *other)
{
    PyObject *args = Py_BuildValue("OO", self, other);
    PyObject *module = _get_module(Py_TYPE(self));
    /* no check here, because 'union_m' checks if needed. */
    return union_m(module, args);
}

static PyObject *
bucket_and(PyObject *self, PyObject *other)
{
    PyObject *args = Py_BuildValue("OO", self, other);
    PyObject *module = _get_module(Py_TYPE(self));
    /* no check here, because 'intersection_m' checks if needed. */
    return intersection_m(module, args);
}

static PyObject *
bucket_setdefault(Bucket *self, PyObject *args)
{
    PyObject *key;
    PyObject *failobj; /* default */
    PyObject *value;   /* return value */
    int dummy_changed; /* in order to call _bucket_set */

    if (! PyArg_UnpackTuple(args, "setdefault", 2, 2, &key, &failobj))
        return NULL;

    value = _bucket_get(self, key, 0);
    if (value != NULL)
        return value;

    /* The key isn't in the bucket.  If that's not due to a KeyError exception,
     * pass back the unexpected exception.
     */
    if (! BTree_ShouldSuppressKeyError())
        return NULL;
    PyErr_Clear();

    /* Associate `key` with `failobj` in the bucket, and return `failobj`. */
    value = failobj;
    if (_bucket_set(self, key, failobj, 0, 0, &dummy_changed) < 0)
        value = NULL;
    Py_XINCREF(value);
    return value;
}


/* forward declaration */
static int
Bucket_length(Bucket *self);

static PyObject *
bucket_pop(Bucket *self, PyObject *args)
{
    PyObject *key;
    PyObject *failobj = NULL; /* default */
    PyObject *value;          /* return value */
    int dummy_changed;        /* in order to call _bucket_set */

    if (! PyArg_UnpackTuple(args, "pop", 1, 2, &key, &failobj))
        return NULL;

    value = _bucket_get(self, key, 0);
    if (value != NULL) {
        /* Delete key and associated value. */
        if (_bucket_set(self, key, NULL, 0, 0, &dummy_changed) < 0) {
        Py_DECREF(value);
        return NULL;
        }
        return value;
    }

    /* The key isn't in the bucket.  If that's not due to a KeyError exception,
     * pass back the unexpected exception.
     */
    if (! BTree_ShouldSuppressKeyError())
        return NULL;

    if (failobj != NULL) {
        /* Clear the KeyError and return the explicit default. */
        PyErr_Clear();
        Py_INCREF(failobj);
        return failobj;
    }

    /* No default given.  The only difference in this case is the error
     * message, which depends on whether the bucket is empty.
     */
    if (Bucket_length(self) == 0)
        PyErr_SetString(PyExc_KeyError, "pop(): Bucket is empty");
    return NULL;
}

static PyObject*
bucket_popitem(Bucket* self, PyObject* args)
{
    PyObject* key = NULL;
    PyObject* pop_args = NULL;
    PyObject* result_val = NULL;
    PyObject* result = NULL;

    if (PyTuple_Size(args) != 0) {
        PyErr_SetString(PyExc_TypeError, "popitem(): Takes no arguments.");
        return NULL;
    }

    key = Bucket_minKey(self, args); /* reuse existing empty tuple. */
    if (!key) {
        PyErr_Clear();
        PyErr_SetString(PyExc_KeyError, "popitem(): empty bucket.");
        return NULL;
    }

    pop_args = PyTuple_Pack(1, key);
    if (pop_args) {
        result_val = bucket_pop(self, pop_args);
        Py_DECREF(pop_args);
        if (result_val) {
            result = PyTuple_Pack(2, key, result_val);
            Py_DECREF(result_val);
        }
    }

    Py_DECREF(key);
    return result;
}


/* Search bucket self for key.  This is the sq_contains slot of the
 * PySequenceMethods.
 *
 * Return:
 *     -1     error
 *      0     not found
 *      1     found
 */
static int
bucket_contains(Bucket *self, PyObject *key)
{
    PyObject *asobj = _bucket_get(self, key, 1);
    int result = -1;

    if (asobj != NULL) {
        result = PyLong_AsLong(asobj) ? 1 : 0;
        Py_DECREF(asobj);
    }
    else if (BTree_ShouldSuppressKeyError()) {
        PyErr_Clear();
        result = 0;
    }
    return result;
}

static PyObject *
bucket_has_key(Bucket *self, PyObject *key)
{
    int result = -1;
    result = bucket_contains(self, key);
    if (result == -1) {
        return NULL;
    }

    if (result)
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}

/*
** bucket_getm
**
*/
static PyObject *
bucket_getm(Bucket *self, PyObject *args)
{
    PyObject *key, *d=Py_None, *r;

    if (!PyArg_ParseTuple(args, "O|O:get", &key, &d))
        return NULL;
    r = _bucket_get(self, key, 0);
    if (r)
        return r;
    if (PyErr_ExceptionMatches(PyExc_TypeError)) {
        PyErr_Clear();
        PyErr_SetObject(PyExc_KeyError, key);
    }
    if (!BTree_ShouldSuppressKeyError())
        return NULL;
    PyErr_Clear();
    Py_INCREF(d);
    return d;
}

/**************************************************************************/
/* Iterator support. */

/* A helper to build all the iterators for Buckets and Sets.
 * If args is NULL, the iterator spans the entire structure.  Else it's an
 * argument tuple, with optional low and high arguments.
 * kind is 'k', 'v' or 'i'.
 * Returns a BTreeIter object, or NULL if error.
 */
static PyObject *
buildBucketIter(Bucket *self, PyObject *args, PyObject *kw, char kind)
{
    PyObject* obj_self = (PyObject*)self;
    BTreeItems *items;
    int lowoffset;
    int highoffset;
    BTreeIter *result = NULL;

    PyObject* module = _get_module(Py_TYPE(obj_self));

    if (module == NULL) {
        PyErr_SetString(
            PyExc_RuntimeError, "buildBucketIter: module is NULL");
        return NULL;
    }

    /* If we have a valid module, this one is bound to succeed. */
    PerCAPI* capi_struct = _get_capi_struct_from_module(module);

    if (!per_use((cPersistentObject*)self, capi_struct))
        return NULL;
    if (Bucket_rangeSearch(self, args, kw, &lowoffset, &highoffset) < 0)
        goto Done;

    items = (BTreeItems *)newBTreeItems(module, kind,
                                        self, lowoffset,
                                        self, highoffset
                                       );
    if (items == NULL)
        goto Done;

    result = newBTreeIter(module, items);      /* win or lose, we're done */
    Py_DECREF(items);

Done:
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return (PyObject *)result;
}

/* The implementation of iter(Bucket_or_Set); the Bucket tp_iter slot. */
static PyObject *
Bucket_getiter(Bucket *self)
{
    return buildBucketIter(self, NULL, NULL, 'k');
}

/* The implementation of Bucket.iterkeys(). */
static PyObject *
Bucket_iterkeys(Bucket *self, PyObject *args, PyObject *kw)
{
    return buildBucketIter(self, args, kw, 'k');
}

/* The implementation of Bucket.itervalues(). */
static PyObject *
Bucket_itervalues(Bucket *self, PyObject *args, PyObject *kw)
{
    return buildBucketIter(self, args, kw, 'v');
}

/* The implementation of Bucket.iteritems(). */
static PyObject *
Bucket_iteritems(Bucket *self, PyObject *args, PyObject *kw)
{
    return buildBucketIter(self, args, kw, 'i');
}

/* End of iterator support. */

#ifdef PERSISTENT
/* Defined in 'MergeTemplate.c' */
static PyObject *merge_error(
    PyObject* module, int p1, int p2, int p3, int reason
);
static PyObject *bucket_merge(
    PyObject* module, Bucket *s1, Bucket *s2, Bucket *s3);

static PyObject *
_bucket__p_resolveConflict(PyTypeObject *tp, PyObject *s[3])
{
    PyObject *result = NULL;    /* guilty until proved innocent */
    Bucket *b[3] = {NULL, NULL, NULL};
    PyObject *meth = NULL;
    PyObject *a = NULL;
    int i;

    PyObject *module = _get_module(tp);

    if (module == NULL) {
        PyErr_SetString(
            PyExc_RuntimeError, "_bucket__p_resolveConflict: module is NULL");
        return NULL;
    }

    for (i = 0; i < 3; i++) {
        PyObject *r;

        b[i] = BUCKET(tp->tp_alloc(tp, 0));
        if (b[i] == NULL)
            goto Done;
        if (s[i] == Py_None) /* None is equivalent to empty, for BTrees */
            continue;
        meth = PyObject_GetAttr((PyObject *)b[i], str___setstate__);
        if (meth == NULL)
            goto Done;
        a = PyTuple_New(1);
        if (a == NULL)
            goto Done;
        PyTuple_SET_ITEM(a, 0, s[i]);
        Py_INCREF(s[i]);
        r = PyObject_CallObject(meth, a);  /* b[i].__setstate__(s[i]) */
        if (r == NULL)
            goto Done;
        Py_DECREF(r);
        Py_DECREF(a);
        Py_DECREF(meth);
        a = meth = NULL;
    }

    if (b[0]->next != b[1]->next || b[0]->next != b[2]->next)
        merge_error(module, -1, -1, -1, 0);
    else
        result = bucket_merge(module, b[0], b[1], b[2]);

Done:
    Py_XDECREF(meth);
    Py_XDECREF(a);
    Py_XDECREF(b[0]);
    Py_XDECREF(b[1]);
    Py_XDECREF(b[2]);

    return result;
}

static PyObject *
bucket__p_resolveConflict(Bucket *self, PyObject *args)
{
    PyObject *s[3];

    if (!PyArg_ParseTuple(args, "OOO", &s[0], &s[1], &s[2]))
        return NULL;

    return _bucket__p_resolveConflict(Py_TYPE(self), s);
}
#endif

/* Caution:  Even though the _next attribute is read-only, a program could
   do arbitrary damage to the btree internals.  For example, it could call
   clear() on a bucket inside a BTree.

   We need to decide if the convenience for inspecting BTrees is worth
   the risk.
*/

static struct PyMemberDef Bucket_members[] = {
    {"_next", T_OBJECT, offsetof(Bucket, next)},
    {NULL}
};

static struct PyMethodDef Bucket_methods[] = {
    {"__getstate__", (PyCFunction) bucket_getstate, METH_NOARGS,
     "__getstate__() -- Return the picklable state of the object"},

    {"__setstate__", (PyCFunction) bucket_setstate, METH_O,
     "__setstate__() -- Set the state of the object"},

    {"keys", (PyCFunction) bucket_keys, METH_VARARGS | METH_KEYWORDS,
     "keys([min, max]) -- Return the keys"},

    {"has_key", (PyCFunction) bucket_has_key, METH_O,
     "has_key(key) -- Test whether the bucket contains the given key"},

    {"clear", (PyCFunction) bucket_clear, METH_VARARGS,
     "clear() -- Remove all of the items from the bucket"},

    {"update", (PyCFunction) Mapping_update, METH_O,
     "update(collection) -- Add the items from the given collection"},

    {"maxKey", (PyCFunction) Bucket_maxKey, METH_VARARGS,
     "maxKey([key]) -- Find the maximum key\n\n"
     "If an argument is given, find the maximum <= the argument"},

    {"minKey", (PyCFunction) Bucket_minKey, METH_VARARGS,
     "minKey([key]) -- Find the minimum key\n\n"
     "If an argument is given, find the minimum >= the argument"},

    {"values", (PyCFunction) bucket_values, METH_VARARGS | METH_KEYWORDS,
     "values([min, max]) -- Return the values"},

    {"items", (PyCFunction) bucket_items, METH_VARARGS | METH_KEYWORDS,
     "items([min, max])) -- Return the items"},

    {"byValue", (PyCFunction) bucket_byValue, METH_O,
     "byValue(min) -- "
     "Return value-keys with values >= min and reverse sorted by values"},

    {"get", (PyCFunction) bucket_getm, METH_VARARGS,
     "get(key[,default]) -- Look up a value\n\n"
     "Return the default (or None) if the key is not found."},

    {"setdefault", (PyCFunction) bucket_setdefault, METH_VARARGS,
     "D.setdefault(k, d) -> D.get(k, d), also set D[k]=d if k not in D.\n\n"
     "Return the value like get() except that if key is missing, d is both\n"
     "returned and inserted into the bucket as the value of k."},

    {"pop", (PyCFunction) bucket_pop, METH_VARARGS,
     "D.pop(k[, d]) -> v, remove key and return the corresponding value.\n\n"
     "If key is not found, d is returned if given, otherwise KeyError\n"
     "is raised."},

    {"popitem", (PyCFunction)bucket_popitem, METH_VARARGS,
     "D.popitem() -> (k, v), remove and return some (key, value) pair\n"
     "as a 2-tuple; but raise KeyError if D is empty."},

    {"iterkeys", (PyCFunction) Bucket_iterkeys, METH_VARARGS | METH_KEYWORDS,
     "B.iterkeys([min[,max]]) -> an iterator over the keys of B"},

    {"itervalues",
     (PyCFunction) Bucket_itervalues, METH_VARARGS | METH_KEYWORDS,
     "B.itervalues([min[,max]]) -> an iterator over the values of B"},

    {"iteritems", (PyCFunction) Bucket_iteritems, METH_VARARGS | METH_KEYWORDS,
     "B.iteritems([min[,max]]) -> an iterator over the (key, value) "
     "items of B"},

#ifdef EXTRA_BUCKET_METHODS
    EXTRA_BUCKET_METHODS
#endif

#ifdef PERSISTENT
    {"_p_resolveConflict",
     (PyCFunction) bucket__p_resolveConflict, METH_VARARGS,
     "_p_resolveConflict() -- Reinitialize from a newly created copy"},

    {"_p_deactivate",
     (PyCFunction) bucket__p_deactivate, METH_VARARGS | METH_KEYWORDS,
     "_p_deactivate() -- Reinitialize from a newly created copy"},
#endif
    {NULL, NULL}
};

static int
Bucket_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *v = NULL;

    if (!PyArg_ParseTuple(args, "|O:" MOD_NAME_PREFIX "Bucket", &v))
        return -1;

    if (v)
        return update_from_seq(self, v);
    else
        return 0;
}

static void
bucket_dealloc(Bucket *self)
{
    PyObject* obj_self = (PyObject*)self;

#if USE_HEAP_ALLOCATED_TYPES
    PyTypeObject* tp = Py_TYPE(obj_self);
#endif

    PyObject_GC_UnTrack(obj_self);
    if (self->state != cPersistent_GHOST_STATE) {
        _bucket_clear(self);
    }

    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    if (! capi_struct) {
        PyErr_SetString(PyExc_RuntimeError, "Cannot find persistence CAPI");
        return;
    }
    capi_struct->pertype->tp_dealloc(obj_self);

#if USE_HEAP_ALLOCATED_TYPES
    int per_is_heaptype = capi_struct->pertype->tp_flags & Py_TPFLAGS_HEAPTYPE;

    /* Heap-allocated Persistent will have already decref'ed our type. */
    if (!per_is_heaptype)
        Py_DECREF(tp);
#endif
}

static int
bucket_traverse(Bucket *self, visitproc visit, void *arg)
{
    PyObject* obj_self = (PyObject*)self;

    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    if(capi_struct == NULL) {
        /* Likely means that we are in application shutdown:  just bail.*/
        return -1;
    }
    /* Call our base type's traverse function.  Because buckets are
     * subclasses of Peristent, there must be one.
     */
    if (capi_struct->pertype->tp_traverse(obj_self, visit, arg) < 0)
        return -1;

#if USE_HEAP_ALLOCATED_TYPES
    int per_is_heaptype = capi_struct->pertype->tp_flags & Py_TPFLAGS_HEAPTYPE;

    /* Heap-allocated Persistent will have already traversed our type. */
    if (!per_is_heaptype)
        Py_VISIT(Py_TYPE(obj_self));
#endif

    /* If this is registered with the persistence system, cleaning up cycles
     * is the database's problem.  It would be horrid to unghostify buckets
     * here just to chase pointers every time gc runs.
     */
    if (self->state == cPersistent_GHOST_STATE)
        return 0;

    /*
     *  OK, now we visit "normal" attributes / items.
     */

#ifdef KEY_TYPE_IS_PYOBJECT
    /* Keys are Python objects so need to be traversed. */
    for (int i_key = 0; i_key < self->len; ++i_key)
        Py_VISIT(self->keys[i_key]);
#endif

#ifdef VALUE_TYPE_IS_PYOBJECT
    if (self->values != NULL) {
        /* self->values exists (this is a mapping bucket, not a set bucket),
         * and are Python objects, so need to be traversed. */
        for (int i_val = 0; i_val < self->len; ++i_val)
            Py_VISIT(self->values[i_val]);
    }
#endif

    Py_VISIT(self->next);

    return 0;
}

static int
bucket_tp_clear(Bucket *self)
{
    if (self->state != cPersistent_GHOST_STATE)
        _bucket_clear(self);
    return 0;
}

/* Code to access Bucket objects as mappings */
static int
Bucket_length( Bucket *self)
{
    PyObject* obj_self = (PyObject*)self;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    int r;
    UNLESS (per_use((cPersistentObject*)self, capi_struct))
        return -1;
    r = self->len;
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return r;
}


static PyObject *
bucket_repr(Bucket *self)
{
    PyObject *i, *r;

    i = bucket_items(self, NULL, NULL);
    if (!i)
    {
        return NULL;
    }
    r = PyUnicode_FromFormat("%s(%R)", Py_TYPE(self)->tp_name, i);
    Py_DECREF(i);
    return r;
}

static char Bucket__name__[] = MODULE_NAME MOD_NAME_PREFIX "Bucket";
static char Bucket__doc__[] =
    "Buckets are fundamental building blocks of BTrees";

#if USE_STATIC_TYPES

static PyNumberMethods Bucket_as_number = {
    .nb_subtract               = bucket_sub,
    .nb_and                    = bucket_and,
    .nb_or                     = bucket_or,
};

static PyMappingMethods Bucket_as_mapping = {
    .mp_length                  = (lenfunc)Bucket_length,
    .mp_subscript               = (binaryfunc)bucket_getitem,
    .mp_ass_subscript           = (objobjargproc)bucket_setitem,
};

static PySequenceMethods Bucket_as_sequence = {
    .sq_contains                = (objobjproc)bucket_contains,
};

static PyTypeObject Bucket_type_def = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name                    = Bucket__name__,
    .tp_doc                     = Bucket__doc__,
    .tp_basicsize               = sizeof(Bucket),
    .tp_flags                   = Py_TPFLAGS_DEFAULT |
                                  Py_TPFLAGS_HAVE_GC |
                                  Py_TPFLAGS_BASETYPE,
    .tp_init                    = Bucket_init,
    .tp_alloc                   = _pytype_generic_alloc,
    .tp_new                     = _pytype_generic_new,
    .tp_repr                    = (reprfunc)bucket_repr,
    .tp_iter                    = (getiterfunc)Bucket_getiter,
    .tp_traverse                = (traverseproc)bucket_traverse,
    .tp_clear                   = (inquiry)bucket_tp_clear,
    .tp_dealloc                 = (destructor)bucket_dealloc,
    .tp_methods                 = Bucket_methods,
    .tp_members                 = Bucket_members,
    .tp_as_number               = &Bucket_as_number,
    .tp_as_sequence             = &Bucket_as_sequence,
    .tp_as_mapping              = &Bucket_as_mapping,
};

#else

static PyType_Slot Bucket_type_slots[] = {
    {Py_tp_doc,                 Bucket__doc__},
    {Py_tp_alloc,               _pytype_generic_alloc},
    {Py_tp_new,                 _pytype_generic_new},
    {Py_tp_init,                Bucket_init},
    {Py_tp_repr,                (reprfunc)bucket_repr},
    {Py_tp_iter,                (getiterfunc)Bucket_getiter},
    {Py_tp_traverse,            (traverseproc)bucket_traverse},
    {Py_tp_clear,               (inquiry)bucket_tp_clear},
    {Py_tp_dealloc,             (destructor)bucket_dealloc},
    {Py_tp_methods,             Bucket_methods},
    {Py_tp_members,             Bucket_members},
    {Py_nb_subtract,            bucket_sub},
    {Py_nb_and,                 bucket_and},
    {Py_nb_or,                  bucket_or},
    {Py_mp_length,              (lenfunc)Bucket_length},
    {Py_mp_subscript,           (binaryfunc)bucket_getitem},
    {Py_mp_ass_subscript,       (objobjargproc)bucket_setitem},
    {Py_sq_contains,            (objobjproc)bucket_contains},
    {0,                         NULL}
};

static PyType_Spec Bucket_type_spec = {
    .name                       = Bucket__name__,
    .basicsize                  = sizeof(Bucket),
    .flags                      = Py_TPFLAGS_DEFAULT |
                                  Py_TPFLAGS_HAVE_GC |
                                  Py_TPFLAGS_IMMUTABLETYPE |
                                  Py_TPFLAGS_BASETYPE,
    .slots                      = Bucket_type_slots
};

#endif

static int
nextBucket(SetIteration *i)
{
    PyObject* obj_self = i->set;
    PerCAPI* capi_struct = _get_capi_struct(obj_self);
    if (i->position >= 0)
    {
        UNLESS(per_use((cPersistentObject*)BUCKET(i->set), capi_struct))
            return -1;

        if (i->position)
        {
          DECREF_KEY(i->key);
          DECREF_VALUE(i->value);
        }

        if (i->position < BUCKET(i->set)->len)
        {
          COPY_KEY(i->key, BUCKET(i->set)->keys[i->position]);
          INCREF_KEY(i->key);
          COPY_VALUE(i->value, BUCKET(i->set)->values[i->position]);
          INCREF_VALUE(i->value);
          i->position ++;
        }
        else
        {
          i->position = -1;
          capi_struct->accessed((cPersistentObject*)BUCKET(i->set));
        }

        per_allow_deactivation((cPersistentObject*)BUCKET(i->set));
    }

    return 0;
}
