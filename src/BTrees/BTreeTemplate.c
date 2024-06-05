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

#define BTREETEMPLATE_C "$Id$\n"

/*
 *  BTreeType metaclass
 */

static int
BTreeType_setattro(PyTypeObject* type, PyObject* name, PyObject* value)
{
    PyObject* allowed_names = _get_btreetype_setattro_allowed_names(type);
    /*
      type.tp_setattro prohibits setting any attributes on a built-in type,
      so we need to use our own (metaclass) type to handle it. The set of
      allowable values needs to be carefully controlled (e.g., setting methods
      would be bad).

      Alternately, we could use heap-allocated types when they are supported
      an all the versions we care about, because those do allow setting
      attributes.
    */
    int allowed;
    allowed = PySequence_Contains(allowed_names, name);
    if (allowed < 0) {
        return -1;
    }

    if (allowed) {
        PyDict_SetItem(type->tp_dict, name, value);
        PyType_Modified(type);
        if (PyErr_Occurred()) {
            return -1;
        }
        return 0;
    }
    return PyType_Type.tp_setattro((PyObject*)type, name, value);
}

static char BTreeType__name__[] =
    MODULE_NAME MOD_NAME_PREFIX "BTreeType";
static char BTreeType__doc__[] = "Metaclass for BTrees";

#if USE_STATIC_TYPES

static PyTypeObject BTreeType_type_def = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name                    = BTreeType__name__,
    .tp_doc                     = BTreeType__doc__,
    .tp_basicsize               = 0,
    .tp_flags                   = Py_TPFLAGS_DEFAULT |
                                  Py_TPFLAGS_BASETYPE,
    .tp_setattro                = (setattrofunc)BTreeType_setattro,
};

#else

static PyType_Slot BTreeType_type_slots[] = {
    {Py_tp_doc,                 BTreeType__doc__},
    {Py_tp_setattro,            (setattrofunc)BTreeType_setattro},
    {0,                         NULL}
};

static PyType_Spec BTreeType_type_spec = {
    .name                       = BTreeType__name__,
    .basicsize                  = 0,
    .flags                      = Py_TPFLAGS_DEFAULT |
                                  Py_TPFLAGS_BASETYPE,
    .slots                      = BTreeType_type_slots
};

#endif

/*
 *  BTree type
 */

static long
_get_max_size(BTree *self, PyObject *name, long default_max)
{
  PyObject *size;
  long isize;
  size = PyObject_GetAttr(OBJECT(OBJECT(self)->ob_type), name);
  if (size == NULL) {
      PyErr_Clear();
      return default_max;
  }

  isize = PyLong_AsLong(size);

  Py_DECREF(size);
  if (isize <= 0 && ! PyErr_Occurred()) {
    PyErr_SetString(PyExc_ValueError,
                    "non-positive max size in BTree subclass");
    return -1;
  }

  return isize;
}

static int
_max_internal_size(BTree *self)
{
  long isize;

  if (self->max_internal_size > 0) return self->max_internal_size;
  isize = _get_max_size(self, str_max_internal_size, -1);
  self->max_internal_size = isize;
  return isize;
}

static int
_max_leaf_size(BTree *self)
{
  long isize;

  if (self->max_leaf_size > 0) return self->max_leaf_size;
  isize = _get_max_size(self, str_max_leaf_size, -1);
  self->max_leaf_size = isize;
  return isize;
}

/* Sanity-check a BTree.  This is a private helper for BTree_check.  Return:
 *      -1         Error.  If it's an internal inconsistency in the BTree,
 *                 AssertionError is set.
 *       0         No problem found.
 *
 * nextbucket is the bucket "one beyond the end" of the BTree; the last bucket
 * directly reachable from following right child pointers *should* be linked
 * to nextbucket (and this is checked).
 */
static int
BTree_check_inner(BTree *self, Bucket *nextbucket)
{
    PyObject* obj_self = (PyObject*)self;
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);
    int i;
    Bucket *bucketafter;
    Sized *child;
    char *errormsg = "internal error";  /* someone should have overriden */
    Sized *activated_child = NULL;
    int result = -1;    /* until proved innocent */

#define CHECK(CONDITION, ERRORMSG)              \
  if (!(CONDITION)) {                           \
    errormsg = (ERRORMSG);                      \
    goto Error;                                 \
  }

    if (!per_use((cPersistentObject*)self, capi_struct))
        return -1;
    CHECK(self->len >= 0, "BTree len < 0");
    CHECK(self->len <= self->size, "BTree len > size");
    if (self->len == 0) /* Empty BTree. */
    {
        CHECK(self->firstbucket == NULL,
            "Empty BTree has non-NULL firstbucket");
        result = 0;
        goto Done;
    }
    /* Non-empty BTree. */
    CHECK(self->firstbucket != NULL, "Non-empty BTree has NULL firstbucket");

    /* Obscure:  The first bucket is pointed to at least by self->firstbucket
    * and data[0].child of whichever BTree node it's a child of.  However,
    * if persistence is enabled then the latter BTree node may be a ghost
    * at this point, and so its pointers "don't count":  we can only rely
    * on self's pointers being intact.
    */
#ifdef PERSISTENT
    CHECK(Py_REFCNT(self->firstbucket) >= 1,
            "Non-empty BTree firstbucket has refcount < 1");
#else
    CHECK(Py_REFCNT(self->firstbucket) >= 2,
            "Non-empty BTree firstbucket has refcount < 2");
#endif

    for (i = 0; i < self->len; ++i)
    {
        CHECK(self->data[i].child != NULL, "BTree has NULL child");
    }

    if (SameType_Check(self, self->data[0].child))
    {
        /* Our children are also BTrees. */
        child = self->data[0].child;
        UNLESS (per_use((cPersistentObject*)child, capi_struct))
            goto Done;
        activated_child = child;
        CHECK(self->firstbucket == BTREE(child)->firstbucket,
            "BTree has firstbucket different than "
            "its first child's firstbucket");
        per_allow_deactivation((cPersistentObject*)child);
        activated_child = NULL;
        for (i = 0; i < self->len; ++i)
        {
            child = self->data[i].child;
            CHECK(SameType_Check(self, child),
                    "BTree children have different types");
            if (i == self->len - 1)
                bucketafter = nextbucket;
            else
            {
                BTree *child2 = BTREE(self->data[i+1].child);
                UNLESS (per_use((cPersistentObject*)child2, capi_struct))
                    goto Done;
                bucketafter = child2->firstbucket;
                per_allow_deactivation((cPersistentObject*)child2);
            }
            if (BTree_check_inner(BTREE(child), bucketafter) < 0)
                goto Done;
        }
    }
    else /* Our children are buckets. */
    {
        CHECK(self->firstbucket == BUCKET(self->data[0].child),
            "Bottom-level BTree node has inconsistent firstbucket belief");
        for (i = 0; i < self->len; ++i)
        {
            child = self->data[i].child;
            UNLESS (per_use((cPersistentObject*)child, capi_struct))
                goto Done;
            activated_child = child;
            CHECK(!SameType_Check(self, child),
                    "BTree children have different types");
            CHECK(
                child->len >= 1, "Bucket length < 1");/* no empty buckets! */
            CHECK(child->len <= child->size, "Bucket len > size");
#ifdef PERSISTENT
            CHECK(Py_REFCNT(child) >= 1, "Bucket has refcount < 1");
#else
            CHECK(Py_REFCNT(child) >= 2, "Bucket has refcount < 2");
#endif
            if (i == self->len - 1)
                bucketafter = nextbucket;
            else
                bucketafter = BUCKET(self->data[i+1].child);
            CHECK(BUCKET(child)->next == bucketafter,
                    "Bucket next pointer is damaged");
            per_allow_deactivation((cPersistentObject*)child);
            activated_child = NULL;
        }
    }
    result = 0;
    goto Done;

Error:
    PyErr_SetString(PyExc_AssertionError, errormsg);
    result = -1;

Done:
    /* No point updating access time -- this isn't a "real" use. */
    per_allow_deactivation((cPersistentObject*)self);
    if (activated_child)
    {
        per_allow_deactivation((cPersistentObject*)activated_child);
    }
    return result;

#undef CHECK
}

/* Sanity-check a BTree.  This is the ._check() method.  Return:
 *      NULL       Error.  If it's an internal inconsistency in the BTree,
 *                 AssertionError is set.
 *      Py_None    No problem found.
 */
static PyObject*
BTree_check(BTree *self)
{
    PyObject *result = NULL;
    int i = BTree_check_inner(self, NULL);

    if (i >= 0)
    {
        result = Py_None;
        Py_INCREF(result);
    }
    return result;
}

#define _BGET_REPLACE_TYPE_ERROR 1
#define _BGET_ALLOW_TYPE_ERROR 0
/*
** _BTree_get
**
** Search a BTree.
**
** Arguments
**      self        a pointer to a BTree
**      keyarg      the key to search for, as a Python object
**      has_key     true/false; when false, try to return the associated
**                  value; when true, return a boolean
**      replace_type_err    true/false: When true, ignore the TypeError from
**                            a key conversion issue, instead
**                            transforming it into a KeyError set. If
**                            you are just reading/searching, set to
**                            true. If you will be adding/updating,
**                             however,  set to false. Or use
**                            _BGET_REPLACE_TYPE_ERROR
**                            and _BGET_ALLOW_TYPE_ERROR, respectively.
** Return
**      When has_key false:
**          If key exists, its associated value.
**          If key doesn't exist, NULL and KeyError is set.
**      When has_key true:
**          A Python int is returned in any case.
**          If key exists, the depth of the bucket in which it was found.
**          If key doesn't exist, 0.
*/
static PyObject *
_BTree_get(BTree *self, PyObject *keyarg, int has_key, int replace_type_err)
{
    PyObject* obj_self = (PyObject*)self;
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);
    KEY_TYPE key;
    PyObject *result = NULL;    /* guilty until proved innocent */
    int copied = 1;

    COPY_KEY_FROM_ARG(key, keyarg, copied);
    UNLESS (copied)
    {
        if (replace_type_err && PyErr_ExceptionMatches(PyExc_TypeError))
        {
            PyErr_Clear();
            PyErr_SetObject(PyExc_KeyError, keyarg);
        }
        return NULL;
    }

    if (!per_use((cPersistentObject*)self, capi_struct))
        return NULL;
    if (self->len == 0)
    {
        /* empty BTree */
        if (has_key)
            result = PyLong_FromLong(0);
        else
            PyErr_SetObject(PyExc_KeyError, keyarg);
    }
    else
    {
        for (;;)
        {
            int i;
            Sized *child;

            BTREE_SEARCH(i, self, key, goto Done);
            child = self->data[i].child;
            has_key += has_key != 0;    /* bump depth counter, maybe */
            if (SameType_Check(self, child))
            {
                per_allow_deactivation((cPersistentObject*)self);
                capi_struct->accessed((cPersistentObject*)self);
                self = BTREE(child);
                if (!per_use((cPersistentObject*)self, capi_struct))
                    return NULL;
            }
            else
            {
                result = _bucket_get(BUCKET(child), keyarg, has_key);
                break;
            }
        }
    }

