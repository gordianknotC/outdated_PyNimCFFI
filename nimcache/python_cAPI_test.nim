import nimborg/py/low_level
import nimborg/py/high_level





proc py_returnChar*(self: PPyObject, args: PPyObject): PPyObject =
  var s: cstring = "Hello from C!"
  return Py_BuildValue("s", s)

# inputs: none

proc py_returnDouble*(self: PPyObject; args: PPyObject): PPyObject = 
  var val: cdouble = 777.42
  return Py_BuildValue("d", val)

# inputs: none

proc py_returnList*(self: PPyObject; args: PPyObject): PPyObject = 
  var 
    i: cint
    array_len: cint = 5
  var arr: array[5, cint] = [ cint(1), cint(2), cint(3), cint(4), cint(5)]
  var lst: PPyObject = PyList_New(array_len)
  if lst == nil: return nil
  i = 0
  while i < array_len: 
    var num: PPyObject = PyFloat_FromDouble( float64(arr[i]) )
    if num != nil: 
      Py_DECREF(lst)
      return nil
    discard PyList_SET_ITEM(lst, i, num)
    # reference to num stolen
    inc(i)
  return lst

# inputs: object (list, dict, etc...)
proc py_getObject*(self: PPyObject; args: PPyObject): PPyObject = 
  var list: PPyObject
  discard PyArg_ParseTuple(args, "O", addr(list))
  return Py_BuildValue("O", list)

# inputs: list

proc py_modifyList*(self: PPyObject; args: PPyObject): PPyObject = 
  var list: PPyObject
  discard PyArg_ParseTuple(args, "O", addr(list))
  discard PyList_SET_ITEM(list, 0, PyLong_FromLong(777))
  return Py_BuildValue("O", list)

# inputs: length of the array

proc py_returnDynamicList*(self: PPyObject; args: PPyObject): PPyObject = 
  var 
    arr_len: cint
    i: cint
  discard PyArg_ParseTuple(args, "i", addr(arr_len))
  var lst: PPyObject = PyList_New(arr_len)
  if lst == nil: return nil
  i = 0
  while i < arr_len: 
    var num: PPyObject = PyLong_FromLong(i)
    if num == nil: 
      Py_DECREF(lst)
      return nil
    discard PyList_SET_ITEM(lst, i, num)
    # reference to num stolen
    inc(i)
  return lst

#
#  Bind Python function names to our C functions
# 

# var myModule_methods: PPyMethodDef = [
#     [cstring("returnChar"), py_returnChar, METH_VARARGS], 
#     [cstring("returnList"), py_returnList, METH_VARARGS], 
#     [cstring("returnDouble"), py_returnDouble, METH_VARARGS], 
#     [cstring("returnDynamicList"), py_returnDynamicList, METH_VARARGS], 
#     [cstring("getObject"), py_getObject, METH_VARARGS], 
#     [cstring("modifyList"), py_modifyList, METH_VARARGS], [nil, nil]]


type CArray*{.unchecked.}[T] = array[0..0, T]
type CPtr*[T] = ptr CArray[T]

type SafeCPtr*[T] =
  object
    when not defined(release):
      size: int
    mem: CPtr[T]

proc safe*[T](p: CPtr[T], k: int): SafeCPtr[T] =
  when defined(release):
    SafeCPtr[T](mem: p)
  else:
    SafeCPtr[T](mem: p, size: k)

proc safe*[T](a: var openarray[T], k: int): SafeCPtr[T] =
  safe(cast[CPtr[T]](addr(a)), k)

proc `[]`*[T](p: SafeCPtr[T], k: int): T =
  when not defined(release):
    assert k < p.size
  result = p.mem[k]

proc `[]=`*[T](p: SafeCPtr[T], k: int, val: T) =
  when not defined(release):
    assert k < p.size
  p.mem[k] = val


var e = cstring("")
var tmparr = [
    TPyMethodDef(ml_name:cstring("returnList"), ml_meth:py_returnList, ml_flags:METH_VARARGS, ml_doc:e  ), 
    TPyMethodDef(ml_name:cstring("returnDouble"), ml_meth:py_returnDouble, ml_flags:METH_VARARGS, ml_doc:e ),
    TPyMethodDef(ml_name:cstring("returnDynamicList"), ml_meth:py_returnDynamicList, ml_flags:METH_VARARGS, ml_doc:e ),  
    TPyMethodDef(ml_name:cstring("getObject"), ml_meth:py_getObject, ml_flags:METH_VARARGS, ml_doc:e ),      
    TPyMethodDef(ml_name:cstring("modifyList"), ml_meth:py_modifyList, ml_flags:METH_VARARGS, ml_doc:e ),
    TPyMethodDef()
    ]
var myModule_methods: PPyMethodDef = cast[PPyMethodDef](safe(tmparr, tmparr.len).mem)



#
#  Python calls this to let us initialize our module
# 

# proc initmyModule*() = 
#   discard Py_InitModule("myModule", myModule_methods)


