#define VALUEMACROS_H "$Id$\n"

/* Note that the second comparison is skipped if the first comparison returns:

   1  -> There was no error and the answer is -1
  -1 -> There was an error, which the caller will detect with PyError_Occurred.
 */
#define COMPARE(lhs, rhs) \
  (lhs == Py_None ? (rhs == Py_None ? 0 : -1) : (rhs == Py_None ? 1 : \
     (PyObject_RichCompareBool((lhs), (rhs), Py_LT) != 0 ? -1 : \
      (PyObject_RichCompareBool((lhs), (rhs), Py_EQ) > 0 ? 0 : 1))))

#define VALUE_TYPE PyObject *
#define VALUE_TYPE_IS_PYOBJECT
#define TEST_VALUE(VALUE, TARGET) (COMPARE((VALUE),(TARGET)))
#define DECLARE_VALUE(NAME) VALUE_TYPE NAME
#define INCREF_VALUE(k) Py_INCREF(k)
#define DECREF_VALUE(k) Py_DECREF(k)
#define COPY_VALUE(k,e) k=(e)
#define COPY_VALUE_TO_OBJECT(O, K) O=(K); Py_INCREF(O)
#define COPY_VALUE_FROM_ARG(TARGET, ARG, S) TARGET=(ARG)
#define NORMALIZE_VALUE(V, MIN) Py_INCREF(V)