Done:
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return result;
}

static PyObject *
BTree_get(BTree *self, PyObject *key)
{
    return _BTree_get(self, key, 0, _BGET_REPLACE_TYPE_ERROR);
}

/* Create a new bucket for the BTree or TreeSet using the class attribute
   _bucket_type, which is normally initialized to Bucket_type_def or
   Set_type_def as appropriate.
*/
static Sized *
BTree_newBucket(BTree *self)
{
#if 1
    PyObject *factory;
    Sized *result;

    /* str__bucket_type defined in BTreeModuleTemplate.c */
    factory = PyObject_GetAttr((PyObject *)Py_TYPE(self), str__bucket_type);
    if (factory == NULL)
        return NULL;
    /* TODO: Should we check that the factory actually returns something
        of the appropriate type? How?  The C code here is going to
        depend on any custom bucket type having the same layout at the
        C level.
    */
    result = SIZED(PyObject_CallObject(factory, NULL));
    Py_DECREF(factory);
    return result;
#else
    /* Can't do this, even though it would be much cleaner, because
     * we've made the promise that classes derived from a BTree can set
     * the '_bucket_type' attribute with whatever they choose (any callable
     * which takes no args, but usually a subclass of the same family's
     * Bucket type.
     */
    PyObject* obj_self = (PyObject*)self;

    PyTypeObject* bucket_type = _get_bucket_type(obj_self);
    if (bucket_type == NULL)
        return NULL;

    return SIZED(bucket_type->tp_alloc(bucket_type, 0));
#endif

}

/*
 * Move data from the current BTree, from index onward, to the newly created
 * BTree 'next'.  self and next must both be activated.  If index is OOB (< 0
 * or >= self->len), use self->len / 2 as the index (i.e., split at the
 * midpoint).  self must have at least 2 children on entry, and index must
 * be such that self and next each have at least one child at exit.  self's
 * accessed time is updated.
 *
 * Return:
 *    -1    error
 *     0    OK
 */
static int
BTree_split(BTree *self, int index, BTree *next)
{
    PyObject* obj_self = (PyObject*)self;
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);
    int next_size;
    Sized *child;

    if (index < 0 || index >= self->len)
        index = self->len / 2;

    next_size = self->len - index;
    ASSERT(index > 0, "split creates empty tree", -1);
    ASSERT(next_size > 0, "split creates empty tree", -1);

    next->data = BTree_Malloc(sizeof(BTreeItem) * next_size);
    if (!next->data)
        return -1;
    memcpy(next->data, self->data + index, sizeof(BTreeItem) * next_size);
    next->size = next_size;  /* but don't set len until we succeed */

    /* Set next's firstbucket.  self->firstbucket is still correct. */
    child = next->data[0].child;
    if (SameType_Check(self, child))
    {
        if (!per_use((cPersistentObject*)child, capi_struct))
            return -1;
        next->firstbucket = BTREE(child)->firstbucket;
        per_allow_deactivation((cPersistentObject*)child);
        capi_struct->accessed((cPersistentObject*)child);
    }
    else
        next->firstbucket = BUCKET(child);
    Py_INCREF(next->firstbucket);

    next->len = next_size;
    self->len = index;
    return capi_struct->changed((cPersistentObject*)self) >= 0 ? 0 : -1;
}


/* Fwd decl -- BTree_grow and BTree_split_root reference each other. */
static int BTree_grow(BTree *self, int index, int noval);

/* Split the root.  This is a little special because the root isn't a child
 * of anything else, and the root needs to retain its object identity.  So
 * this routine moves the root's data into a new child, and splits the
 * latter.  This leaves the root with two children.
 *
 * Return:
 *      0   OK
 *     -1   error
 *
 * CAUTION:  The caller must call 'capi_struct->changed' on self.
 */
static int
BTree_split_root(BTree *self, int noval)
{
    PyTypeObject* tp = Py_TYPE(self);
    BTree *child;
    BTreeItem *d;

    /* Create a child BTree, and a new data vector for self. */
    child = BTREE(tp->tp_alloc(tp, 0));
    if (!child)
        return -1;

    d = BTree_Malloc(sizeof(BTreeItem) * 2);
    if (!d) {
        Py_DECREF(child);
        return -1;
    }

    /* Move our data to new BTree. */
    child->size = self->size;
    child->len = self->len;
    child->data = self->data;
    child->firstbucket = self->firstbucket;
    Py_INCREF(child->firstbucket);

    /* Point self to child and split the child. */
    self->data = d;
    self->len = 1;
    self->size = 2;
    self->data[0].child = SIZED(child); /* transfers reference ownership */
    return BTree_grow(self, 0, noval);
}

/*
** BTree_grow
**
** Grow a BTree
**
** Arguments:    self    The BTree
**        index    self->data[index].child needs to be split.  index
**                      must be 0 if self is empty (len == 0), and a new
**                      empty bucket is created then.
**              noval   Boolean; is this a set (true) or mapping (false)?
**
** Returns:     0    on success
**        -1    on failure
**
** CAUTION:  If self is empty on entry, this routine adds an empty bucket.
** That isn't a legitimate BTree; if the caller doesn't put something in
** in the bucket (say, because of a later error), the BTree must be cleared
** to get rid of the empty bucket.
*/
static int
BTree_grow(BTree *self, int index, int noval)
{
    PyObject* obj_self = (PyObject*)self;
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);
    int i;
    Sized *v, *e = 0;
    BTreeItem *d;

    if (self->len == self->size)
    {
        if (self->size)
        {
            d = BTree_Realloc(self->data, sizeof(BTreeItem) * self->size * 2);
            if (d == NULL)
                return -1;
            self->data = d;
            self->size *= 2;
        }
        else
        {
            d = BTree_Malloc(sizeof(BTreeItem) * 2);
            if (d == NULL)
                return -1;
            self->data = d;
            self->size = 2;
        }
    }

    if (self->len)
    {
        long max_size = _max_internal_size(self);
        if (max_size < 0) return -1;

        d = self->data + index;
        v = d->child;
        /* Create a new object of the same type as the target value */
        PyTypeObject* tp = Py_TYPE(v);
        e = (Sized *)tp->tp_alloc(tp, 0);
        if (e == NULL)
            return -1;

        UNLESS(per_use((cPersistentObject*)v, capi_struct))
        {
            Py_DECREF(e);
            return -1;
        }

        /* Now split between the original (v) and the new (e)
         * at the midpoint*/
        if (SameType_Check(self, v))
            i = BTree_split((BTree *)v, -1, (BTree *)e);
        else
            i = bucket_split((Bucket *)v, -1, (Bucket *)e);
        per_allow_deactivation((cPersistentObject*)v);

        if (i < 0)
        {
            Py_DECREF(e);
            assert(PyErr_Occurred());
            return -1;
        }

        index++;
        d++;
        if (self->len > index)    /* Shift up the old values one array slot */
            memmove(d+1, d, sizeof(BTreeItem)*(self->len-index));

        if (SameType_Check(self, v))
        {
            COPY_KEY(d->key, BTREE(e)->data->key);

            /* We take the unused reference from e, so there's no
                reason to INCREF!
            */
            /* INCREF_KEY(self->data[1].key); */
        }
        else
        {
            COPY_KEY(d->key, BUCKET(e)->keys[0]);
            INCREF_KEY(d->key);
        }
        d->child = e;
        self->len++;

        if (self->len >= max_size * 2)    /* the root is huge */
            return BTree_split_root(self, noval);
    }
    else
    {
        /* The BTree is empty.  Create an empty bucket.  See CAUTION in
        * the comments preceding.
        */
        assert(index == 0);
        d = self->data;
        d->child = BTree_newBucket(self);
        if (d->child == NULL)
            return -1;
        self->len = 1;
        Py_INCREF(d->child);
        self->firstbucket = (Bucket *)d->child;
    }

    return 0;
}

/* Return the rightmost bucket reachable from following child pointers
 * from self.  The caller gets a new reference to this bucket.  Note that
 * bucket 'next' pointers are not followed:  if self is an interior node
 * of a BTree, this returns the rightmost bucket in that node's subtree.
 * In case of error, returns NULL.
 *
 * self must not be a ghost; this isn't checked.  The result may be a ghost.
 *
 * Pragmatics:  Note that the rightmost bucket's last key is the largest
 * key in self's subtree.
 */
static Bucket *
BTree_lastBucket(BTree *self)
{
    PyObject* obj_self = (PyObject*)self;
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);
    Sized *pchild;
    Bucket *result;

    UNLESS (self->data && self->len)
    {
        IndexError(-1); /* is this the best action to take? */
        return NULL;
    }

    pchild = self->data[self->len - 1].child;
    if (SameType_Check(self, pchild))
    {
        self = BTREE(pchild);
        if (!per_use((cPersistentObject*)self, capi_struct))
            return NULL;
        result = BTree_lastBucket(self);
        per_allow_deactivation((cPersistentObject*)self);
        capi_struct->accessed((cPersistentObject*)self);
    }
    else
    {
        Py_INCREF(pchild);
        result = BUCKET(pchild);
    }
    return result;
}

