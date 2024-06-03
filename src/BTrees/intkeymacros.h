
#define KEYMACROS_H "$Id$\n"

#if !defined(ZODB_UNSIGNED_KEY_INTS)
/* signed keys */

#if defined(ZODB_64BIT_INTS)
/* PY_LONG_LONG as key */

#define NEED_LONG_LONG_SUPPORT

#define NEED_LONG_LONG_KEYS
#define KEY_TYPE PY_LONG_LONG

#define NEED_LONG_LONG_CHECK
#define KEY_CHECK longlong_check

#define NEED_LONG_LONG_AS_OBJECT
#define COPY_KEY_TO_OBJECT(O, K) O=longlong_as_object(K)

#define NEED_LONG_LONG_CONVERT
#define COPY_KEY_FROM_ARG(TARGET, ARG, STATUS) \
    if (!longlong_convert((ARG), &TARGET)) \
    { \
        (STATUS)=0; (TARGET)=0; \
    }

#else /* !defined(ZODB_64BIT_INTS) */
/* C int as key */

#define KEY_TYPE int
#define KEY_CHECK PyLong_Check
#define COPY_KEY_TO_OBJECT(O, K) O=PyLong_FromLong(K)
#define COPY_KEY_FROM_ARG(TARGET, ARG, STATUS)                    \
  if (PyLong_Check(ARG)) {                                        \
      long vcopy = PyLong_AsLong(ARG);                            \
      if (PyErr_Occurred()) {                                     \
        if (PyErr_ExceptionMatches(PyExc_OverflowError)) {        \
            PyErr_Clear();                                        \
            PyErr_SetString(PyExc_TypeError, "integer out of range"); \
        }                                                         \
        (STATUS)=0; (TARGET)=0;                                   \
      }                                                           \
      else if ((int)vcopy != vcopy) {                             \
        PyErr_SetString(PyExc_TypeError, "integer out of range"); \
        (STATUS)=0; (TARGET)=0;                                   \
      }                                                           \
      else TARGET = vcopy;                                        \
  } else {                                                        \
      PyErr_SetString(PyExc_TypeError, "expected integer key");   \
      (STATUS)=0; (TARGET)=0; }

#endif /* !defined(ZODB_64BIT_INTS) */

#else
/* Unsigned keys */

#if defined(ZODB_64BIT_INTS)
/* PY_LONG_LONG as key */

#define NEED_LONG_LONG_SUPPORT
#define NEED_LONG_LONG_KEYS
#define KEY_TYPE unsigned PY_LONG_LONG

#define NEED_ULONG_LONG_CHECK
#define KEY_CHECK ulonglong_check

#define NEED_ULONG_LONG_AS_OBJECT
#define COPY_KEY_TO_OBJECT(O, K) O=ulonglong_as_object(K)

#define NEED_ULONG_LONG_CONVERT
#define COPY_KEY_FROM_ARG(TARGET, ARG, STATUS)  \
    if (!ulonglong_convert((ARG), &TARGET))     \
    {                                           \
        (STATUS)=0; (TARGET)=0;                 \
    }

#else /* !defined(ZODB_64BIT_INTS) */
/* C int as key */

#define KEY_TYPE unsigned int
#define KEY_CHECK PyLong_Check
#define COPY_KEY_TO_OBJECT(O, K) O=PyLong_FromUnsignedLongLong(K)

#define COPY_KEY_FROM_ARG(TARGET, ARG, STATUS)                    \
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

#endif /* !defined(ZODB_64BIT_INTS) */

#endif /* ZODB_SIGNED_KEY_INTS */

#undef KEY_TYPE_IS_PYOBJECT

#define TEST_KEY_SET_OR(V, K, T) if ( ( (V) = (((K) < (T)) ? -1 : (((K) > (T)) ? 1: 0)) ) , 0 )
#define DECREF_KEY(KEY)
#define INCREF_KEY(k)
#define COPY_KEY(KEY, E) (KEY=(E))
#define MULTI_INT_UNION 1
