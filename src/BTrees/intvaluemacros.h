
#define VALUEMACROS_H "$Id$\n"

/*
  VALUE_PARSE is used exclusively in SetOpTemplate.c to accept the weight
  values for merging. The PyArg_ParseTuple function it uses has no trivial way
  to express "unsigned with check", so in the unsigned case, passing negative
  values as weights will produce weird output no matter what VALUE_PARSE we
  use (because it will immediately get cast to an unsigned).
*/

#ifndef ZODB_UNSIGNED_VALUE_INTS
/*signed values */
#ifdef ZODB_64BIT_INTS
#define NEED_LONG_LONG_SUPPORT
#define VALUE_TYPE PY_LONG_LONG
#define VALUE_PARSE "L"

#define NEED_LONG_LONG_AS_OBJECT
#define COPY_VALUE_TO_OBJECT(O, K) O=longlong_as_object(K)

#define NEED_LONG_LONG_CONVERT
#define COPY_VALUE_FROM_ARG(TARGET, ARG, STATUS) \
    if (!longlong_convert((ARG), &TARGET)) \
    { \
        (STATUS)=0; (TARGET)=0; \
    }
#else
#define VALUE_TYPE int
#define VALUE_PARSE "i"
#define COPY_VALUE_TO_OBJECT(O, K) O=PyLong_FromLong(K)

#define COPY_VALUE_FROM_ARG(TARGET, ARG, STATUS)                  \
  if (PyLong_Check(ARG)) {                                         \
      long vcopy = PyLong_AsLong(ARG);                            \
      if (PyErr_Occurred()) {                                     \
        if (PyErr_ExceptionMatches(PyExc_OverflowError)) {        \
            PyErr_Clear();                                        \
            PyErr_SetString(PyExc_TypeError, "integer out of range"); \
        }                                                         \
        (STATUS)=0; (TARGET)=0;                                   \
      }                                                           \
      else if ((int)vcopy != vcopy) {                                  \
        PyErr_SetString(PyExc_TypeError, "integer out of range"); \
        (STATUS)=0; (TARGET)=0;                                   \
      }                                                           \
      else TARGET = vcopy;                                        \
  } else {                                                        \
      PyErr_SetString(PyExc_TypeError, "expected integer key");   \
      (STATUS)=0; (TARGET)=0; }

#endif
#else
/* unsigned values */
#ifdef ZODB_64BIT_INTS
/* unsigned, 64-bit values */
#define NEED_LONG_LONG_SUPPORT
#define VALUE_TYPE unsigned PY_LONG_LONG
#define VALUE_PARSE "K"

#define NEED_ULONG_LONG_AS_OBJECT
#define COPY_VALUE_TO_OBJECT(O, K) O=ulonglong_as_object(K)

#define NEED_ULONG_LONG_CONVERT
#define COPY_VALUE_FROM_ARG(TARGET, ARG, STATUS) \
    if (!ulonglong_convert((ARG), &TARGET)) \
    { \
        (STATUS)=0; (TARGET)=0; \
    }
#else
/* unsigned, 32-bit values */
#define VALUE_TYPE unsigned int
#define VALUE_PARSE "I"
#define COPY_VALUE_TO_OBJECT(O, K) O=PyLong_FromUnsignedLongLong(K)

#define COPY_VALUE_FROM_ARG(TARGET, ARG, STATUS)                  \
  if (PyLong_Check(ARG)) {                                        \
      long vcopy = PyLong_AsLong(ARG);                            \
      if (PyErr_Occurred()) {                                     \
        if (PyErr_ExceptionMatches(PyExc_OverflowError)) {        \
            PyErr_Clear();                                        \
            PyErr_SetString(                                      \
                PyExc_TypeError, "integer out of range");         \
        }                                                         \
        (STATUS)=0; (TARGET)=0;                                   \
      }                                                           \
      else if (vcopy < 0) {                                       \
        PyErr_SetString(                                          \
            PyExc_TypeError,                                      \
            "can't convert negative value to unsigned int");      \
        (STATUS)=0; (TARGET)=0;                                   \
      }                                                           \
      else if ((unsigned int)vcopy != vcopy) {                    \
        PyErr_SetString(PyExc_TypeError, "integer out of range"); \
        (STATUS)=0; (TARGET)=0;                                   \
      }                                                           \
      else TARGET = vcopy;                                        \
  } else {                                                        \
      PyErr_SetString(PyExc_TypeError, "expected integer key");   \
      (STATUS)=0; (TARGET)=0; }

#endif
#endif

#undef VALUE_TYPE_IS_PYOBJECT
#define TEST_VALUE(K, T) (((K) < (T)) ? -1 : (((K) > (T)) ? 1: 0))
#define VALUE_SAME(VALUE, TARGET) ( (VALUE) == (TARGET) )
#define DECLARE_VALUE(NAME) VALUE_TYPE NAME
#define DECREF_VALUE(k)
#define INCREF_VALUE(k)
#define COPY_VALUE(V, E) (V=(E))

#define NORMALIZE_VALUE(V, MIN) ((MIN) > 0) ? ((V)/=(MIN)) : 0

#define MERGE_DEFAULT 1
#define MERGE(O1, w1, O2, w2) ((O1)*(w1)+(O2)*(w2))
#define MERGE_WEIGHT(O, w) ((O)*(w))