static int
BTree_deleteNextBucket(BTree *self)
{
    PyObject* obj_self = (PyObject*)self;
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);
    Bucket *b;

    UNLESS (per_use((cPersistentObject*)self, capi_struct))
        return -1;

    b = BTree_lastBucket(self);
    if (b == NULL)
        goto err;
    if (Bucket_deleteNextBucket(b) < 0)
        goto err;

    Py_DECREF(b);
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);

    return 0;

err:
    Py_XDECREF(b);
    per_allow_deactivation((cPersistentObject*)self);
    return -1;
}

/*
** _BTree_clear
**
** Clears out all of the values in the BTree (firstbucket, keys, and
** children); leaving self an empty BTree.
**
** Arguments:    self    The BTree
**
** Returns:     0    on success
**        -1    on failure
**
** Internal:  Deallocation order is important.  The danger is that a long
** list of buckets may get freed "at once" via decref'ing the first bucket,
** in which case a chain of consequenct Py_DECREF calls may blow the stack.
** Luckily, every bucket has a refcount of at least two, one due to being a
** BTree node's child, and another either because it's not the first bucket in
** the chain (so the preceding bucket points to it), or because firstbucket
** points to it.  By clearing in the natural depth-first, left-to-right
** order, the BTree->bucket child pointers prevent Py_DECREF(bucket->next)
** calls from freeing bucket->next, and the maximum stack depth is equal
** to the height of the tree.
**/
static int
_BTree_clear(BTree *self)
{
    const int len = self->len;

    if (self->firstbucket)
    {
        /* Obscure:  The first bucket is pointed to at least by
        * self->firstbucket and data[0].child of whichever BTree node it's
        * a child of.  However, if persistence is enabled then the latter
        * BTree node may be a ghost at this point, and so its pointers "don't
        * count":  we can only rely on self's pointers being intact.
        */
#ifdef PERSISTENT
        ASSERT(Py_REFCNT(self->firstbucket) > 0,
            "Invalid firstbucket pointer", -1);
#else
        ASSERT(Py_REFCNT(self->firstbucket) > 1,
            "Invalid firstbucket pointer", -1);
#endif
        Py_CLEAR(self->firstbucket);
    }

    if (self->data)
    {
        if (len > 0) /* 0 is special because key 0 is trash */
        {
            Py_CLEAR(self->data[0].child);
        }

        for (int i = 1; i < len; ++i)
        {
#ifdef KEY_TYPE_IS_PYOBJECT
            Py_CLEAR(self->data[i].key);
#endif
            Py_CLEAR(self->data[i].child);
        }
        free(self->data);
        self->data = NULL;
    }

    self->len = self->size = 0;
    return 0;
}

/*
  Set (value != 0) or delete (value=0) a tree item.

  If unique is non-zero, then only change if the key is
  new.

  If noval is non-zero, then don't set a value (the tree
  is a set).

  Return:
  -1  error
  0  successful, and number of entries didn't change
  >0  successful, and number of entries did change

  Internal
  There are two distinct return values > 0:

  1  Successful, number of entries changed, but firstbucket did not go away.

  2  Successful, number of entries changed, firstbucket did go away.
  This can only happen on a delete (value == NULL).  The caller may
  need to change its own firstbucket pointer, and in any case *someone*
  needs to adjust the 'next' pointer of the bucket immediately preceding
  the bucket that went away (it needs to point to the bucket immediately
  following the bucket that went away).
*/
static int
_BTree_set(BTree *self, PyObject *keyarg, PyObject *value,
           int unique, int noval)
{
    PyObject* obj_self = (PyObject*)self;
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);
    int changed = 0;    /* did I mutate? */
    int min;            /* index of child I searched */
    BTreeItem *d;       /* self->data[min] */
    int childlength;    /* len(self->data[min].child) */
    int status;         /* our return value; and return value from callee */
    int self_was_empty; /* was self empty at entry? */

    KEY_TYPE key;
    int copied = 1;

    COPY_KEY_FROM_ARG(key, keyarg, copied);
    if (!copied)
        return -1;
#ifdef KEY_CHECK_ON_SET
    if (value && !KEY_CHECK_ON_SET(keyarg))
        return -1;
#endif

    if (!per_use((cPersistentObject*)self, capi_struct))
        return -1;

    self_was_empty = self->len == 0;
    if (self_was_empty)
    {
        /* We're empty.  Make room. */
        if (value)
        {
            if (BTree_grow(self, 0, noval) < 0)
                goto Error;
        }
        else
        {
            /* Can't delete a key from an empty BTree. */
            PyErr_SetObject(PyExc_KeyError, keyarg);
            goto Error;
        }
    }

    /* Find the right child to search, and hand the work off to it. */
    BTREE_SEARCH(min, self, key, goto Error);
    d = self->data + min;

#ifdef PERSISTENT
    if (capi_struct->readCurrent((cPersistentObject*)(self)) < 0) goto Error;
#endif

    if (SameType_Check(self, d->child))
        status = _BTree_set(BTREE(d->child), keyarg, value, unique, noval);
    else
    {
        int bucket_changed = 0;
        status = _bucket_set(BUCKET(d->child), keyarg,
                            value, unique, noval, &bucket_changed);
#ifdef PERSISTENT
        /* If a BTree contains only a single bucket, BTree.__getstate__()
        * includes the bucket's entire state, and the bucket doesn't get
        * an oid of its own.  So if we have a single oid-less bucket that
        * changed, it's *our* oid that should be marked as changed -- the
        * bucket doesn't have one.
        */
        if (bucket_changed
            && self->len == 1
            && self->data[0].child->oid == NULL)
        {
            changed = 1;
        }
#endif
    }
    if (status == 0)
        goto Done;
    if (status < 0)
        goto Error;
    assert(status == 1 || status == 2);

    /* The child changed size.  Get its new size.  Note that since the tree
    * rooted at the child changed size, so did the tree rooted at self:
    * our status must be >= 1 too.
    */
    UNLESS(per_use((cPersistentObject*)d->child, capi_struct))
        goto Error;
    childlength = d->child->len;
    per_allow_deactivation((cPersistentObject*)d->child);
    capi_struct->accessed((cPersistentObject*)d->child);

    if (value)
    {
        /* A bucket got bigger -- if it's "too big", split it. */
        int toobig;

        assert(status == 1);    /* can be 2 only on deletes */
        if (SameType_Check(self, d->child)) {
            long max_size = _max_internal_size(self);
            if (max_size < 0) return -1;
            toobig = childlength > max_size;
        }
        else {
            long max_size = _max_leaf_size(self);
            if (max_size < 0) return -1;
            toobig = childlength > max_size;
        }
        if (toobig) {
            if (BTree_grow(self, min, noval) < 0)
                goto Error;
            changed = 1;        /* BTree_grow mutated self */
        }
        goto Done;      /* and status still == 1 */
    }

    /* A bucket got smaller.  This is much harder, and despite that we
    * don't try to rebalance the tree.
    */

    if (min && childlength)
    {  /* We removed a key. but the node child is non-empty.  If the
        deleted key is the node key, then update the node key using
        the smallest key of the node child.

        This doesn't apply to the 0th node, whos key is unused.
        */
        int _cmp = 1;
        TEST_KEY_SET_OR(_cmp, key, d->key) goto Error;
        if (_cmp == 0) /* Need to replace key with first key from child */
        {
            Bucket *bucket;

            if (SameType_Check(self, d->child))
            {
                UNLESS(per_use((cPersistentObject*)d->child, capi_struct))
                    goto Error;
                bucket = BTREE(d->child)->firstbucket;
                per_allow_deactivation((cPersistentObject*)d->child);
                capi_struct->accessed((cPersistentObject*)d->child);
            }
            else
                bucket = BUCKET(d->child);

            UNLESS(per_use((cPersistentObject*)bucket, capi_struct))
                goto Error;
            DECREF_KEY(d->key);
            COPY_KEY(d->key, bucket->keys[0]);
            INCREF_KEY(d->key);
            per_allow_deactivation((cPersistentObject*)bucket);
            capi_struct->accessed((cPersistentObject*)bucket);
            if (capi_struct->changed((cPersistentObject*)self) < 0)
                    goto Error;
        }
    }

    if (status == 2)
    {
        /* The child must be a BTree because bucket.set never returns 2 */
        /* Two problems to solve:  May have to adjust our own firstbucket,
        * and the bucket that went away needs to get unlinked.
        */
        if (min)
        {
            /* This wasn't our firstbucket, so no need to adjust ours (note
            * that it can't be the firstbucket of any node above us either).
            * Tell "the tree to the left" to do the unlinking.
            */
            if (BTree_deleteNextBucket(BTREE(d[-1].child)) < 0)
                goto Error;
            status = 1;     /* we solved the child's firstbucket problem */
        }
        else
        {
            /* This was our firstbucket.  Update to new firstbucket value. */
            Bucket *nextbucket;
            UNLESS(per_use((cPersistentObject*)d->child, capi_struct))
                goto Error;
            nextbucket = BTREE(d->child)->firstbucket;
            per_allow_deactivation((cPersistentObject*)d->child);
            capi_struct->accessed((cPersistentObject*)d->child);

            Py_XINCREF(nextbucket);
            Py_DECREF(self->firstbucket);
            self->firstbucket = nextbucket;
            changed = 1;

            /* The caller has to do the unlinking -- we can't.  Also, since
            * it was our firstbucket, it may also be theirs.
            */
            assert(status == 2);
        }
    }

    /* If the child isn't empty, we're done!  We did all that was possible for
    * us to do with the firstbucket problems the child gave us, and since the
    * child isn't empty don't create any new firstbucket problems of our own.
    */
    if (childlength)
        goto Done;

    /* The child became empty:  we need to remove it from self->data.
    * But first, if we're a bottom-level node, we've got more bucket-fiddling
    * to set up.
    */
    if (! SameType_Check(self, d->child))
    {
        /* We're about to delete a bucket,
         * so need to adjust bucket pointers.*/
        if (min)
        {
            /* It's not our first bucket, so we can tell the previous
            * bucket to adjust its reference to it.  It can't be anyone
            * else's first bucket either, so the caller needn't do anything.
            */
            if (Bucket_deleteNextBucket(BUCKET(d[-1].child)) < 0)
                goto Error;
            /* status should be 1, and already is:  if it were 2, the
            * block above would have set it to 1 in its min != 0 branch.
            */
            assert(status == 1);
        }
        else
        {
            Bucket *nextbucket;
            /* It's our first bucket.  We can't unlink it directly. */
            /* 'changed' will be set true by the deletion code following. */
            UNLESS(per_use((cPersistentObject*)d->child, capi_struct))
                goto Error;
            nextbucket = BUCKET(d->child)->next;
            per_allow_deactivation((cPersistentObject*)d->child);
            capi_struct->accessed((cPersistentObject*)d->child);

            Py_XINCREF(nextbucket);
            Py_DECREF(self->firstbucket);
            self->firstbucket = nextbucket;

            status = 2; /* giving our caller a new firstbucket problem */
        }
    }

    /* Remove the child from self->data. */
    Py_DECREF(d->child);
