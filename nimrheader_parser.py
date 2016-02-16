#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'gordi_000'
from karnickel import macro
import re, os
from collections import OrderedDict
from cffi import FFI

ffi       = FFI()
typeof   = ffi.typeof
getctype = ffi.getctype
string   = ffi.string
sizeof   = ffi.sizeof
new      = ffi.new
cast     = ffi.cast
null     = cast('void*', 0)

compilers = ['__BORLANDC__','_MSC_VER','__WATCOMC__','__LCC__','__GNUC__','__DMC__','__POCC__','__TINYC__','__clang__']
HEADER    = r'nimcache/nim_test.h'
NIMSOURCE = r'nim_test.nim'
NIMBASE   = r'F:/Nim/lib/nimbase.h'
DLL       = r'nim_test.dll'
COMPILER  = [compilers[1]] + ['WIN32', '_WIN32']
defines   = OrderedDict()
type_map  = {'NI':'int','NI*':'int*'}
catch_block = False
verify      = []
type_data   = None
primitive_types = ['cstring', 'string', 'float', 'int', 'unsigned char']
nim_c_type_map = {'int':'int', 'cstring':'char*','string':'NimStringDesc*','float':'double', 'NIM_BOOL':'unsigned char'}

pretypedef = '''
typedef void* _NULL ;
'''


class COMPILER_CONST(object):
    __slots__ = ['__BORLANDC__','_MSC_VER','__WATCOMC__','__LCC__','__GNUC__','__DMC__','__POCC__','__TINYC__','__clang__']
    def __init__(self):
        for key in self.__slots__:
            setattr(self, key, key)
COMPILER_CONST = COMPILER_CONST()

def dlopen():
    print('load DLL:', os.path.abspath(DLL))
    lib = ffi.dlopen(DLL)
    ffi.cdef(gen_cdef())
    return lib

def setCompiler(c:str):
    global COMPILER, COMPILER_CONST
    if c == COMPILER_CONST._MSC_VER: COMPILER = [c, 'WIN32', '_WIN32']
    else:                            COMPILER = [c]

def setNimPath(nim_file=None, nim_header=None, dll_file=None, nim_path=None):
    global NIMBASE, NIMSOURCE, HEADER, DLL
    abspath, joinpath, splitpath = os.path.abspath, os.path.join, os.path.split
    if nim_file:
                 nim_file  = abspath(nim_file)
                 paths     = splitpath( nim_file )
                 NIMSOURCE = nim_file
                 HEADER    = joinpath(paths[0],'nimcache', paths[1].replace('.nim','.h') )
    if nim_header:HEADER   = nim_header
    if dll_file: DLL       = abspath(dll_file)
    if nim_path: NIMBASE   = os.path.join( abspath(nim_path), 'lib', 'nimbase.h')

    if not dll_file and nim_file: DLL       = nim_file.replace('.nim', '.dll')
    if not nim_file and dll_file: NIMSOURCE = dll_file.replace('.dll', '.nim')
    if not nim_header and not HEADER and dll_file:
        paths  = splitpath(DLL)
        HEADER = joinpath(paths[0], 'nimcache', paths[1].replace('.dll', '.h'))
    if not nim_path: raise Exception('nim path not found')

