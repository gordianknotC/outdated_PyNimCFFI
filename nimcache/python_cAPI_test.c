

// inputs: none
static PyObject* py_returnChar(PyObject* self, PyObject* args)
{
	char *s = "Hello from C!";
	return Py_BuildValue("s", s);
}

// inputs: none
static PyObject* py_returnDouble(PyObject* self, PyObject* args)
{
	double val = 777.42;
	return Py_BuildValue("d", val);
}

// inputs: none
static PyObject* py_returnList(PyObject* self, PyObject* args)
{
	int i, array_len = 5;
	int array[5] = {1,2,3,4,5};
	PyObject *lst = PyList_New(array_len);
	if (!lst)
	    return NULL;
	for (i = 0; i < array_len; i++) {
	    PyObject *num = PyFloat_FromDouble(array[i]);
	    if (!num) {
	        Py_DECREF(lst);
	        return NULL;
	    }
	    PyList_SET_ITEM(lst, i, num);   // reference to num stolen
	}
	return lst;
}

// inputs: object (list, dict, etc...)
static PyObject* py_getObject(PyObject* self, PyObject* args)
{
	PyObject *list;
	PyArg_ParseTuple(args, "O", &list);
	return Py_BuildValue("O", list);
}

// inputs: list
static PyObject* py_modifyList(PyObject* self, PyObject* args)
{
	PyObject *list;
	PyArg_ParseTuple(args, "O", &list);
	PyList_SET_ITEM(list, 0, PyInt_FromLong(777));
	return Py_BuildValue("O", list);
}

// inputs: length of the array
static PyObject* py_returnDynamicList(PyObject* self, PyObject* args)
{
	int arr_len, i;
	PyArg_ParseTuple(args, "i", &arr_len);
	PyObject *lst = PyList_New(arr_len);
	if (!lst)
	    return NULL;
	for (i = 0; i < arr_len; i++) {
	    PyObject *num = PyInt_FromLong(i);
	    if (!num) {
	        Py_DECREF(lst);
	        return NULL;
	    }
	    PyList_SET_ITEM(lst, i, num);   // reference to num stolen
	}
	return lst;
}

/*
 * Bind Python function names to our C functions
 */
static PyMethodDef myModule_methods[] = {
	{"returnChar", py_returnChar, METH_VARARGS},
	{"returnList", py_returnList, METH_VARARGS},
	{"returnDouble", py_returnDouble, METH_VARARGS},
	{"returnDynamicList", py_returnDynamicList, METH_VARARGS},
	{"getObject", py_getObject, METH_VARARGS},
	{"modifyList", py_modifyList, METH_VARARGS},
	{NULL, NULL} 
};

/*
 * Python calls this to let us initialize our module
 */
void initmyModule()
{
	(void) Py_InitModule("myModule", myModule_methods);
}