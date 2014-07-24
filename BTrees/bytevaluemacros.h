
#define VALUEMACROS_H "$Id$\n"

#define VALUE_TYPE char
#define VALUE_PARSE "i"
#define COPY_VALUE_TO_OBJECT(O, K) O=INT_FROM_LONG(K)

#define COPY_VALUE_FROM_ARG(TARGET, ARG, STATUS)                  \
  if (INT_CHECK(ARG)) {                                         \
      long vcopy = INT_AS_LONG(ARG);                            \
      if (vcopy < -127 || vcopy > 127) {                        \
        PyErr_SetString(PyExc_TypeError, "byte out of range"); \
        (STATUS)=0; (TARGET)=0;                                   \
      }                                                           \
      else TARGET = vcopy;                                        \
  } else {                                                        \
      PyErr_SetString(PyExc_TypeError, "expected byte value");   \
      (STATUS)=0; (TARGET)=0; }

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
