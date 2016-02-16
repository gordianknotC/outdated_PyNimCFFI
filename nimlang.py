#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'gordi_000'
from functools import lru_cache
from nimrheader_parser import get_callbackType
from nimrheader_parser import gen_cdef, ffi, get_type_data, setNimPath, \
    setCompiler, COMPILER_CONST, dlopen, typeof, getctype, string, sizeof, \
    new, cast, null, get_typeData
import re
from typing import Any, AnyStr, List
global lib, type_data

def is_table(name, data): return 'Data'   in data and 'Counter' in data and name[:5] == 'table'
def is_tuple(name, data): return 'Field0' in data
def is_seq(name, data):   return 'Sup'    in data and 'data' in data and data.get('Sup') == 'TGenericSeq'
def is_fn(name, data):    return 'ClPrc'  in data and 'ClEnv' in data
@lru_cache()
def get_generic(x): return dict(len= x.len, reserved = x.reserved)
@lru_cache()
def get_string(x): return dict(data=string(x.data), Sup=get_generic(x.Sup))

NimStringDesc = 'NimStringDesc'
TGenericSeq   = 'TGenericSeq'


def setup(compiler=COMPILER_CONST._MSC_VER, nim_file=None, dll_file=None, nim_path=None, nim_header=None):
    global lib, type_data
    setCompiler(compiler)
    setNimPath (nim_file=nim_file , dll_file=dll_file , nim_path=nim_path, nim_header=nim_header )
    lib        = dlopen()
    type_data  = get_type_data()
    print('___________ setup end ___________')


def genNimCType(ctypename:str, pydata:list, garbage_blocker=[]):
    print('1pydata:',pydata)
    if ctypename in ['int', 'float', 'double']: return pydata
    if ctypename in ['char*', 'char']:          return new('char[]', pydata)
    if ctypename == 'unsigned char':            return pydata
    if ctypename == TGenericSeq:                return new(TGenericSeq+'*', pydata)
    pointers = len(ctypename)- len(ctypename.strip('*'))
    typ = type_data['struct'][ctypename.strip('*')]
    items =  list(typ.items())
    print('ctypename', ctypename)
    print('fields:', typ)
    print('items:', items)
    print('pydata:', pydata)
    if   is_tuple(ctypename, typ):
        print('tuple:')
        cdata = [ genNimCType(d[1], pydata[i], garbage_blocker) for i,d in enumerate(items)]
        garbage_blocker.append(cdata)
        print('genreated cdata == ', cdata)
        if pointers:  return new(ctypename , cdata)
        else:         return new(ctypename +'*' , cdata)[0]

    elif is_seq  (ctypename, typ):
        print('pydata:', pydata)
        if not ctypename == NimStringDesc:
            Sup   = new(items[0][1]+'*', [len(pydata), sizeof(items[1][1]) ])
            cdata = [genNimCType( items[1][1],i, garbage_blocker) for i in pydata ]
        else:
            Sup   = new(items[0][1]+'*', [len(pydata), sizeof(items[1][1]) ])
            cdata = pydata

        garbage_blocker.append(cdata)
        print('genreated cdata:', cdata, 'blocker = ', garbage_blocker)
        if pointers: return new(ctypename, [Sup[0], cdata ])
        else:        return new(ctypename + '*', [Sup[0], cdata ])[0]

    elif is_table(ctypename, typ):
        print('pydata:', pydata)
        Counter = len(pydata)
        #items:  [('Data', 'keyvaluepairseq122131*'), ('Counter', 'int')]
        #pydata: [[0, b'tablekey1', b'value1'], [1, b'tablekey2', b'value2']]
        cdata = genNimCType( items[0][1] ,pydata, garbage_blocker)
        garbage_blocker.append(cdata)
        if pointers: return new(ctypename, [cdata, Counter ])
        else:        return new(ctypename + '*', [cdata, Counter ])[0]

        # fn not tested
    elif is_fn(ctypename, typ):
        cdata = new(ctypename + '*', pydata)
        garbage_blocker.append(cdata)
        return cdata

    else:
        print('table:')
        fn    = lambda arg: genNimCType(arg[0][1], arg[1])
        cdata = list(map(fn, zip(items, pydata) ))
        garbage_blocker.append(cdata)
        if pointers: return new(ctypename, cdata)
        else:        return new(ctypename + '*',cdata)[0]