def fetch_nimbase_h():
    def is_catch_defined(rec):
        def defined(x):
            return x[-1*len(COMPILER)-1:-1] in COMPILER
        tmp = [i for i in rec if 'defined(' in i]
        under_defined = [i for i in tmp if defined(i)==True ]
        return under_defined
    def try_catch_defined(rec):
        global catch_block
        if is_catch_defined(rec) and not catch_block:
            skip_conditions.append(len(condition_stack)-1)
            catch_block = True
            #print('         catch block == True')
        elif catch_block:
            #print('found define0', rec[0],'1', rec[1].strip())
            if rec[1].strip() == 'define':
                value = ' '.join(rec[3:])
                if value.find('/*'): value = value.split('/*')[0]
                defines[rec[2]] = value
            #print('          catched defiend line:',' '.join(rec) )

    global catch_block
    condition_stack = []
    is_incondition = lambda : len(condition_stack) > 0
    skip_conditions = []
    skip_this = lambda :skip_conditions[-1] == condition_stack[-1]

    with open(NIMBASE, 'r') as f:
        for lineno, line in enumerate(f):
            rec = [i.lstrip('# ') for i in line.strip(' ;\n').split()]
            if rec:
                # typedef --------------------------------
                if rec[0] == 'typedef':
                    #print(lineno, '     typedef', line.strip())
                    if rec[1] not in ['struct', 'signed', 'unsigned', 'long'] and not rec[1] in type_map:
                        type_map[rec[2]] = rec[1]
                        type_map[rec[2]+'*'] = rec[1]+'*'
                    elif rec[1] in ['signed', 'unsigned', 'long']:
                        type_map[rec[-1]] = ' '.join(rec[1:-1])

                    # if else..---------------------------------------------------------------
                elif rec[0] in ['if', 'endif','elif', 'else', 'ifdef', 'ifndef' ]:
                    catch_block = False
                    #print(lineno, '     condition', line.strip())
                    if rec[0] == 'ifndef':
                        condition_stack.append(len(condition_stack))
                        skip_conditions.append(len(condition_stack) - 1)
                    elif rec[0] == 'ifdef':
                        condition_stack.append(len(condition_stack))
                        skip_conditions.append(len(condition_stack) - 1)
                    elif   rec[0] == 'if':
                        condition_stack.append(len(condition_stack))
                        try_catch_defined(rec)
                        #print(lineno,'        append:', condition_stack)
                    elif rec[0] == 'elif':
                        if skip_conditions:
                            if skip_this():  continue
                        try_catch_defined(rec)
                    elif rec[0] == 'else':
                        skip_conditions.append(len(condition_stack)-1)
                        catch_block = True
                    elif rec[0] == 'endif':
                        i = condition_stack.pop()
                        skip_conditions = [k for k in skip_conditions if k != i]
                        #print(lineno,'        pop:', condition_stack)
                    else:
                        raise Exception('Uncaught exception')

                elif is_incondition():
                    #print(lineno, '     in condition', line.strip())
                    if skip_conditions and not catch_block:
                        if skip_this():  continue
                    try_catch_defined(rec)
                    #outside of if else--------------------------------------
                else:
                    #print(lineno, '     out', line.strip())
                    if rec[0].strip() == 'define':
                        defines[rec[1]] = ' '.join(rec[2:])


