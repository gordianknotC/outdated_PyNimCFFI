import tables
import nimborg/py/low_level


# codegenDecl pragma usage:
# var
#   codegenVar {.codegenDecl: "$# progmem $#".}: int
# --------------------------------------------
# which generate:
# 'int' progmem 'codegenVar'
# proc test(arg:int):RetType {. gencodeDecl:"$# $#$#" .}
# ---------------------------------------------
# which generate:
# RetType test(int arg)
#----------------------------------------------
# proc cstringToString(s:cstring) :string {. exportc, dynlib, codegenDecl:"beforeA $# beforeB $# beforeC $#" .} =
# beforeA NimStringDesc* beforeB cstringToString beforeC (NCSTRING s);


type
    Vector = object
        x, y, z: float

    Man    = tuple
        name: cstring
        age,value: int

    Person = object
        name: cstring     # the * means that `name` is accessible from other modules
        age: int                # no * means that the field is hidden

    PyType* [T] = object
        data*: T
        typename*: cstring

    TSize  = tuple
        width, height: int

    TPos   = tuple
        x,y: int

    TIntList     = seq[int]
    TFloatList   = seq[float]
    TCstringList = seq[cstring]
    TStringList  = seq[string]

    TIntKVTuple       = tuple[key:cstring, val:int]
    TCstringKVTuple   = tuple[key:cstring, val:cstring]
    TFloatKVTuple     = tuple[key:cstring, val:float]

    TIntListKVTp      = tuple[key:cstring, val:TIntList]
    TFloatListKVTp    = tuple[key:cstring, val:TFloatList]
    TCstringListKVTp  = tuple[key:cstring, val:TCstringList]

    TIntTable         = Table[cstring, int]
    TFloatTable       = Table[cstring, float]
    TCstringTable     = Table[cstring, cstring]
    TStringTable      = Table[cstring, string]

    TIntListTable     = Table[cstring, TIntList]
    TFloatListTable   = Table[cstring, TFloatList]
    TCstringListTable = Table[cstring, TCstringList]

    TPyCall = proc (msg:cstring):bool

const
  SymChars: set[char] = {'a'..'z', 'A'..'Z', '\x80'..'\xFF'}

# bad style ahead: Nim is not C.
converter toBool(x: int): bool = x != 0

proc stringToCstring(s:string) :cstring {. exportc, dynlib .}
proc cstringToString(s:cstring) :string {. exportc, dynlib .} =
    result = ""
    var i = 0
    while i < s.len:
        result.add(s[i])
        inc(i)


proc getPerson(name:string, age:int): Person {. exportc, dynlib .}= 
    var name:cstring = name
    result = Person(name:name, age:age)

proc getVector(x,y,z:float): Vector {. exportc, dynlib .}= 
    result = Vector(x:x,y:y,z:z)

proc getMan(name:cstring, age,value:int): Man {. exportc, dynlib .}= 
    result = (name:name, age:age, value:value)

proc stringToCstring(s:string) :cstring =
    echo "inside nimstring to cstring: ", s
    result = s

proc callback_topython(s:cstring, callback:proc (msg:cstring):bool ):cstring {. exportc, dynlib .} = 
  echo "switch case inside nimrod"
  case s[0]
  of SymChars, '_': 
    echo "an identifier"
    echo "call python callback: params: ", "is it a identifier?"
    if callback(cstring("is it a identifier?")) : echo "identifier process"
    else:                               echo "cancel identifer process"
  of '0'..'9':      
    echo "a number"
    if callback("it's a number?"):      echo "numeric process"
    else:                               echo "cancel numeric process"
  else:             
    echo "not a number or an identifier"
    if callback("it's neither a number nor an identifier"):  echo "other process"
    else:                                                    echo "cancel other process"

  result = "done"




#------------------------------------------------
proc reverse* [T](x:seq[T]): seq[T] {.inline.} = 
    result = @[]
    for i in countdown(x.len-1, 0):
        result.add(x[i])
#------------------------------------------------
iterator reversed* [T](x:seq[T]): T {.inline.}= 
        for i in countdown(x.len-1, 0):
                yield x[i]
#------------------------------------------------
proc list*    [T](rest:varargs[T]): seq[T]    = 
    result = @[]
    for i in rest:
        result.add(i)
