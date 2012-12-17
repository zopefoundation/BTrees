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
#define INT_GETMAX(x) 2<<31
#define TEXT_FROM_STRING PyUnicode_FromString
#define TEXT_FORMAT PyUnicode_Format

#define COMPARE(lhs, rhs) \
    PyObject_RichCompareBool((lhs), (rhs), Py_LT) > 0 ? -1 : \
    (PyObject_RichCompareBool((lhs), (rhs), Py_EQ) > 0 ? 0 : 1)


#else

#define INTERN PyString_InternFromString
#define INT_FROM_LONG(x) PyInt_FromLong(x)
#define INT_CHECK(x) PyInt_Check(x)
#define INT_AS_LONG(x) PyInt_AS_LONG(x)
#define INT_GETMAX(x) PyInt_GetMax(x)
#define TEXT_FROM_STRING PyString_FromString
#define TEXT_FORMAT PyString_Format

#define COMPARE(lhs, rhs) PyObject_Compare((lhs), (rhs))

#endif

#endif /* BTREES__COMPAT_H */