#ifdef KEY_TYPE_IS_PYOBJECT
    if (min)
    {
        DECREF_KEY(d->key);
    }
    else if (self->len > 1)
    {
        /* We're deleting the first child of a BTree with more than one
        * child.  The key at d+1 is about to be shifted into slot 0,
        * and hence never to be referenced again (the key in slot 0 is
        * trash).
        */
        DECREF_KEY((d+1)->key);
    }
    /* Else min==0 and len==1:  we're emptying the BTree entirely, and
    * there is no key in need of decrefing.
    */
#endif
    --self->len;
    if (min < self->len)
        memmove(d, d+1, (self->len - min) * sizeof(BTreeItem));
    changed = 1;

Done:
#ifdef PERSISTENT
    if (changed)
    {
        if (capi_struct->changed((cPersistentObject*)self) < 0)
            goto Error;
    }
#endif
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return status;

Error:
    assert(PyErr_Occurred());
    if (self_was_empty)
    {
        /* BTree_grow may have left the BTree in an invalid state.  Make
        * sure the tree is a legitimate empty tree.
        */
        _BTree_clear(self);
    }
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return -1;
}

/*
** BTree_setitem
**
** wrapper for _BTree_set
**
** Arguments:    self    The BTree
**        key    The key to insert
**        v    The value to insert
**
** Returns    -1    on failure
**         0    on success
*/
static int
BTree_setitem(BTree *self, PyObject *key, PyObject *v)
{
    if (_BTree_set(self, key, v, 0, 0) < 0)
        return -1;
    return 0;
}

#ifdef PERSISTENT
static PyObject *
BTree__p_deactivate(BTree *self, PyObject *args, PyObject *keywords)
{
    PyObject* obj_self = (PyObject*)self;
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);

    int ghostify = 1;
    PyObject *force = NULL;

    if (args && PyTuple_GET_SIZE(args) > 0)
    {
        PyErr_SetString(PyExc_TypeError,
                        "_p_deactivate takes not positional arguments");
        return NULL;
    }
    if (keywords)
    {
        int size = PyDict_Size(keywords);
        force = PyDict_GetItemString(keywords, "force");
        if (force)
            size--;
        if (size)
        {
            PyErr_SetString(PyExc_TypeError,
                            "_p_deactivate only accepts keyword arg force");
            return NULL;
        }
    }

    /*
      Always clear our node size cache, whether we're in a jar or not. It is
      only read from the type anyway, and we'll do so on the next write after
      we get activated.
    */
    self->max_internal_size = 0;
    self->max_leaf_size = 0;

    if (self->jar && self->oid)
    {
        ghostify = self->state == cPersistent_UPTODATE_STATE;
        if (!ghostify && force)
        {
            if (PyObject_IsTrue(force))
                ghostify = 1;
            if (PyErr_Occurred())
                return NULL;
        }
        if (ghostify)
        {
            if (_BTree_clear(self) < 0)
                return NULL;
            capi_struct->ghostify((cPersistentObject*)self);
        }
    }

    Py_INCREF(Py_None);
    return Py_None;
}
#endif

static PyObject *
BTree_clear(BTree *self)
{
    PyObject* obj_self = (PyObject*)self;
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);

    UNLESS (per_use((cPersistentObject*)self, capi_struct)) return NULL;

    if (self->len)
    {
        if (_BTree_clear(self) < 0)
            goto err;
        if (capi_struct->changed((cPersistentObject*)self) < 0)
            goto err;
    }

    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);

    Py_INCREF(Py_None);
    return Py_None;

err:
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return NULL;
}

/*
 * Return:
 *
 * For an empty BTree (self->len == 0), None.
 *
 * For a BTree with one child (self->len == 1), and that child is a bucket,
 * and that bucket has a NULL oid, a one-tuple containing a one-tuple
 * containing the bucket's state:
 *
 *     (
 *         (
 *              child[0].__getstate__(),
 *         ),
 *     )
 *
 * Else a two-tuple.  The first element is a tuple interleaving the BTree's
 * keys and direct children, of size 2*self->len - 1 (key[0] is unused and
 * is not saved).  The second element is the firstbucket:
 *
 *     (
 *          (child[0], key[1], child[1], key[2], child[2], ...,
 *                                       key[len-1], child[len-1]),
 *          self->firstbucket
 *     )
 *
 * In the above, key[i] means self->data[i].key, and similarly for child[i].
 */
static PyObject *
BTree_getstate(BTree *self)
{
    PyObject* obj_self = (PyObject*)self;
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);
    PyObject *r = NULL;
    PyObject *o;
    int i;
    int l;

    UNLESS (per_use((cPersistentObject*)self, capi_struct))
        return NULL;

    if (self->len)
    {
        r = PyTuple_New(self->len * 2 - 1);
        if (r == NULL)
            goto err;

        if (self->len == 1
            && Py_TYPE(self->data->child) != Py_TYPE(self)
#ifdef PERSISTENT
            && BUCKET(self->data->child)->oid == NULL
#endif
            )
        {
            /* We have just one bucket. Save its data directly. */
            o = bucket_getstate((Bucket *)self->data->child);
            if (o == NULL)
                goto err;
            PyTuple_SET_ITEM(r, 0, o);
            ASSIGN(r, Py_BuildValue("(O)", r));
        }
        else
        {
            for (i=0, l=0; i < self->len; i++)
            {
                if (i)
                {
                    COPY_KEY_TO_OBJECT(o, self->data[i].key);
                    PyTuple_SET_ITEM(r, l, o);
                    l++;
                }
                o = (PyObject *)self->data[i].child;
                Py_INCREF(o);
                PyTuple_SET_ITEM(r,l,o);
                l++;
            }
            ASSIGN(r, Py_BuildValue("OO", r, self->firstbucket));
        }

    }
    else
    {
        r = Py_None;
        Py_INCREF(r);
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

static int
_BTree_setstate(BTree *self, PyObject *state, int noval)
{
    PyObject* obj_self = (PyObject*)self;
    PyTypeObject *bucket_type = _get_bucket_type(obj_self);
    PyTypeObject *set_type = _get_set_type(obj_self);
    PyObject *items;
    PyObject *firstbucket = NULL;
    BTreeItem *d;
    int len;
    int l;
    int i;
    int copied=1;
    PyTypeObject *leaftype = (noval ? set_type : bucket_type);

    if (_BTree_clear(self) < 0)
        return -1;

    /* The state of a BTree can be one of the following:
        None -- an empty BTree
        A one-tuple -- a single bucket btree
        A two-tuple -- a BTree with more than one bucket
        See comments for BTree_getstate() for the details.
    */

    if (state == Py_None)
        return 0;

    if (!PyArg_ParseTuple(state, "O|O:__setstate__", &items, &firstbucket))
        return -1;

    if (!PyTuple_Check(items))
    {
        PyErr_SetString(PyExc_TypeError,
                        "tuple required for first state element");
        return -1;
    }

    len = PyTuple_Size(items);
    ASSERT(len >= 0, "_BTree_setstate: items tuple has negative size", -1);
    len = (len + 1) / 2;

    assert(len > 0); /* If the BTree is empty, it's state is None. */
    assert(self->size == 0); /* We called _BTree_clear(). */

    self->data = BTree_Malloc(sizeof(BTreeItem) * len);
    if (self->data == NULL)
        return -1;
    self->size = len;

    for (i = 0, d = self->data, l = 0; i < len; i++, d++)
    {
        PyObject *v;
        if (i)
        { /* skip the first key slot */
            COPY_KEY_FROM_ARG(d->key, PyTuple_GET_ITEM(items, l), copied);
            l++;
            if (!copied)
                return -1;
            INCREF_KEY(d->key);
        }
        v = PyTuple_GET_ITEM(items, l);
        if (PyTuple_Check(v))
        {
            /* Handle the special case in __getstate__() for a BTree
                with a single bucket. */
            d->child = BTree_newBucket(self);
            if (!d->child)
                return -1;
            if (noval)
            {
                if (_set_setstate(BUCKET(d->child), v) < 0)
                return -1;
            }
            else
            {
                if (_bucket_setstate(BUCKET(d->child), v) < 0)
                return -1;
            }
        }
        else
        {
            if (!(SameType_Check(self, v) ||
                  PyObject_IsInstance(v, (PyObject *)leaftype)))
            {
                PyErr_Format(PyExc_TypeError,
                             "tree child %s is neither %s nor %s",
                             Py_TYPE(v)->tp_name,
                             Py_TYPE(self)->tp_name,
                             leaftype->tp_name);
                return -1;
            }

            d->child = (Sized *)v;
            Py_INCREF(v);
        }
        l++;
    }

    if (!firstbucket)
        firstbucket = (PyObject *)self->data->child;

    if (!PyObject_IsInstance(firstbucket, (PyObject *)leaftype))
    {
        PyErr_SetString(PyExc_TypeError,
                        "No firstbucket in non-empty BTree");
        return -1;
    }
    self->firstbucket = BUCKET(firstbucket);
    Py_INCREF(firstbucket);
#ifndef PERSISTENT
    /* firstbucket is also the child of some BTree node, but that node may
    * be a ghost if persistence is enabled.
    */
    assert(Py_REFCNT(self->firstbucket) > 1);
#endif
    self->len = len;

    return 0;
}

static PyObject *
BTree_setstate(BTree *self, PyObject *arg)
{
    PyObject* obj_self = (PyObject*)self;
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);
    int r;

    per_prevent_deactivation((cPersistentObject*)self);
    r = _BTree_setstate(self, arg, 0);
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);

    if (r < 0)
        return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}