# print(type_map)
# print('------not compoleted------------')
# type_map.update(defines)
# print(defines)
# for d in defines:
#     print(d)
# print('------- almost done-----------')
def parse_HEADER():
    def enter(key:str, name:str=''):
        default =  dict(struct={'name':name, 'data':OrderedDict()})
        if   key == 'struct':      type_data[-1] = default
        elif key == 'call struct': type_data[-1] = default

    def exit(): type_data.append(OrderedDict())

    global type_data
    ret = ''
    ptn       = r'\(([a-zA-Z ,_*0-9#\[\]]+)\)' # transform (var,var) to ( var, var)
    ptn2      = r'([a-zA-Z0-9_#\[\]*]+),'
    exit_ptn  = r'}[ ]*[a-zA-Z0-9_*]*;'
    type_data = [OrderedDict()]
    callbacks = []
    seqtypes  = {}
    valid_field       = lambda x: x.split('[',1)[0]
    #methods_typ_pairs, typedefs, emit_header = parse_nim_source()
    methods_typ_pairs, typedefs = parse_nim_source()
    for key,value in defines.items():
        if not '(' in key:
            try:
                    int(value)
                    _verify = '#define {key} {value}\n'.format(key=key, value=value)
            except: _verify = '#define {key} ...\n'.format(key=key)
            verify.append(_verify)
            ret += _verify

    with open(HEADER, 'r') as f:
        get       = type_map.get
        #linedata = f.read().strip()
        #linedata = linedata + '\n' + emit_header
        for line in f:
            if not line: continue
            if 'N_LIB_IMPORT N_CDECL(' in line:
                line = line.split('N_LIB_IMPORT N_CDECL(')[1]
                rtyp_args = [ [k.strip('();\n ') for k in i.split(',')] for i in line.split('(')]
                rtyp_name, argtyp_argname = rtyp_args
                real_rtyp, fname = rtyp_name
                args = ' , '.join(argtyp_argname)
                line = '{real_rtyp} {fname}({args});'.format(real_rtyp=real_rtyp, fname=fname, args=args)

            elif 'N_NOCONV(' in line or 'N_NIMCALL(' in line:
                line = [ i.strip('() ,;\n').split(',') for i in line.split('(',1)[1].split('(')]
                rtyp_name, rtyp_args = line
                real_rtyp,fname = rtyp_name
                args = ' , '.join(rtyp_args)
                line = '{real_rtyp} {fname}({args});'.format(real_rtyp=real_rtyp, fname=fname, args=args)

            elif line[0] == '#' or line[0:2] == r'//':
                continue

            line = re.sub(ptn, r'( \1 )', line)
            line = re.sub(ptn2, r'\1 ,', line)
            tmpline = ' '.join( get(i) or i for i in line.split()) + '\n'
            line    = tmpline
            is_struct      = type_data[-1].get('struct') is not None
            is_call_struct = type_data[-1].get('struct')['name'] == '##' if is_struct else False

            if tmpline[0:7] != 'typedef':
                # struct enter
                if not type_data[-1] and tmpline[0:6] == "struct":
                    structname = tmpline.split(' ',1)[1].strip(' \n;{')
                    enter('struct', structname)
                    #type_data[-1] = dict(struct={'name':structname, 'data':OrderedDict()})
                    for i in typedefs.keys():
                        if re.match( i.lower() + '[0-9]+', structname): typedefs[i] = structname

                    # struct exit
                elif is_struct and re.match(exit_ptn, tmpline.strip(' \n')):
                    if is_call_struct:
                            structname = tmpline.strip(' ;\n}')
                            type_data[-1]['struct']['name'] = structname
                            callbacks.append(structname)
                            exit()
                    else:   exit()

                    # inside struct
                elif is_struct:
                    #print('is struct:', tmpline)
                    if is_call_struct:
                        #print('is callstruct:', tmpline)
                        k           = 'N_NIMCALL_PTR'
                        #print(tmpline)
                        if tmpline[:len(k)] == k:
                            args_lbound = tmpline.rfind('(')
                            args        = tmpline[args_lbound:]
                            fn_retype, fn_name = tmpline[len(k)+1:args_lbound-1].strip(') ').split(',')
                            typename    = fn_name
                            typ         = '{ret} (*{fname}){args};\n'.format(ret=fn_retype.strip(), fname=fn_name.strip(),args=args.strip('; \n'))
                            line        = typ
                        else:
                            typ, typename = tmpline.strip(' \n;').rsplit(' ',1)
                        type_data[-1]['struct']['data'][typename.strip()] = typ.strip()
                        #print('set ', typename.strip(), 'to', typ.strip())
                    else:
                        typ, typename = tmpline.strip(' \n;').rsplit(' ',1)
                        type_data[-1]['struct']['data'][valid_field(typename)] = typ.strip()

                    # function
                elif not is_struct and ord(tmpline[0]) in range(65, 123) and tmpline.strip()[-1] == ';': # A..Z_a..z
                    #print(tmpline)
                    rtype, funcname   = [i for i in line.strip(' ;\n').split('(',1)[0].strip().split(' ') if i]
                    argname_typ_pairs = [i.strip().split(' ') for i in line.strip(' ;\n').split('(')[1].strip(' )').split(',')]
                    type_data[-1]['func'] = {
                        'rtype':   rtype.strip() ,
                        'funcname': funcname.strip() ,
                        'args':     argname_typ_pairs }
                    for i, _tp_name in enumerate(argname_typ_pairs[:]):
                        if len(_tp_name) == 1: break # no argutments (void)
                        argtype, argname = _tp_name
                        #print(i, _tp_name, len(_tp_name),  argtype[-2:])
                        if argname == 'Result':
                            if rtype == 'void': type_data[-1]['func']['result'] = True
                            else:               raise Exception('Uncaught exception, found one argument named "Result" in an invalid position in line: OrderedDict()'.format(line))
                        if i == 0:
                            if argtype[-2:] == '**':
                                type_data.append(OrderedDict())
                                #print("_________ match ___________")
                                type_data[-1]['object_methods'] = {'objname':argtype,'funcname':funcname}
                                #print(type_data[-4:])
                    type_data.append(OrderedDict())

            elif tmpline[0:len('typedef struct {')] == 'typedef struct {':
                # function PTR...
                print('enter call struct', tmpline)
                enter('call struct', name='##')

            ret += line

    if type_data and not type_data[-1]: type_data.pop()
    tmp = {'struct':OrderedDict(), 'func':OrderedDict(), 'object_methods':OrderedDict()}
    for i in type_data:
        if   i.get('struct'):
            typename = i['struct']['name'].strip()
            data     = i['struct']['data']
            tmp['struct'][typename] = data
            if typename[0:2] == 'TY' and data.get('Sup') == 'TGenericSeq' and data.get('data'):
                seqtypes[typename] = data

        elif i.get('func'):
            fns = {k[1]:k[0] for k in i['func']['args'] if k[0] in callbacks}
            tmp['func'][i['func']['funcname']] ={'args':i['func']['args'], 'rtype':i['func']['rtype'], 'fns':fns }
        elif i.get('object_methods'):
            #print('found object methods')
            argtype  = i['object_methods']['objname'].strip()
            funcname = i['object_methods']['funcname'].strip()
            if funcname in methods_typ_pairs: argtype = methods_typ_pairs[funcname]
            if not tmp['object_methods'].get(argtype): tmp['object_methods'][argtype] = [funcname]
            else:                                      tmp['object_methods'][argtype].append(funcname)
        else: raise Exception('Uncaught Exception')

    # search seqence list type
    tables = [ [i, tmp['struct'][i]] for i in tmp['struct'].keys() if i[0:5] == 'table' ]
    for nim_generic, nim_typ in typedefs.items():
        nim_typ = re.findall(r'seq\[([a-zA-Z0-9]+)\]', nim_typ)
        if nim_typ:
            _typ = nim_c_type_map[nim_typ[0]]
            for cstruc_name, cstruc_data in seqtypes.items():
                if _typ == cstruc_data['data']:
                    typedefs[nim_generic] = cstruc_name
        if nim_generic[0:6] == 'Table[':
            types = [i.strip() for i  in nim_generic.split('[')[1].strip(']').split(',')]
            verify_table_types( tmp,typedefs,nim_generic, typedefs[nim_generic], types[1], tables)

    type_data = tmp
    type_data['typedefs'] = typedefs
    return pretypedef + ret