#------------------------------------------------
proc intPop     (s:var TIntList):    int     {. exportc, dynlib .} = result = pop(s)
proc floatPop   (s:var TFloatList):  float   {. exportc, dynlib .} = result = pop(s)
proc stringPop  (s:var TStringList): string  {. exportc, dynlib .} = result = pop(s)
proc cstringPop (s:var TCstringList):cstring {. exportc, dynlib .} = result = pop(s)
#------------------------------------------------
proc intReverse    (s:TIntList):    seq[int]    {. exportc, dynlib .}= result = reverse(s)
proc floatRverse   (s:TFloatList):  seq[float]  {. exportc, dynlib .}= result = reverse(s)
proc stringReverse (s:TStringList): seq[string] {. exportc, dynlib .}= result = reverse(s)
proc cstringReverse(s:TCstringList):seq[cstring]{. exportc, dynlib .}= result = reverse(s)
#------------------------------------------------
proc IntList    (rest:varargs[int]):       seq[int]    {. exportc, dynlib .}=result = list(rest)
proc FloatList  (rest:varargs[float]):     seq[float]  {. exportc, dynlib .}=result = list(rest)
proc CstringList(rest:varargs[cstring]):   seq[cstring]{. exportc, dynlib .}=result = list(rest)
proc StringList (rest:varargs[string]):    seq[string] {. exportc, dynlib .}=result = list(rest)
#------------------------------------------------
proc CstringTable():TCstringTable{. exportc, dynlib .} = result = initTable[cstring,cstring]()
proc StringTable(): TStringTable {. exportc, dynlib .} = result = initTable[cstring,string]()
proc IntTable():    TIntTable    {. exportc, dynlib .} = result = initTable[cstring, int]()
proc FloatTable():  TFloatTable  {. exportc, dynlib .} = result = initTable[cstring,float]()
#------------------------------------------------
proc CstringListTable(): TCstringListTable {. exportc, dynlib .}=    result = initTable[cstring, TCstringList]()
# proc StringListTable():    TStringListTable    {. exportc, dynlib .}=    result = initTable[cstring, TStringList]()
proc IntListTable():   TIntListTable       {. exportc, dynlib .}=    result = initTable[cstring, TIntList]()
proc FloatListTable(): TFloatListTable     {. exportc, dynlib .}=    result = initTable[cstring, TFloatList]()
#------------------------------------------------
proc IntKVTuple     (key:cstring, val:int)         :TIntKVTuple     {. exportc, dynlib .}= (key:key, val:val) 
proc FloatKVTuple   (key:cstring, val:float)       :TFloatKVTuple   {. exportc, dynlib .}= (key:key, val:val) 
proc CstringKVTuple (key:cstring, val:cstring)     :TCstringKVTuple {. exportc, dynlib .}= (key:key, val:val) 
proc IntListKVTp    (key:cstring, val:TIntList)    :TIntListKVTp    {. exportc, dynlib .}= (key:key, val:val) 
proc FloatListKVTp  (key:cstring, val:TFloatList)  :TFloatListKVTp  {. exportc, dynlib .}= (key:key, val:val) 
proc CstringListKVTp(key:cstring,val:TCstringList) :TCstringListKVTp{. exportc, dynlib .}= (key:key, val:val) 
#------------------------------------------------









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





proc genPyType* [T] (data:T, typename:cstring): PyType[T] =
    result = PyType[T](data:data, typename:typename)


discard """
proc genIntListPyType(data: TIntList, typename:cstring): PyType[TIntList] {. exportc, dynlib .}= 
  #result = PyType[TIntList](data:data,typename:typename)
  return genPyType(data, typename)

proc getPyObject(obj:pointer):PPyObject {. exportc, dynlib .}= 
    echo "getPyObject: cast void* to object inside nimrod"
    var ret = cast[PPyObject](obj)
    var list: PPyObject
    discard ret[].ob_type
    var s: cstring = "Hello from C!"
    try:
      echo ret[].ob_refcnt
      echo "pass"
      return Py_BuildValue("s", s)
      #echo PyArg_ParseTuple(ret, "O", addr(list) )
      #result = Py_BuildValue("O", list)
    except: 
      echo "error message"
      raise newException(OSError, "some error occured as generating PyArg")
    #return ret

proc py_returnChar*(self: PPyObject; args: PPyObject): PPyObject = 
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



var e = cstring("")
var tmparr = [
        TPyMethodDef(ml_name:cstring("returnList")        , ml_meth:py_returnList        , ml_flags:METH_VARARGS , ml_doc:e ) ,
        TPyMethodDef(ml_name:cstring("returnDouble")      , ml_meth:py_returnDouble      , ml_flags:METH_VARARGS , ml_doc:e )    ,
        TPyMethodDef(ml_name:cstring("returnDynamicList") , ml_meth:py_returnDynamicList , ml_flags:METH_VARARGS , ml_doc:e )    ,
        TPyMethodDef(ml_name:cstring("getObject")         , ml_meth:py_getObject         , ml_flags:METH_VARARGS , ml_doc:e )    ,
        TPyMethodDef(ml_name:cstring("modifyList")        , ml_meth:py_modifyList        , ml_flags:METH_VARARGS , ml_doc:e )    ,
        TPyMethodDef()
        ]
var myModule_methods: PPyMethodDef = cast[PPyMethodDef](safe(tmparr, tmparr.len).mem)
#Python calls this to let us initialize our module

proc initmyModule*() = 
    discard Py_InitModule("myModule", myModule_methods)
"""



