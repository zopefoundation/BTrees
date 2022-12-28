#define KEYMACROS_H "$Id$\n"
#define KEY_TYPE PyObject *
#define KEY_TYPE_IS_PYOBJECT

#include "Python.h"
#include "_compat.h"

static PyObject *object_; /* initialized in BTreeModuleTemplate init */

static int
check_argument_cmp(PyObject *arg)
{
    /* printf("check cmp %p %p %p %p\n",  */
    /*        arg->ob_type->tp_richcompare, */
    /*        ((PyTypeObject *)object_)->ob_type->tp_richcompare, */
    /*        arg->ob_type->tp_compare, */
    /*        ((PyTypeObject *)object_)->ob_type->tp_compare); */
    if (arg == Py_None) {
      return 1;
    }


    if (Py_TYPE(arg)->tp_richcompare == Py_TYPE(object_)->tp_richcompare)
    {
        PyErr_Format(PyExc_TypeError,
		     "Object of class %s has default comparison",
		     Py_TYPE(arg)->tp_name);
        return 0;
    }
    return 1;
}

#define TEST_KEY_SET_OR(V, KEY, TARGET) \
if ( ( (V) = COMPARE((KEY),(TARGET)) ), PyErr_Occurred() )
#define INCREF_KEY(k) Py_INCREF(k)
#define DECREF_KEY(KEY) Py_DECREF(KEY)
#define COPY_KEY(KEY, E) KEY=(E)
#define COPY_KEY_TO_OBJECT(O, K) O=(K); Py_INCREF(O)
#define COPY_KEY_FROM_ARG(TARGET, ARG, S) \
    TARGET=(ARG); \
    (S) = 1;
#define KEY_CHECK_ON_SET check_argument_cmp