#ifdef PERSISTENT

/* Recognize the special cases of a BTree that's empty or contains a single
 * bucket.  In the former case, return a borrowed reference to Py_None.
 * In this single-bucket case, the bucket state is embedded directly in the
 * BTree state, like so:
 *
 *     (
 *         (
 *              thebucket.__getstate__(),
 *         ),
 *     )
 *
 * When this obtains, return a borrowed reference to thebucket.__getstate__().
 * Else return NULL with an exception set.  The exception should always be
 * ConflictError then, but may be TypeError if the state makes no sense at all
 * for a BTree (corrupted or hostile state).
 */
PyObject *
get_bucket_state(PyObject* obj_self, PyObject *t)
{
    if (t == Py_None)
        return Py_None;        /* an empty BTree */
    if (! PyTuple_Check(t))
    {
        PyErr_SetString(
            PyExc_TypeError,
            "_p_resolveConflict: expected tuple or None for state");
        return NULL;
    }

    if (PyTuple_GET_SIZE(t) == 2)
    {
        /* A non-degenerate BTree. */
        return merge_error(obj_self, -1, -1, -1, 11);
    }

    /* We're in the one-bucket case. */

    if (PyTuple_GET_SIZE(t) != 1)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "_p_resolveConflict: expected 1- or 2-tuple for state");
        return NULL;
    }

    t = PyTuple_GET_ITEM(t, 0);
    if (! PyTuple_Check(t) || PyTuple_GET_SIZE(t) != 1)
    {
        PyErr_SetString(PyExc_TypeError,
                        "_p_resolveConflict: expected 1-tuple containing "
                        "bucket state");
        return NULL;
    }

    t = PyTuple_GET_ITEM(t, 0);
    if (! PyTuple_Check(t))
    {
        PyErr_SetString(
            PyExc_TypeError,
            "_p_resolveConflict: expected tuple for bucket state");
        return NULL;
    }

    return t;
}

/* Tricky.  The only kind of BTree conflict we can actually potentially
 * resolve is the special case of a BTree containing a single bucket,
 * in which case this becomes a fancy way of calling the bucket conflict
 * resolution code.
 */
static PyObject *
BTree__p_resolveConflict(BTree *self, PyObject *args)
{
    PyObject *obj_self = (PyObject*)self;
    PyTypeObject *btree_type = _get_btree_type(obj_self);
    PyTypeObject *bucket_type = _get_bucket_type(obj_self);
    PyTypeObject *set_type = _get_set_type(obj_self);
    PyObject *s[3];
    PyObject *x;
    PyObject *y;
    PyObject *z;

    if (!PyArg_ParseTuple(args, "OOO", &x, &y, &z))
        return NULL;

    s[0] = get_bucket_state(obj_self, x);
    if (s[0] == NULL)
        return NULL;
    s[1] = get_bucket_state(obj_self, y);
    if (s[1] == NULL)
        return NULL;
    s[2] = get_bucket_state(obj_self, z);
    if (s[2] == NULL)
        return NULL;

    if (PyObject_IsInstance((PyObject *)self, (PyObject *)btree_type))
        x = _bucket__p_resolveConflict(bucket_type, s);
    else
        x = _bucket__p_resolveConflict(set_type, s);

    if (x == NULL)
        return NULL;

    return Py_BuildValue("((N))", x);
}
#endif

/*
  BTree_findRangeEnd -- Find one end, expressed as a bucket and
  position, for a range search.

  If low, return bucket and index of the smallest item >= key,
  otherwise return bucket and index of the largest item <= key.

  If exclude_equal, exact matches aren't acceptable; if one is found,
  move right if low, or left if !low (this is for range searches exclusive
  of an endpoint).

  Return:
  -1      Error; offset and bucket unchanged
  0      Not found; offset and bucket unchanged
  1      Correct bucket and offset stored; the caller owns a new reference
  to the bucket.

  Internal:
  We do binary searches in BTree nodes downward, at each step following
  C(i) where K(i) <= key < K(i+1).  As always, K(i) <= C(i) < K(i+1) too.
  (See Maintainer.txt for the meaning of that notation.)  That eventually
  leads to a bucket where we do Bucket_findRangeEnd.  That usually works,
  but there are two cases where it can fail to find the correct answer:

  1. On a low search, we find a bucket with keys >= K(i), but that doesn't
  imply there are keys in the bucket >= key.  For example, suppose
  a bucket has keys in 1..100, its successor's keys are in 200..300, and
  we're doing a low search on 150.  We'll end up in the first bucket,
  but there are no keys >= 150 in it.  K(i+1) > key, though, and all
  the keys in C(i+1) >= K(i+1) > key, so the first key in the next
  bucket (if any) is the correct result.  This is easy to find by
  following the bucket 'next' pointer.

  2. On a high search, again that the keys in the bucket are >= K(i)
  doesn't imply that any key in the bucket is <= key, but it's harder
  for this to fail (and an earlier version of this routine didn't
  catch it):  if K(i) itself is in the bucket, it works (then
  K(i) <= key is *a* key in the bucket that's in the desired range).
  But when keys get deleted from buckets, they aren't also deleted from
  BTree nodes, so there's no guarantee that K(i) is in the bucket.
  For example, delete the smallest key S from some bucket, and S
  remains in the interior BTree nodes.  Do a high search for S, and
  the BTree nodes direct the search to the bucket S used to be in,
  but all keys remaining in that bucket are > S.  The largest key in
  the *preceding* bucket (if any) is < K(i), though, and K(i) <= key,
  so the largest key in the preceding bucket is < key and so is the
  proper result.

  This is harder to get at efficiently, as buckets are linked only in
  the increasing direction.  While we're searching downward,
  deepest_smaller is set to the  node deepest in the tree where
  we *could* have gone to the left of C(i).  The rightmost bucket in
  deepest_smaller's subtree is the bucket preceding the bucket we find
  at first.  This is clumsy to get at, but efficient.
*/
static int
BTree_findRangeEnd(BTree *self, PyObject *keyarg, int low, int exclude_equal,
                   Bucket **bucket, int *offset)
{
    PyObject* obj_self = (PyObject*)self;
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);
    Sized *deepest_smaller = NULL;      /* last possibility to move left */
    int deepest_smaller_is_btree = 0;   /* Boolean; if false, it's a bucket */
    Bucket *pbucket;
    int self_got_rebound = 0;   /* Boolean; when true, deactivate self */
    int result = -1;            /* Until proven innocent */
    int i;
    KEY_TYPE key;
    int copied = 1;

    COPY_KEY_FROM_ARG(key, keyarg, copied);
    UNLESS (copied)
        return -1;

    /* We don't need to check 'per_use(self, capi_struct)' and return -1
     * on fail, because the caller does.
     */
    UNLESS (self->data && self->len)
        return 0;

    /* Search downward until hitting a bucket, stored in pbucket. */
    for (;;)
    {
        Sized *pchild;
        int pchild_is_btree;

        BTREE_SEARCH(i, self, key, goto Done);
        pchild = self->data[i].child;
        pchild_is_btree = SameType_Check(self, pchild);
        if (i)
        {
            deepest_smaller = self->data[i-1].child;
            deepest_smaller_is_btree = pchild_is_btree;
        }

        if (pchild_is_btree)
        {
            if (self_got_rebound)
            {
                per_allow_deactivation((cPersistentObject*)self);
                capi_struct->accessed((cPersistentObject*)self);
            }
            self = BTREE(pchild);
            self_got_rebound = 1;
            if (!per_use((cPersistentObject*)self, capi_struct))
                return -1;
        }
        else
        {
            pbucket = BUCKET(pchild);
            break;
        }
    }

    /* Search the bucket for a suitable key. */
    i = Bucket_findRangeEnd(pbucket, keyarg, low, exclude_equal, offset);
    if (i < 0)
        goto Done;
    if (i > 0)
    {
        Py_INCREF(pbucket);
        *bucket = pbucket;
        result = 1;
        goto Done;
    }
    /* This may be one of the two difficult cases detailed in the comments. */
    if (low)
    {
        Bucket *next;

        UNLESS(per_use((cPersistentObject*)pbucket, capi_struct)) goto Done;
        next = pbucket->next;
        if (next) {
        result = 1;
        Py_INCREF(next);
        *bucket = next;
        *offset = 0;
        }
        else
        result = 0;
        per_allow_deactivation((cPersistentObject*)pbucket);
        capi_struct->accessed((cPersistentObject*)pbucket);
    }
    /* High-end search:  if it's possible to go left, do so. */
    else if (deepest_smaller)
    {
        if (deepest_smaller_is_btree)
        {
            UNLESS(per_use((cPersistentObject*)deepest_smaller, capi_struct))
                goto Done;
            /* We own the reference this returns. */
            pbucket = BTree_lastBucket(BTREE(deepest_smaller));
            per_allow_deactivation((cPersistentObject*)deepest_smaller);
            capi_struct->accessed((cPersistentObject*)deepest_smaller);
            if (pbucket == NULL)
                    goto Done;   /* error */
        }
        else
        {
            pbucket = BUCKET(deepest_smaller);
            Py_INCREF(pbucket);
        }
        UNLESS(per_use((cPersistentObject*)pbucket, capi_struct))
            goto Done;
        result = 1;
        *bucket = pbucket;  /* transfer ownership to caller */
        *offset = pbucket->len - 1;
        per_allow_deactivation((cPersistentObject*)pbucket);
        capi_struct->accessed((cPersistentObject*)pbucket);
    }
    else
        result = 0;     /* simply not found */

Done:
    if (self_got_rebound)
    {
        per_allow_deactivation((cPersistentObject*)self);
        capi_struct->accessed((cPersistentObject*)self);
    }
    return result;
}