def verify_table_types(db,typedefs, nim_generic_typ , nim_typ, sought_typ, tables):
    # nim_generic_typ: Table[cstring,int], nim_typ: TintTable, sought_typ: int
    ntyp = nim_c_type_map.get(sought_typ)
    if not ntyp:
          for _typ in primitive_types:
              if _typ in sought_typ.lower(): sought_typ = nim_c_type_map[_typ]; break
    else: sought_typ = ntyp
    #print("========== verify =================", nim_typ, sought_typ)
    def search(_db, keys, typ):
        fields = _db.get(keys[-1])
        deep_scans = [v for v in fields.values() if v in _db]
        if not deep_scans:
            _typ = _db[keys[-1].strip('*')].get('data') or _db[keys[-1].strip('*')].get('Field2')
            if _typ == sought_typ: return keys
        else:
            for v in deep_scans:
                ret = search(_db, keys + [v], typ)
                if ret: return ret

    def search_old(_db, keys, typ):
        fields = _db.get(keys[-1])
        #print("    fields:", fields)
        if not fields:
            if keys[-1][0:2] == 'TY':
                  if _db[ keys[-1].strip('*') ]['data'] == sought_typ:
                    return keys
            else: return
        else:
            for k,v in fields.items():
                ret = search(_db, keys + [v], typ)
                if ret: return ret

    for t in tables:
        keypath = search(db['struct'], [t[1]['Data'].strip('*')], sought_typ)
        if keypath:
            print( nim_typ, 'key path == ', keypath, ' verified t == ', t[0])
            typedefs[nim_typ] =t[0]
            typedefs[nim_generic_typ] = keypath[0]

