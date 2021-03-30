# ifndef SETOPTEMPLATE_H
# define SETOPTEMPLATE_H

#include "Python.h"

static PyObject *
union_m(PyObject *ignored, PyObject *args);

static PyObject *
intersection_m(PyObject *ignored, PyObject *args);

static PyObject *
difference_m(PyObject *ignored, PyObject *args);

# endif