@lru_cache()
def getCType_fromNimType(typename:str)-> List[str]:
    real_typename = type_data['typedefs'].get(typename)
    if real_typename: return real_typename, type_data['struct'][real_typename]
    else:
        if typename in type_data['struct']: return typename, type_data['struct'][typename]
        else: raise Exception('UnKnown nimrod type:', typename)


def genNimType(nimtype_name:str, pydata:list, garbage_blocker=[]):
    return genNimCType( getCType_fromNimType(nimtype_name)[0], pydata, garbage_blocker )

def from_nim(funcname, param=None):
    try:
            print(type_data)
            realtypes = type_data['func'][funcname]['fns']
            ret = {}
            if realtypes:
                for param_name, real_type in realtypes.items():
                    ret[param_name] = type_data['struct'][real_type]['ClPrc']
            return ret[param].strip('; ')
    except: raise Exception("Can't found function pointer for function:",
                            funcname, type_data['func'][funcname]['fns'])


class TCstring(object):
    __slots__ = ['nim']
    def __init__(self, s:str, encode):
        self.nim = ffi.new('char[]', s)
        super(TCstring, self).__init__(s, encode)

    def __repr__(self):
        return string(self.nim)

class PCstring(object):
    __slots__ = ['nim']
    def __init__(self, s:TCstring):
        self.nim = ffi.new('char**', s.nim)

    def __getitem__(self, item):
        if item == 0: return self.nim[0]
        else: raise Exception("index is not allowed in string pointer")

class PPCstring(PCstring):
    def __init__(self, s:PCstring):
        self.nim = ffi.new('char***', s.nim)

def _nimtable(typ):
    if   typ is int:    return lib.IntTable()
    elif typ is float:  return lib.FLoatTable()
    elif typ is str:    return lib.CstringTable()
    elif typ is list:
        _typ = type(typ[0])
        if   _typ is int:   return lib.IntListTable()
        elif _typ is float: return lib.FloatListTable()
        elif _typ is str:   return  lib.StringListTable()
        else:   raise TypeError('Invalid Table Type', typ, _typ)
    else:       raise TypeError('Invalid Table Type', typ)

def _nimseq(lst:list=None):
    typ = type(lst[0])
    ret = []
    if   typ is int:   ret = lib.IntList(lst)
    elif typ is float: ret = lib.FloatList(lst)
    elif typ is str:   ret = lib.CstringList(lst)
    else: raise TypeError('Invalid List Type', typ)
    return ret


default_transformer = {'int':None,'char*':'char[]', 'unsigned char':None}
#default_transformer.update({k:k+'*' for k in type_data['struct'].keys()})
def convert(data:tuple, types:[str], transformer:dict={}):
    transformer = transformer or default_transformer
    ret = []
    print(types, data)
    for i, d in enumerate(data):
        if isinstance(d, str):
            print('conver str fromn', d)
            d = bytes(d, 'utf-8')
            print('to bytes ', d)
        _otyp = types[i]
        _ntyp = type_data['typedefs'].get(_otyp.strip('*'))
        fields = type_data['struct'].get(_otyp.strip('*'))
        if not _ntyp and not fields:
            _typ  = transformer[_otyp]
            print('convert', d, 'to', _typ)
            if _typ:
                d = ffi.new( _typ , d)
                ret.append( d )
                print('converted:', d, string(d))
            else:     ret.append( d                  )
        else:
            _otyp = _otyp.strip('*')
            print(d, _otyp, _ntyp, fields)
            if   isinstance(d, NimBase): d = d.nim
            if   is_tuple(_otyp, fields): ret.append(NimTuple(d, real_type=_otyp ).nim)
            elif is_seq  (_otyp, fields): ret.append(NimSeq  (d, real_type=_otyp ).nim)
            elif is_table(_otyp, fields): ret.append(NimTable(d, real_type=_otyp ).nim)
            else:
                # object type
                raise Exception('Not Implement yet')
    return ret

def NimTGenericSeq(length=0, reserved=4):
    return ffi.new('TGenericSeq*', [length, reserved])

class KVPair(list):
    def __init__(self,*kv_pairs):
        super(KVPair, self).__init__(kv_pairs)

class SeqKVPair(list):
    def __init__(self, *data:[KVPair]):
        print('gen SeqKVPair:', [ [i,d] for i,d in enumerate(data) ])
        super(SeqKVPair, self).__init__( [ [i,d] for i,d in enumerate(data) ] )

