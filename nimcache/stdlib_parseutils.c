/* Generated by Nim Compiler v0.10.2 */
/*   (c) 2014 Andreas Rumpf */
/* The generated code is subject to the original license. */
/* Compiled for: Windows, i386, gcc */
/* Command for C compiler:
   F:\Nim\dist\mingw\bin\gcc.exe -c  -w  -IF:\Nim\lib -o f:\mydocument\[programing]\python\pynimcffi\nimcache\stdlib_parseutils.o f:\mydocument\[programing]\python\pynimcffi\nimcache\stdlib_parseutils.c */
#define NIM_INTBITS 32
#include "nimbase.h"

#include <string.h>
typedef struct slice86066 slice86066;
struct  slice86066  {
NI A;
NI B;
};
static N_INLINE(slice86066, HEX2EHEX2E_92098)(NI a_92102, NI b_92104);
static N_INLINE(void, nimFrame)(TFrame* s);
N_NOINLINE(void, stackoverflow_18801)(void);
static N_INLINE(void, popFrame)(void);
extern TFrame* frameptr_16242;

static N_INLINE(void, nimFrame)(TFrame* s) {
	NI LOC1;
	LOC1 = 0;
	{
		if (!(frameptr_16242 == NIM_NIL)) goto LA4;
		LOC1 = 0;
	}
	goto LA2;
	LA4: ;
	{
		LOC1 = ((NI) ((NI16)((*frameptr_16242).calldepth + ((NI16) 1))));
	}
	LA2: ;
	(*s).calldepth = ((NI16) (LOC1));
	(*s).prev = frameptr_16242;
	frameptr_16242 = s;
	{
		if (!((*s).calldepth == ((NI16) 2000))) goto LA9;
		stackoverflow_18801();
	}
	LA9: ;
}

static N_INLINE(void, popFrame)(void) {
	frameptr_16242 = (*frameptr_16242).prev;
}

static N_INLINE(slice86066, HEX2EHEX2E_92098)(NI a_92102, NI b_92104) {
	slice86066 result;
	nimfr("..", "system.nim")
	memset((void*)(&result), 0, sizeof(result));
	nimln(226, "system.nim");
	result.A = a_92102;
	nimln(227, "system.nim");
	result.B = b_92104;
	popFrame();
	return result;
}
NIM_EXTERNC N_NOINLINE(void, stdlib_parseutilsInit)(void) {
	nimfr("parseutils", "parseutils.nim")
	popFrame();
}

NIM_EXTERNC N_NOINLINE(void, stdlib_parseutilsDatInit)(void) {
}

