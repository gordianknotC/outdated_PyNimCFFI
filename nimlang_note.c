1) N_NIMCALL macro
	N_NIMCALL    (rettype, name) rettype __fastcall name

	EX:
	N_NIMCALL(NIM_BOOL,       tobool_122248) (NI x)
	N_NIMCALL(NimStringDesc*, nimIntToStr)   (NI x)
	
	above macro rewrite to following code
	NIM_BOOL       __fastcall tobool_122248 (NI x)
	NimStringDesc* __fastcall nimIntToStr   (NI x)


2) N_CDECL macro
    N_CDECL(rettype, name) rettype __cdecl name

    EX:
    N_CDECL(NimStringDesc*, cstringToString)(NCSTRING s);

    above macro translate to following code
    NimStringDesc* __cdecl cstringToString(NCSTRING s)


3) N_NIMCALL_PTR macro
	N_NIMCALL_PTR(rettype, name) rettype (__fastcall *name)
	--------------------------------------------------------
    this macro used for defining nimrod callback

    EX:
    N_NIMCALL_PTR(NIM_BOOL, ClPrc) (NI x, NI y, void* ClEnv);

    above macro translate to following code:
    NIM_BOOL (__fastcall * ClPrc) (NI x, NI y, void* ClEnv);
    --------------------------------------------------------
    as an aside
    callback function pointer in nimrod actually are struct data
    to define callback struct

    typedef struct {
    N_NIMCALL_PTR(NIM_BOOL, ClPrc) (NCSTRING msg, void* ClEnv);
    void* ClEnv;
    };

    which is equivalent to

    struct{
    NIM_BOOL (__fastcall *ClPrc) (NCSTRING msg, void* ClEnv);
    void* ClEnv;
    };

    in above case ClEnv is a NIM_NIL constant, which is ((void*)0)

    N_CLOSURE_PTR(NIM_BOOL, TMP325) (NCSTRING msg, void* ClEnv);
    NIM_BOOL TMP325 (NCSTRING msg, void* ClEnv)
	callback_struct.ClPrc = ((TMP325) (HEX3Aanonymous_125697))
	callback_struct.ClEnv = NIM_NIL
	LOC6 = callback("AnIdentifier", callback_struct)


4) N_CLOSURE_PTR
    N_CLOSURE_PTR(rettype, name) N_NIMCALL_PTR(rettype, name)