def parse_nim_source():
    method_typ_pairs = OrderedDict()
    typedefs =OrderedDict()
    proc_ptn = r'\bproc ([a-zA-Z_0-9]+)'
    args_ptn = r'([a-zA-Z_0-9 ]+):([a-zA-Z_0-9 \[\]]+)'
    rtyp_ptn = r':([a-zA-Z_0-9 \[\]]+)='
    emit_ptn = r'{.[ ]*emit:[ ]*"""[ ]*//header'
    fetch_emit = False
    tab = 0
    tab_stack = []
    under_typedef = True
    typedef_tab = 0
    #emit_header = ""
    #emit_to_header = lambda x: re.match(emit_ptn, x)
    with open(NIMSOURCE) as f:
        for line in f:
            tab_stack.append(tab)
            tab  = len(line) - len(line.lstrip())
            line = line.strip()

            if tab <= typedef_tab and not fetch_emit: under_typedef = False
            if under_typedef and not fetch_emit:
                if '=' in line:
                    typename, typ =  line.split('=',1)
                    typename = typename.strip()
                    is_generic = typename[-1] == ']'
                    if not is_generic:
                        if typ.strip()[-1] == ']':
                            #print(typ)
                            seq_type = re.findall(r'seq\[([a-zA-Z0-9]+)\]', typ)   # seq[T] generic type
                            if seq_type:  typedefs[typename] = typ.strip(); typedefs[typ.strip()] = typename
                            else:         typedefs[typename] = typ.strip(); typedefs[typ.strip()] = typename
                        else:                          typedefs[typename] = typ.strip()

            if line.strip() == 'type' and not fetch_emit:
                under_typedef = True
                typedef_tab = tab
                continue

            # if fetch_emit and line == '"""}':
            #     fetch_emit = False
            #
            # if fetch_emit:
            #     emit_header += line + '\n'
            #
            # if emit_to_header(line):
            #     fetch_emit = True
            #     continue

            if line[0:4] == 'proc' and not fetch_emit and not under_typedef:
                _founded = re.findall(proc_ptn, line)
                if _founded: funcname = _founded[0]
                else:       continue
                _args = line.split('(',1)[1]
                args        = re.findall(args_ptn,_args)
                if args:
                    if args[0][1].strip()[0:4] == 'var ':
                        method_typ_pairs[funcname] = args[0][1].split('var ')[1].strip()
                else: pass
                #rtype_match = re.search(rtyp_ptn, _args)
                #if rtype_match: rtype = rtype_match.group().strip()

    print('============== nimsource ===============')
    from pprint import pprint
    #print('emit header --------------')
    #print(emit_header)
    pprint(method_typ_pairs)
    pprint(typedefs)
    return method_typ_pairs, typedefs #, emit_header




def get_type_data():
    return type_data

def gen_cdef(header:str = None, nimbase_h:str=None):
    if header: HEADER = header
    if nimbase_h: nimbase = nimbase_h
    fetch_nimbase_h()
    ret =  parse_HEADER()
    print("===========================")
    print("cdef:")
    print("---------------------------")
    print(ret)
    return ret

# def gen_verify():
#     ret = ''.join(verify)
#     print("===========================")
#     print("verify:")
#     print("---------------------------")
#     print(ret)
#     return ret


def get_typeData(nim_typename):
    return type_data['struct'][type_data['typedefs'][nim_typename]]


def get_callbackType(  funcname, argname):
    return type_data['func'][funcname]['fns'][argname]+'*'

# @macro.expr
# def get_callbackStruct(struct, funcname, param):
#     callback_struct = new( get_callbackType(funcname, param) )[0]
#     callback_struct.ClPrc = callback
#     callback_struct.ClEnv = null


if __name__ =='__main__':
    #print(gen_cdef.__dict__)
    #print(gen_cdef.__annotations__)
    source = gen_cdef()
    #gen_verify()
    from pprint import pprint
    print('---------------------------')
    print('nimheader main')
    print('---------------------------')
    print(source)
    pprint(type_data)
    #parse_nim_source()