var psn  = Person(name:"hello",    age:13)
var obj  = PyType[TIntList](data: @[1,2,3], typename:"data")
echo "obj == ", obj
var oojj = genPyType( @[3,4,5] , "hello")

when isMainModule:
    echo "============= Call Inside Nimrod isMainModule ============="
    var s:cstring = "hello"
    var ss = "hello"
    var sss:float = 1.234355
    var ssss:cdouble = 1.22432423

    discard callback_topython("AnIdentifier") do (msg:cstring) -> bool:
        echo "msg:", msg
        return false



    echo "sizeof cstring:", sizeof(s)
    echo "sizeof string: ", sizeof(ss)
    echo "sizeof float: ", sizeof(sss)
    echo "sizeof cdouble:", sizeof(ssss)
    echo ""
    echo ""
    echo cstringToString(s)
    var ilst =  IntList(1,2,3,4)
    echo "pop ilist:", intPop(ilst) , " ilist == ", ilst
    echo FloatList(1.123,4.4234)

    echo stringToCstring("hello person")
    echo getPerson("hello person", 13)
    echo "end"

    var ret = @[1,2,3,4]
    echo reverse(ret)
    echo reverse(@[3,4,5,3])
    echo reverse(@[1.2,32.142])

    var xxx = {"Key":"value", "key2":"value2", "key3":"value3"}
    echo xxx[0], xxx[1], xxx[2], xxx[2][0]

    var yyy:Table[string, string] = initTable[string,string]()
    yyy["key"] = "value"

    var z = [(key:"key", valsss:"value")]
    echo z[0].key

    var zz = toTable(z)
    echo zz["key"]

    var xx:TStringTable = initTable[string,string]()
    xx["key"] = "value"

    var yy = StringTable()
    yy["name"] = "hello"


    var kk = 1
    var gg = cast[cint](kk)

    

    type Foo = ref object
        x, y: float
 
    var f: Foo
    new f
    echo "------------"
    echo f[]
    echo "------------"
    echo f[].x
    f[].y = 12
    echo f.y
    f.x = 13.5
    var x = 3
    var p = addr x
    echo p[]
    p[] = 42
    var y = 12
    p = addr y
    p = nil







discard """

proc py_returnChar*(self: PPyObject; args: PPyObject): PPyObject    = 
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


var e = cstring("")
var tmparr = [
        TPyMethodDef(ml_name:cstring("returnList"), ml_meth:py_returnList, ml_flags:METH_VARARGS, ml_doc:e    ), 
        TPyMethodDef(ml_name:cstring("returnDouble"), ml_meth:py_returnDouble, ml_flags:METH_VARARGS, ml_doc:e ),
        TPyMethodDef(ml_name:cstring("returnDynamicList"), ml_meth:py_returnDynamicList, ml_flags:METH_VARARGS, ml_doc:e ),    
        TPyMethodDef(ml_name:cstring("getObject"), ml_meth:py_getObject, ml_flags:METH_VARARGS, ml_doc:e ),            
        TPyMethodDef(ml_name:cstring("modifyList"), ml_meth:py_modifyList, ml_flags:METH_VARARGS, ml_doc:e ),
        TPyMethodDef()
        ]
var myModule_methods: PPyMethodDef = cast[PPyMethodDef](safe(tmparr, tmparr.len).mem)
#Python calls this to let us initialize our module

proc initmyModule*() = 
    discard Py_InitModule("myModule", myModule_methods)



#"""