class NimBase(object):
    __slots__ = [ 'nim', 'data_type', 'nim_data'] # nim_data: to prevent garbage collection, keep memory alive otherwise ffi will remove it
    def __init__(self, args, typename:str):
        real_type, data_type = getCType_fromNimType(typename)
        garbage_blocker = []
        cdata           = genNimCType(real_type, args, garbage_blocker=garbage_blocker)
        self.nim        = cdata
        self.data_type  = data_type
        self.nim_data   = garbage_blocker

    def __getattr__(self, item):
        if item in self.data_type:
              return getattr(self.nim, item)
        else: raise AttributeError(item)

    def genKeymap(self, pairs, initail_id=0):
        return {d[0]:'Field'+str(initail_id+i) for i, d in enumerate(pairs)}

class NimTuple(NimBase):
    __slots__ = ['nim','keymaps', 'data_type']
    def __init__(self, pairs:KVPair, typename:str=None, assertBytes=True):
        if assertBytes: args = strToBytes([i[1] for i in pairs])
        else:           args = [i[1] for i in pairs]
        super(NimTuple, self).__init__(args, typename)
        self.keymaps = self.genKeymap(pairs)

    def __getattr__(self, item):
        if item in self.keymaps:
              realkey = self.keymaps[item]
              _typ = self.data_type[realkey]
              return getattr(self.nim, realkey)
        else: raise AttributeError(item, 'should be one of {}'.format(self.keymaps.keys()))

    def __repr__(self):
        d = {k:getattr(self.nim, v) for k,v in self.keymaps.items()}
        return 'NimTuple {}'.format(d)

class NimTable(NimTuple):
    __slots__ = ['nim','keymaps', 'data_type']
    def __init__(self, seq_pairs:SeqKVPair, typename:str, asserBytes=True):
        # [(0, ('key1','value1'), ('key2','value2')),(1, ...), ...]
        if asserBytes: args = strToBytes([  [ [i[0]] + [k[1] for k in i[1]] ][0] for i in seq_pairs])
        else:          args = [ [i[0],i[1][1]] for i in seq_pairs]
        super(NimTuple, self).__init__(args, typename)
        self.keymaps = self.genKeymap(seq_pairs[0][1], initail_id=1)

    def __len__(self): return self.nim.Data.Sup.len

    def __repr__(self):
        nim = self.nim
        keymaps = self.keymaps
        d = [{k: getattr(nim.Data[i], v) for k,v in keymaps.items()} for i in range(len(self))]
        return 'NimTable {}'.format(d)

    def __getitem__(self, item):
        if   item < len(self): return self.nim.Data[item]
        else:raise Exception('Index {} out of range  0-{}'.format(item, len(self)))

nim_seq_ptn = ''
class NimSeq(NimBase):
    def __init__(self, data=None, typename:str=None, real_type:str=None):
        if not real_type:
            try:
                real_type   = type_data['typedefs'][typename]
                data_type = type_data['struct'][real_type]
            except:     raise Exception('UnKnown type: ', typename)
        else:           data_type = type_data['struct'][real_type]
        print('----------------------------')
        print('data type:', data_type)
        print('data: ', data)

        self.data_type = data_type
        length   = len(data)
        reserved = 8 if data_type['data'] in ['float64', 'double'] else 4
        seqdata  = NimTGenericSeq(length=length, reserved = reserved)

        if isinstance(data[0], NimBase):
            data = [i.nim[0] for i in data]
        self.nim_data = [seqdata, data]
        self.nim = ffi.new(real_type+'*', [seqdata[0], data])

    def __len__(self): return self.nim.Sup.len

    def __repr__(self):return "<NimSeq: {}>".format( self.nim.data )




nimstring_ptn = ''
class NimString(NimSeq):
    __slots__ = ['Sup', 'data', 'nim']
    def __init__(self, data:str=None):
        data = bytes(data, 'utf-8')
        super(NimString, self).__init__(real_type ='NimStringDesc', data= data)
    def __len__(self): return self.Sup.len
    def __repr__(self): return str(string(self.nim.data))






def _parse_nimdata_struct(typename:str, pointer=0):
    type_info = type_data['struct'].get(typename)
    if type_info:
        pass

    else: raise Exception('UnKnown nim data type:', typename)

