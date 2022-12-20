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

#ifndef Py_RETURN_NOTIMPLEMENTED
#define Py_RETURN_NOTIMPLEMENTED \
    return Py_INCREF(Py_NotImplemented), Py_NotImplemented
#endif

#define INTERN PyUnicode_InternFromString
#define INT_FROM_LONG(x) PyLong_FromLong(x)
#define INT_CHECK(x) PyLong_Check(x)
#define INT_AS_LONG(x) PyLong_AsLong(x)
#define UINT_FROM_LONG(x) PyLong_FromUnsignedLong(x)
#define UINT_AS_LONG(x) PyLong_AsUnsignedLong(x)
#define TEXT_FROM_STRING PyUnicode_FromString
#define TEXT_FORMAT PyUnicode_Format

/* Note that the second comparison is skipped if the first comparison returns:

   1  -> There was no error and the answer is -1
  -1 -> There was an error, which the caller will detect with PyError_Occurred.
 */
#define COMPARE(lhs, rhs) \
  (lhs == Py_None ? (rhs == Py_None ? 0 : -1) : (rhs == Py_None ? 1 : \
     (PyObject_RichCompareBool((lhs), (rhs), Py_LT) != 0 ? -1 : \
      (PyObject_RichCompareBool((lhs), (rhs), Py_EQ) > 0 ? 0 : 1))))

#endif /* BTREES__COMPAT_H */