static PyObject *
BTree_maxminKey(BTree *self, PyObject *args, int min)
{
    PyObject* obj_self = (PyObject*)self;
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);
    PyObject *key=0;
    Bucket *bucket = NULL;
    int offset, rc;
    int empty_tree = 1;

    UNLESS (PyArg_ParseTuple(args, "|O", &key))
        return NULL;

    UNLESS (per_use((cPersistentObject*)self, capi_struct))
        return NULL;

    UNLESS (self->data && self->len)
        goto empty;

    /* Find the  range */

    if (key && key != Py_None)
    {
        if ((rc = BTree_findRangeEnd(
                    self, key, min, 0, &bucket, &offset)) <= 0
        ) {
            if (rc < 0)
                goto err;
            empty_tree = 0;
            goto empty;
        }
        per_allow_deactivation((cPersistentObject*)self);
        capi_struct->accessed((cPersistentObject*)self);
        UNLESS (per_use((cPersistentObject*)bucket, capi_struct))
        {
            Py_DECREF(bucket);
            return NULL;
        }
    }
    else if (min)
    {
        bucket = self->firstbucket;
        per_allow_deactivation((cPersistentObject*)self);
        capi_struct->accessed((cPersistentObject*)self);
        if (!per_use((cPersistentObject*)bucket, capi_struct))
            return NULL;
        Py_INCREF(bucket);
        offset = 0;
    }
    else
    {
        bucket = BTree_lastBucket(self);
        per_allow_deactivation((cPersistentObject*)self);
        capi_struct->accessed((cPersistentObject*)self);
        UNLESS (per_use((cPersistentObject*)bucket, capi_struct))
        {
            Py_DECREF(bucket);
            return NULL;
        }
        assert(bucket->len);
        offset = bucket->len - 1;
    }

    COPY_KEY_TO_OBJECT(key, bucket->keys[offset]);
    per_allow_deactivation((cPersistentObject*)bucket);
    capi_struct->accessed((cPersistentObject*)bucket);
    Py_DECREF(bucket);

    return key;

empty:
    PyErr_SetString(PyExc_ValueError,
                    empty_tree ? "empty tree" :
                    "no key satisfies the conditions");
err:
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    if (bucket)
    {
        per_allow_deactivation((cPersistentObject*)bucket);
        capi_struct->accessed((cPersistentObject*)bucket);
        Py_DECREF(bucket);
    }
  return NULL;
}

static PyObject *
BTree_minKey(BTree *self, PyObject *args)
{
    return BTree_maxminKey(self, args, 1);
}

static PyObject *
BTree_maxKey(BTree *self, PyObject *args)
{
    return BTree_maxminKey(self, args, 0);
}

/*
** BTree_rangeSearch
**
** Generates a BTreeItems object based on the two indexes passed in,
** being the range between them.
**
*/
static PyObject *
BTree_rangeSearch(BTree *self, PyObject *args, PyObject *kw, char type)
{
    PyObject* obj_self = (PyObject*)self;
    PyObject* module = _get_module(Py_TYPE(obj_self));
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);
    PyObject *min = Py_None;
    PyObject *max = Py_None;
    int excludemin = 0;
    int excludemax = 0;
    int rc;
    Bucket *lowbucket = NULL;
    Bucket *highbucket = NULL;
    int lowoffset;
    int highoffset;
    PyObject *result;

    if (args)
    {
        if (! PyArg_ParseTupleAndKeywords(args, kw, "|OOii", search_keywords,
                                        &min,
                                        &max,
                                        &excludemin,
                                        &excludemax))
        return NULL;
    }

    UNLESS (per_use((cPersistentObject*)self, capi_struct))
        return NULL;

    UNLESS (self->data && self->len)
        goto empty;

    /* Find the low range */
    if (min != Py_None)
    {
        if ((rc = BTree_findRangeEnd(self, min, 1, excludemin,
                                    &lowbucket, &lowoffset)) <= 0)
        {
            if (rc < 0)
                goto err;
            goto empty;
        }
    }
    else
    {
        lowbucket = self->firstbucket;
        lowoffset = 0;
        if (excludemin)
        {
            int bucketlen;
            UNLESS (per_use((cPersistentObject*)lowbucket, capi_struct))
                goto err;
            bucketlen = lowbucket->len;
            per_allow_deactivation((cPersistentObject*)lowbucket);
            capi_struct->accessed((cPersistentObject*)lowbucket);
            if (bucketlen > 1)
                lowoffset = 1;
            else if (self->len < 2)
                goto empty;
            else
            {    /* move to first item in next bucket */
                Bucket *next;
                UNLESS (per_use((cPersistentObject*)lowbucket, capi_struct))
                    goto err;
                next = lowbucket->next;
                per_allow_deactivation((cPersistentObject*)lowbucket);
                capi_struct->accessed((cPersistentObject*)lowbucket);
                assert(next != NULL);
                lowbucket = next;
                /* and lowoffset is still 0 */
                assert(lowoffset == 0);
            }
        }
        Py_INCREF(lowbucket);
    }

    /* Find the high range */
    if (max != Py_None)
    {
        if ((rc = BTree_findRangeEnd(self, max, 0, excludemax,
                                    &highbucket, &highoffset)) <= 0)
        {
            Py_DECREF(lowbucket);
            if (rc < 0)
                goto err;
            goto empty;
        }
    }
    else
    {
        int bucketlen;
        highbucket = BTree_lastBucket(self);
        assert(highbucket != NULL);  /* we know self isn't empty */
        UNLESS (per_use((cPersistentObject*)highbucket, capi_struct))
            goto err_and_decref_buckets;
        bucketlen = highbucket->len;
        per_allow_deactivation((cPersistentObject*)highbucket);
        capi_struct->accessed((cPersistentObject*)highbucket);
        highoffset = bucketlen - 1;
        if (excludemax)
        {
            if (highoffset > 0)
                --highoffset;
            else if (self->len < 2)
                goto empty_and_decref_buckets;
            else /* move to last item of preceding bucket */
            {
                int status;
                assert(highbucket != self->firstbucket);
                Py_DECREF(highbucket);
                status = PreviousBucket(&highbucket, self->firstbucket);
                if (status < 0)
                {
                    Py_DECREF(lowbucket);
                    goto err;
                }
                assert(status > 0);
                Py_INCREF(highbucket);
                UNLESS (per_use((cPersistentObject*)highbucket, capi_struct))
                    goto err_and_decref_buckets;
                highoffset = highbucket->len - 1;
                per_allow_deactivation((cPersistentObject*)highbucket);
                capi_struct->accessed((cPersistentObject*)highbucket);
            }
        }
        assert(highoffset >= 0);
    }

    /* It's still possible that the range is empty, even if min < max.  For
    * example, if min=3 and max=4, and 3 and 4 aren't in the BTree, but 2 and
    * 5 are, then the low position points to the 5 now and the high position
    * points to the 2 now.  They're not necessarily even in the same bucket,
    * so there's no trick we can play with pointer compares to get out
    * cheap in general.
    */
    if (lowbucket == highbucket && lowoffset > highoffset)
        goto empty_and_decref_buckets;      /* definitely empty */

    /* The buckets differ, or they're the same and the offsets show a non-
    * empty range.
    */
    if (min != Py_None && max != Py_None && /* both args user-supplied */
        lowbucket != highbucket)   /* and different buckets */
    {
        KEY_TYPE first;
        KEY_TYPE last;
        int cmp;

        /* Have to check the hard way:  see how the endpoints compare. */
        UNLESS (per_use((cPersistentObject*)lowbucket, capi_struct))
            goto err_and_decref_buckets;
        COPY_KEY(first, lowbucket->keys[lowoffset]);
        per_allow_deactivation((cPersistentObject*)lowbucket);
        capi_struct->accessed((cPersistentObject*)lowbucket);

        UNLESS (per_use((cPersistentObject*)highbucket, capi_struct))
            goto err_and_decref_buckets;
        COPY_KEY(last, highbucket->keys[highoffset]);
        per_allow_deactivation((cPersistentObject*)highbucket);
        capi_struct->accessed((cPersistentObject*)highbucket);

        TEST_KEY_SET_OR(cmp, first, last)
            goto err_and_decref_buckets;
        if (cmp > 0)
                goto empty_and_decref_buckets;
    }

    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);

    result = newBTreeItems(
        module, type, lowbucket, lowoffset, highbucket, highoffset);
    Py_DECREF(lowbucket);
    Py_DECREF(highbucket);
    return result;

err_and_decref_buckets:
    Py_DECREF(lowbucket);
    Py_DECREF(highbucket);

err:
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return NULL;

empty_and_decref_buckets:
    Py_DECREF(lowbucket);
    Py_DECREF(highbucket);

empty:
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return newBTreeItems(module, type, 0, 0, 0, 0);
}

/*
** BTree_keys
*/
static PyObject *
BTree_keys(BTree *self, PyObject *args, PyObject *kw)
{
    return BTree_rangeSearch(self, args, kw, 'k');
}

/*
** BTree_values
*/
static PyObject *
BTree_values(BTree *self, PyObject *args, PyObject *kw)
{
    return BTree_rangeSearch(self, args, kw, 'v');
}

/*
** BTree_items
*/
static PyObject *
BTree_items(BTree *self, PyObject *args, PyObject *kw)
{
    return BTree_rangeSearch(self, args, kw, 'i');
}

