
#define KEYMACROS_H "$Id$\n"

#ifndef ZODB_UNSIGNED_KEY_INTS
/* signed keys */
#ifdef ZODB_64BIT_INTS
/* PY_LONG_LONG as key */
#define NEED_LONG_LONG_SUPPORT
#define NEED_LONG_LONG_KEYS
#define KEY_TYPE PY_LONG_LONG
#define KEY_CHECK longlong_check
#define COPY_KEY_TO_OBJECT(O, K) O=longlong_as_object(K)
#define COPY_KEY_FROM_ARG(TARGET, ARG, STATUS) \
    if (!longlong_convert((ARG), &TARGET)) \
    { \
        (STATUS)=0; (TARGET)=0; \
    }
#else
/* C int as key */
#define KEY_TYPE int
#define KEY_CHECK INT_CHECK
#define COPY_KEY_TO_OBJECT(O, K) O=INT_FROM_LONG(K)
#define COPY_KEY_FROM_ARG(TARGET, ARG, STATUS)                    \
  if (INT_CHECK(ARG)) {                                           \
      long vcopy = INT_AS_LONG(ARG);                              \
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
#endif
#else
/* Unsigned keys */
#ifdef ZODB_64BIT_INTS
/* PY_LONG_LONG as key */
#define NEED_LONG_LONG_SUPPORT
#define NEED_LONG_LONG_KEYS
#define KEY_TYPE unsigned PY_LONG_LONG
#define KEY_CHECK ulonglong_check
#define COPY_KEY_TO_OBJECT(O, K) O=ulonglong_as_object(K)
#define COPY_KEY_FROM_ARG(TARGET, ARG, STATUS) \
    if (!ulonglong_convert((ARG), &TARGET)) \
    { \
        (STATUS)=0; (TARGET)=0; \
    }
#else
/* C int as key */
#define KEY_TYPE unsigned int
#define KEY_CHECK INT_CHECK
#define COPY_KEY_TO_OBJECT(O, K) O=UINT_FROM_LONG(K)
#define COPY_KEY_FROM_ARG(TARGET, ARG, STATUS)                    \
  if (INT_CHECK(ARG)) {                                           \
      long vcopy = INT_AS_LONG(ARG);                     \
      if (PyErr_Occurred()) {                                     \
        if (PyErr_ExceptionMatches(PyExc_OverflowError)) {        \
            PyErr_Clear();                                        \
            PyErr_SetString(PyExc_TypeError, "integer out of range"); \
        }                                                         \
        (STATUS)=0; (TARGET)=0;                                   \
      }                                                           \
      else if (vcopy < 0) {                                       \
        PyErr_SetString(PyExc_TypeError, "can't convert negative value to unsigned int"); \
        (STATUS)=0; (TARGET)=0;                                   \
      }                                                           \
      else if ((unsigned int)vcopy != vcopy) {                     \
        PyErr_SetString(PyExc_TypeError, "integer out of range"); \
        (STATUS)=0; (TARGET)=0;                                   \
      }                                                           \
      else TARGET = vcopy;                                        \
  } else {                                                        \
      PyErr_SetString(PyExc_TypeError, "expected integer key");   \
      (STATUS)=0; (TARGET)=0; }
#endif
#endif /* ZODB_SIGNED_KEY_INTS */

#undef KEY_TYPE_IS_PYOBJECT
#define TEST_KEY_SET_OR(V, K, T) if ( ( (V) = (((K) < (T)) ? -1 : (((K) > (T)) ? 1: 0)) ) , 0 )
#define DECREF_KEY(KEY)
#define INCREF_KEY(k)
#define COPY_KEY(KEY, E) (KEY=(E))
#define MULTI_INT_UNION 1