def unifyList(data:list, typ):
    ret = []
    if isinstance(data, list):
           for i in data: ret.extend([ unifyList(i,typ) ] )
           ret = [ret]
    else:  ret.append( typ(data) )
    return ret[0]

def strToBytes(data:list):
    ret = []
    if isinstance(data, list) or isinstance(data, tuple):
        for i in data:            ret.extend ([strToBytes(i)])
        ret = [ret]
    elif isinstance(data, str):   ret.append (bytes(data, 'utf-8'))
    else:                         ret.append (data)
    return ret[0]

class typenameStack(object):
    __slot__ = ['typenmae','cdata']
    def __init__(self,typename:str=None, cdata:ffi.CData=None):
        self.typename = typename; self.cdata = cdata


def ref(node, kind, pointer):
    print('ref info:' , node, kind, pointer)
    if kind == 'pointer' or pointer != 0:
        node = node[0]
        print('deref node:', node, pointer -1)
        return ref(node, None, pointer-1)
    return node

def cToPy(node, typenames:[typenameStack]=None):
    typ      = typeof(node)
    typename = getctype(typ)
    pointer  = len(typename.split('*')) -1
    kind = typ.kind

    if typename[0:4] == 'char': return ffi.string(node)
    if   kind == 'array':
        print('kind array')
        item = typ.item
        if item.kind == 'primitive':
            if item.cname == 'char':
                print('char array')
                try:    return string(node)
                except: return None
            else:
                print('primitive array')
                # primitive array
                if   typenames is None: return [node[i] for i in range(typ.length)]
                elif typenames[-1].typename:
                    print(typenames[-1].cdata)
                    return [ node[i] for i in range(typenames[-1].cdata.Sup.len)]
                else: raise Exception('Uncaught Exception')
        else:
            # not a primitive array
            return [ nimToPy(i, typenames) for i in range(typ.length)]

    elif kind == 'primitive': return int(node)
    elif kind == 'struct':
        ret = []
        fields = typ.fields
        nimtyp = typenames[-1].typename
        for fieldname, subtype in fields:
            print(typename, fieldname, subtype)
            _typ = getctype(typeof(subtype))
            #print('--- parse struct ---')
            #print(typ.type.kind, field, _typ)
            #print(s, fields)
            if subtype.type.kind == 'primitive':
                #print('try get primitieve value')
                #print('value = ', _typ, 'field', field)
                if _typ == TGenericSeq:
                    field_value = None if not nimtyp else nimtyp[fieldname]
                    ret.append( [fieldname, field_value] )
                    continue
                elif _typ == NimStringDesc:  ret.append([fieldname, string(node)])
                try:    field_value = getattr(node, fieldname)
                except:
                    #print('[Warning1] cannot get field value from', s, field)
                    field_value = None
                #print('getted', field, field_value)
                ret.append( [fieldname, field_value] )
                continue
            else:
                #print('try get non primitive')
                try:    field_value = getattr(node, fieldname)
                except:
                    #print('[Warning1] cannot get field value from', s, field)
                    field_value = None
                    ret.append([fieldname, field_value])
                    continue
                #print('getted', field, field_value)
                field_value = nimToPy(field_value, typenames)
                #print('converted fieldvalue = ', field_value)
                ret.append( [fieldname, field_value] )
                continue
        #print('return struct')
        return ret

    elif pointer and typename[0:4] != 'char':
        node = ref(node, kind, pointer)
        if not is_nimtype(typename): return cToPy(node, typenames)
        else:                        return nimToPy(node, typenames)


def is_nimtype(typename):
    if typename.strip(' *') in type_data['struct'].keys(): return True
    return False


def nimToPy(node, typenames:[typenameStack]=None, pointer:int=None):
    typ         = typeof(node)
    typename    = getctype(typ)
    typenames   = typenames or []
    typename    = typename.strip(' *')
    is_nim      = typename in type_data['struct'].keys()
    result      = {}

    print('typename == ', typename, typ)
    if not is_nim:
        print('1           typename:', typename, 'switch to cToPy')
        return cToPy(node, typenames)

    typenames.append(typenameStack(typename=typename, cdata=node))
    fields = type_data['struct'][typename].items()
    for k,v in fields:
        print(k,v)
        field_value = getattr(node, k)
        if isinstance(field_value, ffi.CData):
            result[k]   = nimToPy(field_value, typenames)

        else: result[k] = field_value
    return result