static PyObject *
BTree_byValue(BTree *self, PyObject *omin)
{
    PyObject* obj_self = (PyObject*)self;
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);
    PyObject *r=0;
    PyObject *o=0;
    PyObject *item=0;
    VALUE_TYPE min;
    VALUE_TYPE v;
    int copied=1;
    SetIteration it = {0, 0, 1};

    UNLESS (per_use((cPersistentObject*)self, capi_struct))
        return NULL;

    COPY_VALUE_FROM_ARG(min, omin, copied);
    UNLESS(copied)
        return NULL;

    UNLESS (r=PyList_New(0))
        goto err;

    it.set=BTree_rangeSearch(self, NULL, NULL, 'i');
    UNLESS(it.set)
        goto err;

    if (nextBTreeItems(&it) < 0)
        goto err;

    while (it.position >= 0)
    {
        if (TEST_VALUE(it.value, min) >= 0)
        {
            UNLESS (item = PyTuple_New(2))
                goto err;

            COPY_KEY_TO_OBJECT(o, it.key);
            UNLESS (o)
                goto err;
            PyTuple_SET_ITEM(item, 1, o);

            COPY_VALUE(v, it.value);
            NORMALIZE_VALUE(v, min);
            COPY_VALUE_TO_OBJECT(o, v);
            DECREF_VALUE(v);
            UNLESS (o)
                goto err;
            PyTuple_SET_ITEM(item, 0, o);

            if (PyList_Append(r, item) < 0)
                goto err;
            Py_DECREF(item);
            item = 0;
        }
        if (nextBTreeItems(&it) < 0)
            goto err;
    }

    item = PyObject_CallMethodObjArgs(r, str_sort, NULL);
    if(item == NULL)
        goto err;
    Py_DECREF(item); /* Py_None */
    item = PyObject_CallMethodObjArgs(r, str_reverse, NULL);
    if(item == NULL)
        goto err;
    Py_DECREF(item); /* Py_None */

    finiSetIteration(&it);
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    return r;

err:
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    Py_XDECREF(r);
    finiSetIteration(&it);
    Py_XDECREF(item);
    return NULL;
}

/*
** BTree_getm
*/
static PyObject *
BTree_getm(BTree *self, PyObject *args)
{
    PyObject *key, *d=Py_None, *r;

    UNLESS (PyArg_ParseTuple(args, "O|O", &key, &d))
        return NULL;
    if ((r=_BTree_get(self, key, 0, _BGET_REPLACE_TYPE_ERROR)))
        return r;
    UNLESS (BTree_ShouldSuppressKeyError())
        return NULL;
    PyErr_Clear();
    Py_INCREF(d);
    return d;
}

static PyObject *
BTree_setdefault(BTree *self, PyObject *args)
{
    PyObject *key;
    PyObject *failobj; /* default */
    PyObject *value;   /* return value */

    if (! PyArg_UnpackTuple(args, "setdefault", 2, 2, &key, &failobj))
        return NULL;

    value = _BTree_get(self, key, 0, _BGET_ALLOW_TYPE_ERROR);
    if (value != NULL)
        return value;

    /* The key isn't in the tree.  If that's not due to a KeyError exception,
    * pass back the unexpected exception.
    */
    if (! BTree_ShouldSuppressKeyError())
        return NULL;
    PyErr_Clear();

    /* Associate `key` with `failobj` in the tree, and return `failobj`. */
    value = failobj;
    if (_BTree_set(self, key, failobj, 0, 0) < 0)
        value = NULL;
    Py_XINCREF(value);
    return value;
}

/* forward declaration */
static Py_ssize_t
BTree_length_or_nonzero(BTree *self, int nonzero);

static PyObject *
BTree_pop(BTree *self, PyObject *args)
{
    PyObject *key;
    PyObject *failobj = NULL; /* default */
    PyObject *value;          /* return value */

    if (! PyArg_UnpackTuple(args, "pop", 1, 2, &key, &failobj))
        return NULL;

    value = _BTree_get(self, key, 0, _BGET_ALLOW_TYPE_ERROR);
    if (value != NULL)
    {
        /* Delete key and associated value. */
        if (_BTree_set(self, key, NULL, 0, 0) < 0)
        {
            Py_DECREF(value);
            return NULL;;
        }
        return value;
    }

    /* The key isn't in the tree.  If that's not due to a KeyError exception,
    * pass back the unexpected exception.
    */
    if (! BTree_ShouldSuppressKeyError())
        return NULL;

    if (failobj != NULL)
    {
        /* Clear the KeyError and return the explicit default. */
        PyErr_Clear();
        Py_INCREF(failobj);
        return failobj;
    }

    /* No default given.  The only difference in this case is the error
    * message, which depends on whether the tree is empty.
    */
    if (BTree_length_or_nonzero(self, 1) == 0) /* tree is empty */
        PyErr_SetString(PyExc_KeyError, "pop(): BTree is empty");
    return NULL;
}


static PyObject*
BTree_popitem(BTree* self, PyObject* args)
{
    PyObject* key = NULL;
    PyObject* pop_args = NULL;
    PyObject* result_val = NULL;
    PyObject* result = NULL;

    if (PyTuple_Size(args) != 0) {
        PyErr_SetString(PyExc_TypeError, "popitem(): Takes no arguments.");
        return NULL;
    }

    key = BTree_minKey(self, args); /* reuse existing empty tuple. */
    if (!key) {
        PyErr_Clear();
        PyErr_SetString(PyExc_KeyError, "popitem(): empty BTree.");
        return NULL;
    }

    pop_args = PyTuple_Pack(1, key);
    if (pop_args) {
        result_val = BTree_pop(self, pop_args);
        Py_DECREF(pop_args);
        if (result_val) {
            result = PyTuple_Pack(2, key, result_val);
            Py_DECREF(result_val);
        }
    }

    Py_DECREF(key);
    return result;
}



/* Search BTree self for key.  This is the sq_contains slot of the
 * PySequenceMethods.
 *
 * Return:
 *     -1     error
 *      0     not found
 *      1     found
 */
static int
BTree_contains(BTree *self, PyObject *key)
{
    PyObject *asobj = _BTree_get(self, key, 1, _BGET_REPLACE_TYPE_ERROR);
    int result = -1;

    if (asobj != NULL)
    {
        result = PyLong_AsLong(asobj) ? 1 : 0;
        Py_DECREF(asobj);
    }
    else if (BTree_ShouldSuppressKeyError())
    {
        PyErr_Clear();
        result = 0;
    }
    return result;
}

static PyObject *
BTree_has_key(BTree *self, PyObject *key)
{
    int result = -1;
    result = BTree_contains(self, key);
    if (result == -1) {
        return NULL;
    }

    if (result)
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}


static PyObject *
BTree_addUnique(BTree *self, PyObject *args)
{
    int grew;
    PyObject *key, *v;

    UNLESS (PyArg_ParseTuple(args, "OO", &key, &v))
        return NULL;

    if ((grew=_BTree_set(self, key, v, 1, 0)) < 0)
        return NULL;
    return PyLong_FromLong(grew);
}

/**************************************************************************/
/* Iterator support. */

/* A helper to build all the iterators for BTrees and TreeSets.
 * If args is NULL, the iterator spans the entire structure.  Else it's an
 * argument tuple, with optional low and high arguments.
 * kind is 'k', 'v' or 'i'.
 * Returns a BTreeIter object, or NULL if error.
 */
static PyObject *
buildBTreeIter(BTree *self, PyObject *args, PyObject *kw, char kind)
{
    PyObject* obj_self = (PyObject*)self;
    PyObject* module = _get_module(Py_TYPE(obj_self));
    BTreeIter *result = NULL;
    BTreeItems *items = (BTreeItems *)BTree_rangeSearch(self, args, kw, kind);

    if (items)
    {
        result = newBTreeIter(module, items);
        Py_DECREF(items);
    }
    return (PyObject *)result;
}

/* The implementation of iter(BTree_or_TreeSet); the BTree tp_iter slot. */
static PyObject *
BTree_getiter(BTree *self)
{
    return buildBTreeIter(self, NULL, NULL, 'k');
}

/* The implementation of BTree.iterkeys(). */
static PyObject *
BTree_iterkeys(BTree *self, PyObject *args, PyObject *kw)
{
    return buildBTreeIter(self, args, kw, 'k');
}

/* The implementation of BTree.itervalues(). */
static PyObject *
BTree_itervalues(BTree *self, PyObject *args, PyObject *kw)
{
    return buildBTreeIter(self, args, kw, 'v');
}

/* The implementation of BTree.iteritems(). */
static PyObject *
BTree_iteritems(BTree *self, PyObject *args, PyObject *kw)
{
    return buildBTreeIter(self, args, kw, 'i');
}

/* End of iterator support. */


/* Caution:  Even though the _firstbucket attribute is read-only, a program
   could do arbitrary damage to the btree internals.  For example, it could
   call clear() on a bucket inside a BTree.

   We need to decide if the convenience for inspecting BTrees is worth
   the risk.
*/

static struct PyMemberDef BTree_members[] = {
    {"_firstbucket", T_OBJECT, offsetof(BTree, firstbucket), READONLY},
    {NULL}
};

static struct PyMethodDef BTree_methods[] = {
    {"__getstate__", (PyCFunction) BTree_getstate, METH_NOARGS,
     "__getstate__() -> state\n\n"
     "Return the picklable state of the BTree."},

    {"__setstate__", (PyCFunction) BTree_setstate, METH_O,
     "__setstate__(state)\n\n"
     "Set the state of the BTree."},

    {"has_key", (PyCFunction) BTree_has_key, METH_O,
     "has_key(key)\n\n"
     "Return true if the BTree contains the given key."},

    {"keys", (PyCFunction) BTree_keys, METH_VARARGS | METH_KEYWORDS,
     "keys([min, max]) -> list of keys\n\n"
     "Returns the keys of the BTree.  If min and max are supplied, only\n"
     "keys greater than min and less than max are returned."},

    {"values", (PyCFunction) BTree_values, METH_VARARGS | METH_KEYWORDS,
     "values([min, max]) -> list of values\n\n"
     "Returns the values of the BTree.  If min and max are supplied, only\n"
     "values corresponding to keys greater than min and less than max are\n"
     "returned."},

    {"items", (PyCFunction) BTree_items, METH_VARARGS | METH_KEYWORDS,
     "items([min, max]) -> -- list of key, value pairs\n\n"
     "Returns the items of the BTree.  If min and max are supplied, only\n"
     "items with keys greater than min and less than max are returned."},

    {"byValue", (PyCFunction) BTree_byValue, METH_O,
     "byValue(min) ->  list of value, key pairs\n\n"
     "Returns list of value, key pairs where the value is >= min.  The\n"
     "list is sorted by value.  Note that items() returns keys in the\n"
     "opposite order."},

    {"get", (PyCFunction) BTree_getm, METH_VARARGS,
     "get(key[, default=None]) -> Value for key or default\n\n"
     "Return the value or the default if the key is not found."},

