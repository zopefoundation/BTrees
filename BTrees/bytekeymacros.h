
#define KEYMACROS_H "$Id$\n"

/* C char as key */
#define KEY_TYPE char
#define KEY_CHECK INT_CHECK
#define COPY_KEY_TO_OBJECT(O, K) O=INT_FROM_LONG(K)
#define COPY_KEY_FROM_ARG(TARGET, ARG, STATUS)                    \
  if (INT_CHECK(ARG)) {                                         \
      long vcopy = INT_AS_LONG(ARG);                            \
      if (vcopy < -127 || vcopy > 127) {                         \
        PyErr_SetString(PyExc_TypeError, "byte out of range"); \
        (STATUS)=0; (TARGET)=0;                                   \
      }                                                           \
      else TARGET = vcopy;                                        \
  } else {                                                        \
      PyErr_SetString(PyExc_TypeError, "expected byte key");   \
      (STATUS)=0; (TARGET)=0; }

#undef KEY_TYPE_IS_PYOBJECT
#define TEST_KEY_SET_OR(V, K, T) if ( ( (V) = (((K) < (T)) ? -1 : (((K) > (T)) ? 1: 0)) ) , 0 )
#define DECREF_KEY(KEY)
#define INCREF_KEY(k)
#define COPY_KEY(KEY, E) (KEY=(E))
#define MULTI_INT_UNION 1
