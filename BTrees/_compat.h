/* Straddle Python 2 / 3 */
#ifndef BTREES__COMPAT_H
#define BTREES__COMPAT_H

#include "Python.h"

#ifdef INTERN
#undef INTERN
#endif

#ifdef INT_FROM_LONG
#undef INT_FROM_LONG
#endif

#ifdef INT_CHECK
#undef INT_CHECK
#endif

#if PY_MAJOR_VERSION >= 3

#define PY3K

#define INTERN PyUnicode_InternFromString
#define INT_FROM_LONG(x) PyLong_FromLong(x)
#define INT_CHECK(x) PyLong_Check(x)
#define INT_AS_LONG(x) PyLong_AS_LONG(x)
#define TEXT_FROM_STRING PyUnicode_FromString
#define TEXT_FORMAT PyUnicode_Format

/* Emulate Python2's __cmp__,  wrapping PyObject_RichCompareBool(),
 * Return -2/-3 for errors, -1 for lhs<rhs, 0 for lhs==rhs, 1 for lhs>rhs.
 */
static inline
int __compare(PyObject *lhs, PyObject *rhs) {
    int less, equal;

    less = PyObject_RichCompareBool(lhs, rhs, Py_LT);
    if ( less == -1 ) {
        return -2;
    }
    equal = PyObject_RichCompareBool(lhs, rhs, Py_EQ);
    if ( equal == -1 ) {
        return -3;
    }
    return less ? -1 : (equal ? 0 : 1);
}

#define COMPARE(lhs, rhs) __compare((lhs), (rhs))


#else

#define INTERN PyString_InternFromString
#define INT_FROM_LONG(x) PyInt_FromLong(x)
#define INT_CHECK(x) PyInt_Check(x)
#define INT_AS_LONG(x) PyInt_AS_LONG(x)
#define TEXT_FROM_STRING PyString_FromString
#define TEXT_FORMAT PyString_Format

#define COMPARE(lhs, rhs) PyObject_Compare((lhs), (rhs))

#endif

#endif /* BTREES__COMPAT_H */