if __name__ =='__main__' :
    def test_nimString():
        print('------------------------------------------')
        print('        test NimString class              ')
        print("------------------------------------------")
        ret = NimString('hello bb')
        print('ret = ', ret)
        print('ret.nim = ', ret.nim)
        print('len(ret) = ', len(ret))
        print('pass ret to nim, test for valid type')
        rr = lib.stringToCstring(ret.nim)
        print('returned cstring == ', string(rr))
    #
    def test_nimSeq():
        print('------------------------------------------')
        print('        test NimSeq    class              ')
        print("------------------------------------------")
        print('test seq[int]')
        ret = NimSeq(typename='TIntList', data=[1,2,3,4])
        print('ret = ', ret)
        print('ret.nim = ', ret.nim)
        print('len(ret) = ', len(ret))
        print('ret.data = ', ret.nim.data[0])
        print('ret.Sup == ', ret.Sup)
        print('ret.Sup.len:', ret.Sup.len)

    def test_nimTule():
        print('------------------------------------------')
        print('        test TIntKvTuple    class              ')
        print("------------------------------------------")
        print("call"," NimTuple([('key', 'IndexKey'),('value', 13)], typename ='TIntKVTuple' )" )
        pair = KVPair(['index_key','some_id'],['sort_genre',13])
        print('pair = ', pair)
        ret = NimTuple( pair, typename ='TIntKVTuple' )
        print('ret = ', ret)
        print('ret.key', cToPy(ret.index_key))
        print('ret.value', ret.sort_genre)
        print('ret.nim.Field0:', ret.nim.Field0)
        print('ret.nim.Field1:', ret.nim.Field1)
        print('ret.nim.Field0:', cToPy(ret.nim.Field0))

        print('------------------------------------------')
        print('        test TIntListKVTp    class        ')
        print("------------------------------------------")
        args = [('key', 'list_data'), ('value', [1,2,3,4,5])]
        ret = NimTuple( args, typename='TIntListKVTp')
        print('ret = ', ret)
        print('ret.key == ', cToPy(ret.key))
        print('---------------')
        print( ret.value )
        print( ret.value.data )
        print( ret.value.Sup  )
        print( ret.value.Sup.len )
    #
    def test_nimTule2():
        # print('----------------------------------------')
        # print('         test TIntKvTuple Creation     ')
        # print('----------------------------------------')
        # key = ffi.new("char[]" ,b"indexKey")
        # value = 13
        # data = [key, value]
        # ret = ffi.new('tintkvtuple122025*', data)
        # print('ret = ', ret)
        # print('ret.Field0', ret.Field0)
        # print('ret.Field0', cToPy(ret.Field0))
        # print('ret.Field1', ret.Field1)
        print('----------------------------------------')
        print('         test TIntKvTuple class         ')
        print('----------------------------------------')
        print("call"," NimTuple([('key', 'IndexKey'),('value', 13)], typename ='TIntKVTuple' )" )
        ret = NimTuple([('key', 'IndexKey'),('value', 13)], typename ='TIntKVTuple' )

        print('ret.key', cToPy(ret.key))
        print('ret.value', ret.value)
        print('ret.nim.Field0:', ret.nim.Field0)
        print('ret.nim.Field0:', cToPy(ret.nim.Field0))
        print('ret = ', ret)
    #
    def test_cstringTable_raw():
        print('----------------------------------------')
        print('         test cstringTable Creation     ')
        print('----------------------------------------')
        n = ffi.new
        tp1 = n('keyvaluepair122136*', [0, n('char[]', b'Key0'), n('char[]', b'value0')])
        tp2 = n('keyvaluepair122136*', [1, n('char[]',b'Key1'), n('char[]',b'value1')])
        Sup = NimTGenericSeq(2,4)
        Data = ffi.new('keyvaluepairseq122133*', [Sup[0] , [tp1[0], tp2[0]] ])
        Counter = 2
        data = [Data, Counter]
        ret = ffi.new('table122130*',data)
        print('ret = ', ret, 'ret.Counter == ', ret.Counter, 'ret.Data == ', ret.Data)
        print('ret.Data[0].Field0', ret.Data.data[0].Field0)
        print('ret.Data[0].Field1', ret.Data.data[0].Field1)
        print('ret.Data[0].Field2', ret.Data.data[0].Field2)


    def test_nimTypeConvertion():
        # print('-------------------------------------')
        # print('         test_nimTypeConvertion')
        # print('-------------------------------------')
        # n = ffi.new
        garbage_blocker = []
        # genNimType('keyvaluepair122090',[0, b'hello1', 13])
        # kvpair = genNimType('keyvaluepair122134',[1, b'hello2', b'mygod1'])
        # genNimType('tintkvtuple122025', [b'kvtupleKey', 13], garbage_blocker=garbage_blocker)
        # print('kvpair = ', kvpair)
        # print('kvpair.Field1 = ', kvpair.Field1)
        # print(typeof(kvpair))
        # print(typeof(kvpair).fields)
        #
        # print('----------------------------------------------')
        # print('      gen KvSequence                          ')
        # print('----------------------------------------------')
        # # Sup:len:3,reserved:4   data:
        # kvseq = genNimType('keyvaluepairseq122131',  [[0, b'hello1', b'mygod1'], [1, b'hello2', b'mygod2']] )
        # print('kvseq == ', kvseq)
        # print('----------- sho seq data --------------')
        # print(kvseq.data[0].Field0)
        # print( cToPy(kvseq.data[0].Field1))
        # print( cToPy(kvseq.data[0].Field2))
        #
        # print(kvseq.data[1].Field0)
        # print( cToPy(kvseq.data[1].Field1))
        # print( cToPy(kvseq.data[1].Field2))
        print('----------------------------------------------')
        print('         gen seq: NimStringDesc                ')
        print('----------------------------------------------')
        data = b'hello ev body'
        nimstring = genNimCType('NimStringDesc', data)
        print(nimstring)
        #genNimCType(getCType_fromNimType('TIntList')[0], [1,2,3,4,5], garbage_blocker )  # use genRealType instead of genNimType
        print('----------------------------------------------')
        print('         gen seq: TIntList                ')
        print('----------------------------------------------')
        intlist = genNimType('TIntList', [1,2,3,4,5], garbage_blocker)
        print(intlist)

        print('----------------------------------------------')
        print('            gen CstringTable                  ')
        print('----------------------------------------------')
        #genNimType('Cstring')
        Data = [[0, b'tablekey1', b'value1'], [1, b'tablekey2', b'value2']]
        Counter = 2
        print( 'cstring table ctype:',getCType_fromNimType('TCstringTable'))
        #table = genNimCType( getCType_fromNimType('TCstringTable')[0] , Data, garbage_blocker)
        table = genNimType('TCstringTable',  Data, garbage_blocker)


        print('table = ', table)
        print('table.Data = ', table.Data)
        print('table.Data.data = ', table.Data.data)
        print('table.Data.data[0] = ', table.Data.data[0])
        print( typeof( table.Data.data))
        print( typeof( table.Data.data))
        print( typeof( table.Data.data[0]))
        print( typeof(table.Data.data[0]).fields )
        print( table.Data.data[0].Field0)
        print( cToPy(table.Data.data[0].Field1))
        print( cToPy(table.Data.data[0].Field2))
        #
        print('----------------------------------------------')
        print('      gen Nim Object                          ')
        print('----------------------------------------------')
        obj = genNimType('Vector', [1.1,2.2,3.3], garbage_blocker)
        print('obj = ', obj)
        obj.X = 1.2324324
        print('obj.x = ', obj.X)
        print('obj.Y = ', obj.Y)
        print('obj.Z = ', obj.Z)
        obj.X = 1000
        print('obj.X = ', obj.X)

    def test_nimcallback():
        @ffi.callback(from_nim('callback_topython', param='callback'))
        def callback(msg, clenv):
            print("sho message inside python")
            print(msg, string(msg))
            if string(msg) == "is it an identifier?": return True
            else:                                     return False

        callback_struct = new( get_callbackType( 'callback_topython', 'callback') )[0]
        callback_struct.ClPrc = callback
        callback_struct.ClEnv = null
        lib.callback_topython(b"testSuite", callback_struct)
        #lib.callback_topython("", gen_nimCallback()


    print("==============================================================")
    setup( nim_file=r'nim_test.nim', dll_file=r'nim_test.dll', nim_path=r'F:/Nim', nim_header=r'nimcache/nim_test.h')
    print('type_data = ', type_data)
    test_nimTule()
    test_nimTule2()
    test_cstringTable_raw()
    #test_Table()
    test_nimTypeConvertion()
    test_nimcallback()