    {"setdefault", (PyCFunction) BTree_setdefault, METH_VARARGS,
     "D.setdefault(k, d) -> D.get(k, d), also set D[k]=d if k not in D.\n\n"
     "Return the value like get() except that if key is missing, d is both\n"
     "returned and inserted into the BTree as the value of k."},

    {"pop", (PyCFunction) BTree_pop, METH_VARARGS,
     "D.pop(k[, d]) -> v, remove key and return the corresponding value.\n\n"
     "If key is not found, d is returned if given, otherwise KeyError\n"
     "is raised."},

    {"popitem", (PyCFunction)BTree_popitem, METH_VARARGS,
     "D.popitem() -> (k, v), remove and return some (key, value) pair\n"
     "as a 2-tuple; but raise KeyError if D is empty."},

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

    {"insert", (PyCFunction)BTree_addUnique, METH_VARARGS,
     "insert(key, value) -> 0 or 1\n\n"
     "Add an item if the key is not already used. Return 1 if the item was\n"
     "added, or 0 otherwise."},

    {"update", (PyCFunction)Mapping_update, METH_O,
     "update(collection)\n\n Add the items from the given collection."},

    {"iterkeys", (PyCFunction)BTree_iterkeys, METH_VARARGS | METH_KEYWORDS,
     "B.iterkeys([min[,max]]) -> an iterator over the keys of B"},

    {"itervalues",
     (PyCFunction)BTree_itervalues, METH_VARARGS | METH_KEYWORDS,
     "B.itervalues([min[,max]]) -> an iterator over the values of B"},

    {"iteritems", (PyCFunction)BTree_iteritems, METH_VARARGS | METH_KEYWORDS,
     "B.iteritems([min[,max]]) -> an iterator over the (key, value) "
     "items of B"},

    {"_check", (PyCFunction)BTree_check, METH_NOARGS,
     "Perform sanity check on BTree, and raise exception if flawed."},

#ifdef PERSISTENT
    {"_p_resolveConflict",
     (PyCFunction)BTree__p_resolveConflict, METH_VARARGS,
     "_p_resolveConflict() -- Reinitialize from a newly created copy"},

    {"_p_deactivate",
     (PyCFunction) BTree__p_deactivate, METH_VARARGS | METH_KEYWORDS,
     "_p_deactivate()\n\nReinitialize from a newly created copy."},
#endif
    {NULL, NULL}
};

static int
BTree_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *v = NULL;

    BTREE(self)->max_leaf_size = 0;
    BTREE(self)->max_internal_size = 0;

    if (!PyArg_ParseTuple(args, "|O:" MOD_NAME_PREFIX "BTree", &v))
        return -1;

    if (v)
        return update_from_seq(self, v);
    else
        return 0;
}

static void
BTree_dealloc(BTree *self)
{
    PyObject* obj_self = (PyObject*)self;
#if USE_HEAP_ALLOCATED_TYPES
    PyTypeObject* tp = Py_TYPE(obj_self);
#endif
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);

    PyObject_GC_UnTrack(obj_self);
    if (self->state != cPersistent_GHOST_STATE) {
        _BTree_clear(self);
    }
    if (capi_struct) {
        capi_struct->pertype->tp_dealloc(obj_self);
    } else {
        PyErr_SetString(PyExc_RuntimeError, "Cannot find persistence CAPI");
    }
#if USE_HEAP_ALLOCATED_TYPES
    /* Hmmm, is Persistent going to do this for us? */
    Py_DECREF(tp);
#endif
}

static int
BTree_traverse(BTree *self, visitproc visit, void *arg)
{
    PyObject* obj_self = (PyObject*)self;
#if USE_HEAP_ALLOCATED_TYPES
    PyTypeObject* tp = Py_TYPE(obj_self);
    Py_VISIT(tp);
#endif
    PyTypeObject *btree_type = _get_btree_type(obj_self);
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);

    int i;
    int len;

    if (capi_struct == NULL)
        return -1;

    if (Py_TYPE(self) == btree_type)
        assert(Py_TYPE(self)->tp_dictoffset == 0);

    /* Call our base type's traverse function.
     *
     * Because BTrees are subclasses of Peristent, there must be one.
    */
    if (capi_struct->pertype->tp_traverse((PyObject *)self, visit, arg) < 0)
        return -1;

    /* If this is registered with the persistence system, cleaning up cycles
    * is the database's problem.  It would be horrid to unghostify BTree
    * nodes here just to chase pointers every time gc runs.
    */
    if (self->state == cPersistent_GHOST_STATE)
        return 0;

    len = self->len;

#ifdef KEY_TYPE_IS_PYOBJECT
    /* Keys are Python objects so need to be traversed.  Note that the
    * key 0 slot is unused and should not be traversed.
    */
    for (i = 1; i < len; i++)
        Py_VISIT(self->data[i].key);
#endif

    /* Children are always pointers, and child 0 is legit. */
    for (i = 0; i < len; i++)
        Py_VISIT(self->data[i].child);

    Py_VISIT(self->firstbucket);

    return 0;
}

static int
BTree_tp_clear(BTree *self)
{
    if (self->state != cPersistent_GHOST_STATE)
        _BTree_clear(self);
    return 0;
}

/*
 * Return the number of elements in a BTree.  nonzero is a Boolean, and
 * when true requests just a non-empty/empty result.  Testing for emptiness
 * is efficient (constant-time).  Getting the true length takes time
 * proportional to the number of leaves (buckets).
 *
 * Return:
 *     When nonzero true:
 *          -1  error
 *           0  empty
 *           1  not empty
 *     When nonzero false (possibly expensive!):
 *          -1  error
 *        >= 0  number of elements.
 */
static Py_ssize_t
BTree_length_or_nonzero(BTree *self, int nonzero)
{
    PyObject* obj_self = (PyObject*)self;
    cPersistenceCAPIstruct* capi_struct = _get_capi_struct(obj_self);
    int result;
    Bucket *b;
    Bucket *next;

    if (!per_use((cPersistentObject*)self, capi_struct))
        return -1;
    b = self->firstbucket;
    per_allow_deactivation((cPersistentObject*)self);
    capi_struct->accessed((cPersistentObject*)self);
    if (nonzero)
        return b != NULL;

    result = 0;
    while (b)
    {
        if (!per_use((cPersistentObject*)b, capi_struct))
            return -1;
        result += b->len;
        next = b->next;
        per_allow_deactivation((cPersistentObject*)b);
        capi_struct->accessed((cPersistentObject*)b);
        b = next;
    }
    return result;
}

static Py_ssize_t
BTree_length(BTree *self)
{
    return BTree_length_or_nonzero(self, 0);
}

static Py_ssize_t
BTree_nonzero(BTree *self)
{
  return BTree_length_or_nonzero(self, 1);
}


static char BTree__name__[] = MODULE_NAME MOD_NAME_PREFIX "BTree";
static char BTree__doc__[] = "Persistent BTree type";

#if USE_STATIC_TYPES

static PyNumberMethods BTree_as_number_for_nonzero = {
    .nb_subtract                = bucket_sub,
    .nb_bool                    = (inquiry)BTree_nonzero,
    .nb_and                     = bucket_and,
    .nb_or                      = bucket_or,
};

static PySequenceMethods BTree_as_sequence = {
    .sq_contains                = (objobjproc)BTree_contains,
};

static PyMappingMethods BTree_as_mapping = {
    .mp_length                  = (lenfunc)BTree_length,
    .mp_subscript               = (binaryfunc)BTree_get,
    .mp_ass_subscript           = (objobjargproc)BTree_setitem,
};

static PyTypeObject BTree_type_def = {
    PyVarObject_HEAD_INIT(&BTreeType_type_def, 0)
    .tp_name                    = BTree__name__,
    .tp_doc                     = BTree__doc__,
    .tp_basicsize               = sizeof(BTree),
    .tp_flags                   = Py_TPFLAGS_DEFAULT |
                                  Py_TPFLAGS_HAVE_GC |
                                  Py_TPFLAGS_BASETYPE,
    .tp_init                    = BTree_init,
    .tp_iter                    = (getiterfunc)BTree_getiter,
    .tp_traverse                = (traverseproc)BTree_traverse,
    .tp_clear                   = (inquiry)BTree_tp_clear,
    .tp_dealloc                 = (destructor)BTree_dealloc,
    .tp_methods                 = BTree_methods,
    .tp_members                 = BTree_members,
    .tp_as_number               = &BTree_as_number_for_nonzero,
    .tp_as_sequence             = &BTree_as_sequence,
    .tp_as_mapping              = &BTree_as_mapping,
};

#else

static PyType_Slot BTree_type_slots[] = {
    {Py_tp_doc,                 BTree__doc__},
    {Py_tp_init,                BTree_init},
    {Py_tp_iter,                (getiterfunc)BTree_getiter},
    {Py_tp_traverse,            (traverseproc)BTree_traverse},
    {Py_tp_clear,               (inquiry)BTree_tp_clear},
    {Py_tp_dealloc,             (destructor)BTree_dealloc},
    {Py_tp_methods,             BTree_methods},
    {Py_tp_members,             BTree_members},
    {Py_nb_subtract,            bucket_sub},
    {Py_nb_bool,                (inquiry)BTree_nonzero},
    {Py_nb_and,                 bucket_and},
    {Py_nb_or,                  bucket_or},
    {Py_sq_contains,            (objobjproc)BTree_contains},
    {Py_mp_length,              (lenfunc)BTree_length},
    {Py_mp_subscript,           (binaryfunc)BTree_get},
    {Py_mp_ass_subscript,       (objobjargproc)BTree_setitem},
    {0,                         NULL}
};

static PyType_Spec BTree_type_spec = {
    .name                       = BTree__name__,
    .basicsize                  = sizeof(BTree),
    .flags                      = Py_TPFLAGS_DEFAULT |
                                  Py_TPFLAGS_HAVE_GC |
                                  Py_TPFLAGS_IMMUTABLETYPE |
                                  Py_TPFLAGS_BASETYPE,
    .slots                      = BTree_type_slots
};

#endif
