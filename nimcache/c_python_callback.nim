# Implementing C function callbacks using Python (Python recipe)

proc qsort*(a2: pointer; a3: csize; a4: csize; 
            a5: proc (a2: pointer; a3: pointer): cint)
var py_compare_func*: ptr PyObject = nil

proc stub_compare_func*(a: ptr ptr PyObject; b: ptr ptr PyObject): cint = 
  var retvalue: cint = 0
  # Build up the argument list... 
  var arglist: ptr PyObject = Py_BuildValue("(OO)", a[], b[])
  # ...for calling the Python compare function.
  var result: ptr PyObject = PyEval_CallObject(py_compare_func, arglist)
  if result and PyInt_Check(result): 
    retvalue = PyInt_AsLong(result)
  Py_XDECREF(result)
  Py_DECREF(arglist)
  return retvalue

proc pyqsort*(obj: ptr PyObject; args: ptr PyObject): ptr PyObject = 
  var pycompobj: ptr PyObject
  var list: ptr PyObject
  if not PyArg_ParseTuple(args, "OO", addr(list), addr(pycompobj)): 
    return nil
  if not PyCallable_Check(pycompobj): 
    PyErr_SetString(PyExc_TypeError, "Need a callable object!")
  else: 
    # save the compare func. This obviously won't work for multi-threaded
    # programs.
    py_compare_func = pycompobj
    if PyList_Check(list): 
      var size: cint = PyList_Size(list)
      var i: cint
      # make an array of (PyObject *), because qsort does not know about
      # the PyList object
      var v: ptr ptr PyObject = cast[ptr ptr PyObject](malloc(
          sizeof(cast[ptr PyObject](size[]))))
      i = 0
      while i < size: 
        v[i] = PyList_GetItem(list, i)
        # increment the reference count, because setting the list items below
        # will decrement the ref count
        Py_INCREF(v[i])
        inc(i)
      qsort(v, size, sizeof(ptr PyObject), stub_compare_func)
      i = 0
      while i < size: 
        PyList_SetItem(list, i, v[i])
        # need not do Py_DECREF - see above
        inc(i)
      free(v)
  Py_INCREF(Py_None)
  return Py_None

var qsortMethods*: ptr PyMethodDef = [["qsort", pyqsort, METH_VARARGS],[nil, nil]]

#__declspec(dllexport) void initqsort(void) {
#    PyObject *m;
#    m = Py_InitModule("qsort", qsortMethods);
#}
