#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'gordi_000'
from nimlang import setup
setup( nim_file=r'../nim_test.nim', dll_file=r'../nim_test.dll', nim_path=r'F:/Nim', nim_header=r'../nimcache/nim_test.h')
from nimlang import *
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
print('type_data = ', type_data)
test_nimTule()
test_nimTule2()
test_cstringTable_raw()
#test_Table()
test_nimTypeConvertion()
test_nimcallback()