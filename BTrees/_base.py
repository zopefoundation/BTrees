##############################################################################
#
# Copyright 2011 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Python BTree implementation
"""

from struct import pack
from struct import unpack
from struct import error as struct_error

import persistent

from BTrees.Interfaces import BTreesConflictError

_marker = object()


class _Base(persistent.Persistent):

    _key_type = list

    def __init__(self, items=None):
        self.clear()
        if items:
            self.update(items)


class _BucketBase(_Base):

    def clear(self):
        self._keys = self._key_type()
        self._next = None

    def __len__(self):
        return len(self._keys)

    @property
    def size(self):
        return len(self._keys)

    def _deleteNextBucket(self):
        next = self._next
        if next is not None:
            self._next = next._next

    def _search(self, key):
        # Return non-negative index on success
        # return -(insertion_index + 1) on fail
        low = 0
        keys = self._keys
        high = len(keys)
        while low < high:
            i = (low + high) // 2
            k = keys[i]
            if k == key:
                return i
            if k < key:
                low = i + 1
            else:
                high = i
        return -1 - low

    def minKey(self, key=_marker):
        if key is _marker:
            return self._keys[0]
        key = self._to_key(key)
        index = self._search(key)
        if index >= 0:
            return key
        index = -index - 1
        if index < len(self._keys):
            return self._keys[index]
        else:
            raise ValueError("no key satisfies the conditions")

    def maxKey(self, key=_marker):
        if key is _marker:
            return self._keys[-1]
        key = self._to_key(key)
        index = self._search(key)
        if index >= 0:
            return key
        else:
            index = -index-1
            if index:
                return self._keys[index-1]
            else:
                raise ValueError("no key satisfies the conditions")

    def _range(self, min=_marker, max=_marker,
               excludemin=False, excludemax=False):
        if min is _marker:
            start = 0
            if excludemin:
                start = 1
        else:
            min = self._to_key(min)
            start = self._search(min)
            if start >= 0:
                if excludemin:
                    start += 1
            else:
                start = -start - 1
        if max is _marker:
            end = len(self._keys)
            if excludemax:
                end -= 1
        else:
            max = self._to_key(max)
            end = self._search(max)
            if end >= 0:
                if not excludemax:
                    end += 1
            else:
                end = -end - 1

        return start, end

    def keys(self, *args, **kw):
        start, end = self._range(*args, **kw)
        return self._keys[start:end]

    def iterkeys(self, *args, **kw):
        if not (args or kw):
            return iter(self._keys)
        keys = self._keys
        return (keys[i] for i in xrange(*self._range(*args, **kw)))

    def __iter__(self):
        return iter(self._keys)

    def __contains__(self, key):
        return (self._search(self._to_key(key)) >= 0)

    has_key = __contains__


class _SetIteration(object):

    def __init__(self, set, useValues=False, default=None):
        if set is None:
            set = ()
        self.set = set
        if useValues:
            try:
                itmeth = set.iteritems
            except AttributeError:
                itmeth = set.__iter__
                useValues = False
            else:
                self.value = None
        else:
            itmeth = set.__iter__

        self.useValues = useValues
        self._next = itmeth().next
        self.active = True
        self.position = 0
        self.value = default
        self.advance()

    def advance(self):
        try:
            if self.useValues:
                self.key, self.value = self._next()
            else:
                self.key = self._next()
            self.position += 1
        except StopIteration:
            self.active = False
            self.position = -1

        return self


class _MappingBase(_Base):

    def setdefault(self, key, value):
        return self._set(self._to_key(key), self._to_value(value), True)[1]

    def pop(self, key, default=_marker):
        try:
            return self._del(self._to_key(key))[1]
        except KeyError:
            if default is _marker:
                raise
            return default

    def update(self, items):
        if hasattr(items, 'iteritems'):
            items = items.iteritems()
        elif hasattr(items, 'items'):
            items = items.items()

        set = self.__setitem__
        for i in items:
            set(*i)

    def __setitem__(self, key, value):
        # Enforce test that key has non-default comparison.
        if ( getattr(key, '__lt__', None) is None and
            getattr(key, '__cmp__', None) is None):
            raise TypeError("Can't use default __cmp__")
        self._set(self._to_key(key), self._to_value(value))

    def __delitem__(self, key):
        self._del(self._to_key(key))

    def _p_resolveConflict(self, s_old, s_com, s_new):
        b_old = self.__class__()
        if s_old is not None:
            b_old.__setstate__(s_old)
        b_com = self.__class__()
        if s_com is not None:
            b_com.__setstate__(s_com)
        b_new = self.__class__()
        if s_new is not None:
            b_new.__setstate__(s_new)
        if (b_com._next != b_old._next or
            b_new._next != b_old._next):
            raise BTreesConflictError(-1, -1, -1, 0)

        if not b_com or not b_new:
            raise BTreesConflictError(-1, -1, -1, 12)

        i_old = _SetIteration(b_old, True)
        i_com = _SetIteration(b_com, True)
        i_new = _SetIteration(b_new, True)

        def merge_error(reason):
            return BTreesConflictError(
                i_old.position, i_com.position, i_new.position, reason)

        result = self.__class__()

        def merge_output(it):
            result._keys.append(it.key)
            result._values.append(it.value)
            it.advance()

        while i_old.active and i_com.active and i_new.active:
            cmp12 = cmp(i_old.key, i_com.key)
            cmp13 = cmp(i_old.key, i_new.key)
            if cmp12==0:
                if cmp13==0:
                    if i_com.value == i_old.value:
                        result[i_old.key] = i_new.value
                    elif i_new.value == i_old.value:
                        result[i_old.key] = i_com.value
                    else:
                        raise merge_error(1)
                    i_old.advance()
                    i_com.advance()
                    i_new.advance()
                elif (cmp13 > 0): # insert in new
                    merge_output(i_new)
                elif i_old.value == i_com.value: # deleted new
                    if i_new.position == 1:
                        # Deleted the first item.  This will modify the
                        # parent node, so we don't know if merging will be
                        # safe
                        raise merge_error(13)
                    i_old.advance()
                    i_com.advance()
                else:
                    raise merge_error(2)
            elif cmp13 == 0:
                if cmp12 > 0: # insert committed
                    merge_output(i_com)
                elif i_old.value == i_new.value: # delete committed
                    if i_com.position == 1:
                        # Deleted the first item.  This will modify the
                        # parent node, so we don't know if merging will be
                        # safe
                        raise merge_error(13)
                    i_old.advance()
                    i_new.advance()
                else:
                    raise merge_error(3)
            else: # both keys changed
                cmp23 = cmp(i_com.key, i_new.key)
                if cmp23 == 0:
                    raise merge_error(4)
                if cmp12 > 0: # insert committed
                    if cmp23 > 0: # insert i_new first
                        merge_output(i_new)
                    else:
                        merge_output(i_com)
                elif cmp13 > 0: # insert i_new
                    merge_output(i_new)
                else:
                    raise merge_error(5) # both deleted same key

        while i_com.active and i_new.active: # new inserts
            cmp23 = cmp(i_com.key, i_new.key)
            if cmp23 == 0:
                raise merge_error(6) # dueling insert
            if cmp23 > 0: # insert new
                merge_output(i_new)
            else: # insert committed
                merge_output(i_com)

        while i_old.active and i_com.active: # new deletes rest of original
            cmp12 = cmp(i_old.key, i_com.key)
            if cmp12 > 0: # insert committed
                merge_output(i_com)
            elif cmp12 == 0 and (i_old.value == i_com.value): # del in new
                i_old.advance()
                i_com.advance()
            else: # dueling deletes or delete and change
                raise merge_error(7)

        while i_old.active and i_new.active:
            # committed deletes rest of original
            cmp13 = cmp(i_old.key, i_new.key)
            if cmp13 > 0: # insert new
                merge_output(i_new)
            elif cmp13 == 0 and (i_old.value == i_new.value):
                # deleted in committed
                i_old.advance()
                i_new.advance()
            else: # dueling deletes or delete and change
                raise merge_error(8)

        if i_old.active: # dueling deletes
            raise merge_error(9)

        while i_com.active:
            merge_output(i_com)

        while i_new.active:
            merge_output(i_new)

        if len(result._keys) == 0:
            # If the output bucket is empty, conflict resolution doesn't have
            # enough info to unlink it from its containing BTree correctly.
            raise merge_error(10)

        result._next = b_old._next
        return result.__getstate__()


class _SetBase(_Base):

    #_next = None
    def add(self, key):
        return self._set(self._to_key(key))[0]

    insert = add

    def remove(self, key):
        self._del(self._to_key(key))

    def update(self, items):
        add = self.add
        for i in items:
            add(i)

    def _p_resolveConflict(self, s_old, s_com, s_new):
        b_old = self.__class__()
        if s_old is not None:
            b_old.__setstate__(s_old)
        b_com = self.__class__()
        if s_com is not None:
            b_com.__setstate__(s_com)
        b_new = self.__class__()
        if s_new is not None:
            b_new.__setstate__(s_new)
        if (b_com._next != b_old._next or
            b_new._next != b_old._next):
            raise BTreesConflictError(-1, -1, -1, 0)

        if not b_com or not b_new:
            raise BTreesConflictError(-1, -1, -1, 12)

        i_old = _SetIteration(b_old, True)
        i_com = _SetIteration(b_com, True)
        i_new = _SetIteration(b_new, True)

        def merge_error(reason):
            return BTreesConflictError(
                i_old.position, i_com.position, i_new.position, reason)

        result = self.__class__()

        def merge_output(it):
            result._keys.append(it.key)
            it.advance()

        while i_old.active and i_com.active and i_new.active:
            cmp12 = cmp(i_old.key, i_com.key)
            cmp13 = cmp(i_old.key, i_new.key)
            if cmp12 == 0:
                if cmp13 == 0:
                    result.add(i_old.key)
                    i_old.advance()
                    i_com.advance()
                    i_new.advance()
                elif cmp13 > 0: # insert in new
                    merge_output(i_new)
                else: # deleted new
                    if i_new.position == 1:
                        # Deleted the first item.  This will modify the
                        # parent node, so we don't know if merging will be
                        # safe
                        raise merge_error(13)
                    i_old.advance()
                    i_com.advance()
            elif cmp13 == 0:
                if cmp12 > 0: # insert committed
                    merge_output(i_com)
                else: # delete committed
                    if i_com.position == 1:
                        # Deleted the first item.  This will modify the
                        # parent node, so we don't know if merging will be
                        # safe
                        raise merge_error(13)
                    i_old.advance()
                    i_new.advance()
            else: # both keys changed
                cmp23 = cmp(i_com.key, i_new.key)
                if cmp23 == 0:
                    raise merge_error(4)
                if cmp12 > 0: # insert committed
                    if cmp23 > 0: # insert i_new first
                        merge_output(i_new)
                    else:
                        merge_output(i_com)
                elif cmp13 > 0: # insert i_new
                    merge_output(i_new)
                else:
                    raise merge_error(5) # both deleted same key

        while i_com.active and i_new.active: # new inserts
            cmp23 = cmp(i_com.key, i_new.key)
            if cmp23 == 0:
                raise merge_error(6) # dueling insert
            if cmp23 > 0: # insert new
                merge_output(i_new)
            else: # insert committed
                merge_output(i_com)

        while i_old.active and i_com.active: # new deletes rest of original
            cmp12 = cmp(i_old.key, i_com.key)
            if cmp12 > 0: # insert committed
                merge_output(i_com)
            elif cmp12 == 0: # del in new
                i_old.advance()
                i_com.advance()
            else: # dueling deletes or delete and change
                raise merge_error(7)

        while i_old.active and i_new.active:
            # committed deletes rest of original
            cmp13 = cmp(i_old.key, i_new.key)
            if cmp13 > 0: # insert new
                merge_output(i_new)
            elif cmp13 == 0: # deleted in committed
                i_old.advance()
                i_new.advance()
            else: # dueling deletes or delete and change
                raise merge_error(8)

        if i_old.active: # dueling deletes
            raise merge_error(9)

        while i_com.active:
            merge_output(i_com)

        while i_new.active:
            merge_output(i_new)

        if len(result._keys) == 0:
            # If the output bucket is empty, conflict resolution doesn't have
            # enough info to unlink it from its containing BTree correctly.
            raise merge_error(10)

        result._next = b_old._next
        return result.__getstate__()


class Bucket(_MappingBase, _BucketBase):

    _value_type = list
    _to_value = lambda x: x
    VALUE_SAME_CHECK = False

    def clear(self):
        _BucketBase.clear(self)
        self._values = self._value_type()

    def get(self, key, default=None):
        index = self._search(self._to_key(key))
        if index < 0:
            return default
        return self._values[index]

    def __getitem__(self, key):
        index = self._search(self._to_key(key))
        if index < 0:
            raise KeyError(key)
        return self._values[index]

    def _set(self, key, value, ifunset=False):
        """Set a value

        Return: status, value

        Status is:
              None if no change
                  0 if change, but not size change
                  1 if change and size change
        """
        index = self._search(key)
        if index >= 0:
            if (ifunset or
                self.VALUE_SAME_CHECK and value == self._values[index]
                ):
                return None, self._values[index]
            self._p_changed = True
            self._values[index] = value
            return 0, value
        else:
            self._p_changed = True
            index = -index - 1
            self._keys.insert(index, key)
            self._values.insert(index, value)
            return 1, value

    def _del(self, key):
        index = self._search(key)
        if index >= 0:
            self._p_changed = True
            del self._keys[index]
            return 0, self._values.pop(index)
        raise KeyError(key)

    def _split(self, index=-1):
        if index < 0 or index >= len(self._keys):
            index = len(self._keys) / 2
        new_instance = self.__class__()
        new_instance._keys = self._keys[index:]
        new_instance._values = self._values[index:]
        del self._keys[index:]
        del self._values[index:]
        new_instance._next = self._next
        self._next = new_instance
        return new_instance

    def values(self, *args, **kw):
        start, end = self._range(*args, **kw)
        return self._values[start:end]

    def itervalues(self, *args, **kw):
        values = self._values
        return (values[i] for i in xrange(*self._range(*args, **kw)))

    def items(self, *args, **kw):
        keys = self._keys
        values = self._values
        return [(keys[i], values[i])
                    for i in xrange(*self._range(*args, **kw))]

    def iteritems(self, *args, **kw):
        keys = self._keys
        values = self._values
        return ((keys[i], values[i])
                    for i in xrange(*self._range(*args, **kw)))

    def __getstate__(self):
        keys = self._keys
        values = self._values
        data = []
        for i in range(len(keys)):
            data.append(keys[i])
            data.append(values[i])
        data = tuple(data)

        if self._next:
            return data, self._next
        return (data, )

    def __setstate__(self, state):
        if not isinstance(state[0], tuple):
            raise TypeError("tuple required for first state element")

        self.clear()
        if len(state) == 2:
            state, self._next = state
        else:
            self._next = None
            state = state[0]

        keys = self._keys
        values = self._values
        for i in range(0, len(state), 2):
            keys.append(state[i])
            values.append(state[i+1])


class Set(_SetBase, _BucketBase):

    def __getstate__(self):
        data = tuple(self._keys)
        if self._next:
            return data, self._next
        return (data, )

    def __setstate__(self, state):
        if not isinstance(state[0], tuple):
            raise TypeError('tuple required for first state element')

        self.clear()
        if len(state) == 2:
            state, self._next = state
        else:
            self._next = None
            state = state[0]

        self._keys.extend(state)


    def _set(self, key, value=None, ifunset=False):
        index = self._search(key)
        if index < 0:
            index = -index - 1
            self._keys.insert(index, key)
            return True, None
        return False, None

    def _del(self, key):
        index = self._search(key)
        if index >= 0:
            self._p_changed = True
            del self._keys[index]
            return 0, 0
        raise KeyError(key)

    def __getitem__(self, i):
        return self._keys[i]

    def _split(self, index=-1):
        if index < 0 or index >= len(self._keys):
            index = len(self._keys) / 2
        new_instance = self.__class__()
        new_instance._keys = self._keys[index:]
        del self._keys[index:]
        new_instance._next = self._next
        self._next = new_instance
        return new_instance


class _TreeItem(object):

    __slots__ = 'key', 'child'

    def __init__(self, key, child):
        self.key = key
        self.child = child


class _Tree(_MappingBase):

    def clear(self):
        self._data = []
        self._firstbucket = None

    def __nonzero__(self):
        return bool(self._data)

    def __len__(self):
        l = 0
        bucket = self._firstbucket
        while bucket is not None:
            l += len(bucket._keys)
            bucket = bucket._next
        return l

    @property
    def size(self):
        return len(self._data)

    def _search(self, key):
        data = self._data
        if data:
            lo = 0
            hi = len(data)
            i = hi//2
            while i > lo:
                cmp_ = cmp(data[i].key, key)
                if cmp_ < 0:
                    lo = i
                elif cmp_ > 0:
                    hi = i
                else:
                    break
                i = (lo+hi)//2
            return i
        return -1

    def _findbucket(self, key):
        index = self._search(key)
        if index >= 0:
            child = self._data[index].child
            if isinstance(child, self._bucket_type):
                return child
            return child._findbucket(key)

    def __contains__(self, key):
        return key in (self._findbucket(self._to_key(key)) or ())

    def has_key(self, key):
        index = self._search(key)
        if index < 0:
            return False
        r = self._data[index].child.has_key(key)
        return r and r + 1

    def keys(self, min=_marker, max=_marker,
             excludemin=False, excludemax=False,
             itertype='iterkeys'):
        if not self._data:
            return ()

        if min != _marker:
            min = self._to_key(min)
            bucket = self._findbucket(min)
        else:
            bucket = self._firstbucket

        iterargs = min, max, excludemin, excludemax

        return _TreeItems(bucket, itertype, iterargs)

    def iterkeys(self, min=_marker, max=_marker,
                 excludemin=False, excludemax=False):
        return iter(self.keys(min, max, excludemin, excludemax))

    def __iter__(self):
        return iter(self.keys())

    def minKey(self, min=_marker):
        if min is _marker:
            bucket = self._firstbucket
        else:
            min = self._to_key(min)
            bucket = self._findbucket(min)
        if bucket is not None:
            return bucket.minKey(min)
        raise ValueError('empty tree')

    def maxKey(self, max=_marker):
        data = self._data
        if not data:
            raise ValueError('empty tree')
        if max is _marker:
            return data[-1].child.maxKey()

        max = self._to_key(max)
        index = self._search(max)
        if index and data[index].child.minKey() > max:
            index -= 1
        return data[index].child.maxKey(max)


    def _set(self, key, value=None, ifunset=False):
        if (self._p_jar is not None and
            self._p_oid is not None and
            self._p_serial is not None):
            self._p_jar.readCurrent(self)
        data = self._data
        if data:
            index = self._search(key)
            child = data[index].child
        else:
            index = 0
            child = self._bucket_type()
            self._firstbucket = child
            data.append(_TreeItem(None, child))

        result = child._set(key, value, ifunset)
        grew = result[0]
        if grew and child.size > child.MAX_SIZE:
            self._grow(child, index)
        elif (grew is not None and
              child.__class__ is self._bucket_type and
              len(data) == 1 and
              child._p_oid is None
              ):
            self._p_changed = 1
        return result

    def _grow(self, child, index):
        self._p_changed = True
        new_child = child._split()
        self._data.insert(index+1, _TreeItem(new_child.minKey(), new_child))
        if len(self._data) > self.MAX_SIZE * 2:
            self._split_root()

    def _split_root(self):
        child = self.__class__()
        child._data = self._data
        child._firstbucket = self._firstbucket
        self._data = [_TreeItem(None, child)]
        self._grow(child, 0)

    def _split(self, index=None):
        data = self._data
        if index is None:
            index = len(data)//2

        next = self.__class__()
        next._data = data[index:]
        first = data[index]
        del data[index:]
        if isinstance(first.child, self.__class__):
            next._firstbucket = first.child._firstbucket
        else:
            next._firstbucket = first.child;
        return next

    def _del(self, key):
        if (self._p_jar is not None and
            self._p_oid is not None and
            self._p_serial is not None):
            self._p_jar.readCurrent(self)
        data = self._data
        if data:
            index = self._search(key)
            child = data[index].child
        else:
            raise KeyError(key)

        removed_first_bucket, value = child._del(key)

        if index and child.size and key == data[index].key:
            self._p_changed = True
            data[index].key = child.minKey()

        if removed_first_bucket:
            if index:
                data[index-1].child._deleteNextBucket()
                removed_first_bucket = False # clear flag
            else:
                self._firstbucket = child._firstbucket

        if not child.size:
            if child.__class__ is self._bucket_type:
                if index:
                    data[index-1].child._deleteNextBucket()
                else:
                    self._firstbucket = child._next
                    removed_first_bucket = True
            del data[index]

        return removed_first_bucket, value

    def _deleteNextBucket(self):
        self._data[-1].child._deleteNextBucket()

    def __getstate__(self):
        data = self._data

        if not data:
            return None

        if (len(data) == 1 and
            data[0].child.__class__ is not self.__class__ and
            data[0].child._p_oid is None
            ):
            return ((data[0].child.__getstate__(), ), )

        sdata = []
        for item in data:
            if sdata:
                sdata.append(item.key)
                sdata.append(item.child)
            else:
                sdata.append(item.child)

        return tuple(sdata), self._firstbucket

    def __setstate__(self, state):
        if state and not isinstance(state[0], tuple):
            raise TypeError('tuple required for first state element')

        self.clear()
        if state is None:
            return

        if len(state) == 1:
            bucket = self._bucket_type()
            bucket.__setstate__(state[0][0])
            state = [bucket], bucket

        data, self._firstbucket = state
        data = list(reversed(data))

        self._data.append(_TreeItem(None, data.pop()))
        while data:
            key = data.pop()
            child = data.pop()
            self._data.append(_TreeItem(key, child))

    def _assert(self, condition, message):
        if not condition:
            raise AssertionError(message)

    def _check(self, nextbucket=None):
        data = self._data
        assert_ = self._assert
        if not data:
            assert_(self._firstbucket is None,
                    "Empty BTree has non-NULL firstbucket")
            return
        assert_(self._firstbucket is not None,
                "Non-empty BTree has NULL firstbucket")

        child_class = data[0].child.__class__
        for i in data:
            assert_(i.child is not None, "BTree has NULL child")
            assert_(i.child.__class__ is child_class,
                    "BTree children have different types");
            assert_(i.child.size, "Bucket length < 1")

        if child_class is self.__class__:
            assert_(self._firstbucket is data[0].child._firstbucket,
                    "BTree has firstbucket different than "
                    "its first child's firstbucket")
            for i in range(len(data)-1):
               data[i].child._check(data[i+1].child._firstbucket)
            data[-1].child._check(nextbucket)
        elif child_class is self._bucket_type:
            assert_(self._firstbucket is data[0].child,
                    "Bottom-level BTree node has inconsistent firstbucket "
                    "belief")
            for i in range(len(data)-1):
                assert_(data[i].child._next is data[i+1].child,
                       "Bucket next pointer is damaged")
            assert_(data[-1].child._next is nextbucket,
                    "Bucket next pointer is damaged")
        else:
            assert_(False, "Incorrect child type")

    def _p_resolveConflict(self, old, com, new):
        s_old = _get_simple_btree_bucket_state(old)
        s_com = _get_simple_btree_bucket_state(com)
        s_new = _get_simple_btree_bucket_state(new)
        return ((
            self._bucket_type()._p_resolveConflict(s_old, s_com, s_new), ), )


def _get_simple_btree_bucket_state(state):
    if state is None:
        return state
    if not isinstance(state, tuple):
        raise TypeError("_p_resolveConflict: expected tuple or None for state")
    if len(state) == 2:
        raise BTreesConflictError(-1, -1, -1, 11)
    if len(state) != 1:
        raise TypeError("_p_resolveConflict: expected 1- or 2-tuple for state")
    state = state[0]
    if not isinstance(state, tuple) or len(state) != 1:
        raise TypeError("_p_resolveConflict: expected 1-tuple containing "
                        "bucket state")
    state = state[0]
    if not isinstance(state, tuple):
        raise TypeError("_p_resolveConflict: expected tuple for bucket state")
    return state


class _TreeItems(object):

    def __init__(self, firstbucket, itertype, iterargs):
        self.firstbucket = firstbucket
        self.itertype = itertype
        self.iterargs = iterargs
        self.index = -1
        self.it = iter(self)

    def __getitem__(self, i):
        if isinstance(i, slice):
            return list(self)[i]
        if i < 0:
            i = len(self) + i
            if i < 0:
                raise IndexError(i)

        if i < self.index:
            self.index = -1
            self.it = iter(self)

        while i > self.index:
            try:
                self.v = self.it.next()
            except StopIteration:
                raise IndexError(i)
            else:
                self.index += 1
        return self.v

    def __len__(self):
        try:
            return self._len
        except AttributeError:
            i = 0
            for _ in self:
                i += 1
            self._len = i
            return self._len

    def __iter__(self):
        bucket = self.firstbucket
        itertype = self.itertype
        iterargs = self.iterargs
        done = 0
        # Note that we don't mind if the first bucket yields no
        # results due to an idiosyncrasy in how range searches are done.
        while bucket is not None:
            for k in getattr(bucket, itertype)(*iterargs):
                yield k
                done = 0
            if done:
                return
            bucket = bucket._next
            done = 1


class Tree(_Tree):

    def get(self, key, default=None):
        bucket = self._findbucket(key)
        if bucket:
            return bucket.get(key, default)
        return default

    def __getitem__(self, key):
        bucket = self._findbucket(key)
        if bucket:
            return bucket[key]
        raise KeyError(key)

    def values(self, min=_marker, max=_marker,
               excludemin=False, excludemax=False):
        return self.keys(min, max, excludemin, excludemax, 'itervalues')

    def itervalues(self, min=_marker, max=_marker,
                   excludemin=False, excludemax=False):
        return iter(self.values(min, max, excludemin, excludemax))

    def items(self, min=_marker, max=_marker,
              excludemin=False, excludemax=False):
        return self.keys(min, max, excludemin, excludemax, 'iteritems')

    def iteritems(self, min=_marker, max=_marker,
                  excludemin=False, excludemax=False):
        return iter(self.items(min, max, excludemin, excludemax))

    def byValue(self, min):
        return sorted((v, k) for (k, v) in self.iteritems() if v >= min)

    def insert(self, key, value):
        return bool(self._set(key, value, True)[0])


class TreeSet(_SetBase, _Tree):
    _p_resolveConflict = _Tree._p_resolveConflict


def _set_operation(s1, s2,
                   usevalues1=False, usevalues2=False,
                   w1=1, w2=1,
                   c1=True, c12=True, c2=True):
    MERGE_DEFAULT = getattr(s1, 'MERGE_DEFAULT', None)
    i1 = _SetIteration(s1, usevalues1, MERGE_DEFAULT)
    i2 = _SetIteration(s2, usevalues2, MERGE_DEFAULT)
    merge = i1.useValues or i2.useValues
    MERGE = getattr(s1, 'MERGE', None)
    if merge:
        MERGE_WEIGHT = getattr(s1, 'MERGE_WEIGHT')
        if MERGE is None and c12 and i1.useValues and i2.useValues:
            raise TypeError("invalid set operation")

        if (not i1.useValues) and i2.useValues:
            t = i1; i1 = i2; i2 = t
            t = w1; w1 = w2; w2 = t
            t = c1; c1 = c2; c2 = t

        if MERGE_DEFAULT is None:
            if i1.useValues:
                if (not i2.useValues) and c2:
                    raise TypeError("invalid set operation")
            else:
                if c1 or c12:
                    raise TypeError("invalid set operation")

        r = s1._mapping_type()

        def copy(i, w):
            r._keys.append(i.key)
            r._values.append(MERGE_WEIGHT(i.value, w))
    else:
        r = s1._set_type()
        def copy(i, w):
            r._keys.append(i.key)

    while i1.active and i2.active:
        cmp_ = cmp(i1.key, i2.key)
        if cmp_ < 0:
            if c1:
                copy(i1, w1)
            i1.advance()
        elif cmp_ == 0:
            if c12:
                r._keys.append(i1.key)
                if merge:
                    r._values.append(MERGE(i1.value, w1, i2.value, w2))
            i1.advance()
            i2.advance()
        else:
            if c2:
                copy(i2, w2)
            i2.advance()

    if c1:
        while i1.active:
            copy(i1, w1)
            i1.advance()
    if c2:
        while i2.active:
            copy(i2, w2)
            i2.advance()

    return r


class setop(object):

    def __init__(self, func, set_type):
        self.func = func
        self.set_type = set_type

    def __call__(self, *a, **k):
        return self.func(self.set_type, *a, **k)


def difference(set_type, o1, o2):
    if o1 is None or o2 is None:
        return o1
    return _set_operation(o1, o2, 1, 0, 1, 0, 1, 0, 0)

def union(set_type, o1, o2):
    if o1 is None:
        return o2
    if o2 is None:
        return o1
    return _set_operation(o1, o2, 0, 0, 1, 1, 1, 1, 1)

def intersection(set_type, o1, o2):
    if o1 is None:
        return o2
    if o2 is None:
        return o1
    return _set_operation(o1, o2, 0, 0, 1, 1, 0, 1, 0)

def weightedUnion(set_type, o1, o2, w1=1, w2=1):
    if o1 is None:
        if o2 is None:
            return 0, o2
        else:
            return w2, o2
    elif o2 is None:
        return w1, o1
    else:
        return 1, _set_operation(o1, o2, 1, 1, w1, w2, 1, 1, 1)

def weightedIntersection(set_type, o1, o2, w1=1, w2=1):
    if o1 is None:
        if o2 is None:
            return 0, o2
        else:
            return w2, o2
    elif o2 is None:
        return w1, o1
    else:
        result = _set_operation(o1, o2, 1, 1, w1, w2, 0, 1, 0)
        return (w1 + w2 if isinstance(result, (Set, TreeSet)) else 1, result)

def multiunion(set_type, seqs):
    # XXX simple/slow implementation. Goal is just to get tests to pass.
    if not seqs:
        return set_type()
    result = set_type()
    for s in seqs:
        try:
            iter(s)
        except TypeError:
            s = set_type((s, ))
        result.update(s)
    return result

def to_ob(self, v):
    return v

int_types = int, long
def to_int(self, v):
    try:
        if not unpack("i", pack("i", v))[0] == v:
            raise TypeError('32-bit integer expected')
    except (struct_error,
            OverflowError, #PyPy
           ):
        raise TypeError('32-bit integer expected')

    return int(v)

def to_float(self, v):
    try:
        pack("f", v)
    except struct_error:
        raise TypeError('float expected')
    return float(v)

def to_long(self, v):
    try:
        if not unpack("q", pack("q", v))[0] == v:
            if isinstance(v, int_types):
                raise ValueError("Value out of range", v)
            raise TypeError('64-bit integer expected')
    except (struct_error,
            OverflowError, #PyPy
           ):
        if isinstance(v, int_types):
            raise ValueError("Value out of range", v)
        raise TypeError('64-bit integer expected')

    return int(v)

def to_str(l):
    def to(self, v):
        if not (isinstance(v, str) and len(v) == l):
            raise TypeError("%s-character string expected" % l)
        return v
    return to

tos = dict(I=to_int, L=to_long, F=to_float, O=to_ob)

MERGE_DEFAULT_int = 1
MERGE_DEFAULT_float = 1.0

def MERGE(self, value1, weight1, value2, weight2):
    return (value1 * weight1) + (value2 * weight2)

def MERGE_WEIGHT_default(self, value, weight):
    return value

def MERGE_WEIGHT_numeric(self, value, weight):
    return value * weight
