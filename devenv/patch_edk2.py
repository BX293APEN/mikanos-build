#!/usr/bin/env python3
"""
EDK2 edk2-stable202208 向け GCC 14 互換パッチ

Pccts の antlr/dlg にある #ifdef __cplusplus / #else 二重定義ブロックを
実際の呼び出しシグネチャに合った型で統一する。

各配列の呼び出し元:
  fpPrint[]              : PRINT マクロ  → (p)         1引数 void*
  fpReach[], fpTraverse[]: REACH/TRAV    → (p, k, rk)  3引数 void*,int,set*
  fpTrans, fpJTrans      : TRANS マクロ  → (p)         1引数 void*
  C_Trans[], C_JTrans[]  : TRANS マクロ  → (p)         1引数 void*
  WildFunc               : ProcessArgs   → (*argv) or (*argv,*(argv+1))
"""
import sys, os, re

def read_lf(path):
    with open(path, "rb") as f:
        return f.read().replace(b"\r\n", b"\n")

def write_lf(path, data):
    with open(path, "wb") as f:
        f.write(data)

def patch(path, old, new, desc):
    data = read_lf(path)
    if new in data:
        print(f"already patched: {desc}")
        return
    if old in data:
        write_lf(path, data.replace(old, new))
        print(f"patched: {desc}")
    else:
        print(f"WARNING: pattern not found: {desc}")

def add_build_cflags(path, flags, desc):
    data = read_lf(path)
    if flags in data:
        print(f"already patched: {desc}")
        return
    patched = re.sub(
        rb'(BUILD_CFLAGS\s*=\s*[^\n]+)',
        lambda m: m.group(0) + b"  " + flags,
        data, count=1
    )
    if patched != data:
        write_lf(path, patched)
        print(f"patched: {desc}")
    else:
        print(f"WARNING: BUILD_CFLAGS not found: {desc}")

edk2_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/Programs/mikanos-build/edk2")
antlr    = os.path.join(edk2_dir, "BaseTools/Source/C/VfrCompile/Pccts/antlr")
dlg      = os.path.join(edk2_dir, "BaseTools/Source/C/VfrCompile/Pccts/dlg")

globals_c = os.path.join(antlr, "globals.c")
proto_h   = os.path.join(antlr, "proto.h")
gen_c     = os.path.join(antlr, "gen.c")
syn_h     = os.path.join(antlr, "syn.h")
antlr_mk  = os.path.join(antlr, "makefile")
dlg_main  = os.path.join(dlg,   "main.c")
dlg_mk    = os.path.join(dlg,   "makefile")

# ── globals.c ────────────────────────────────────────────────

patch(globals_c,
b"""#ifdef __cplusplus
struct _tree *(*fpTraverse[NumNodeTypes+1])(... /* Node *, int, set * */) = {
\tNULL,
\t(struct _tree *(*)(...)) tJunc,
\t(struct _tree *(*)(...)) tRuleRef,
\t(struct _tree *(*)(...)) tToken,
\t(struct _tree *(*)(...)) tAction
};
#else
Tree *(*fpTraverse[NumNodeTypes+1])() = {
\tNULL,
\ttJunc,
\ttRuleRef,
\ttToken,
\ttAction
};
#endif""",
b"""Tree *(*fpTraverse[NumNodeTypes+1])(void*, int, set*) = {
\tNULL,
\t(Tree *(*)(void*, int, set*)) tJunc,
\t(Tree *(*)(void*, int, set*)) tRuleRef,
\t(Tree *(*)(void*, int, set*)) tToken,
\t(Tree *(*)(void*, int, set*)) tAction
};""",
"globals.c: fpTraverse")

patch(globals_c,
b"""#ifdef __cplusplus
struct _set (*fpReach[NumNodeTypes+1])(... /* Node *, int, set * */) = {
\tNULL,
\t(struct _set (*)(...)) rJunc,
\t(struct _set (*)(...)) rRuleRef,
\t(struct _set (*)(...)) rToken,
\t(struct _set (*)(...)) rAction
};
#else
set (*fpReach[NumNodeTypes+1])() = {
\tNULL,
\trJunc,
\trRuleRef,
\trToken,
\trAction
};
#endif""",
b"""set (*fpReach[NumNodeTypes+1])(void*, int, set*) = {
\tNULL,
\t(set (*)(void*, int, set*)) rJunc,
\t(set (*)(void*, int, set*)) rRuleRef,
\t(set (*)(void*, int, set*)) rToken,
\t(set (*)(void*, int, set*)) rAction
};""",
"globals.c: fpReach")

patch(globals_c,
b"""#ifdef __cplusplus
void (*fpPrint[NumNodeTypes+1])(... /* Node * */) = {
\tNULL,
\t(void (*)(...)) pJunc,
\t(void (*)(...)) pRuleRef,
\t(void (*)(...)) pToken,
\t(void (*)(...)) pAction
};
#else
void (*fpPrint[NumNodeTypes+1])() = {
\tNULL,
\tpJunc,
\tpRuleRef,
\tpToken,
\tpAction
};
#endif""",
b"""void (*fpPrint[NumNodeTypes+1])(void*) = {
\tNULL,
\t(void (*)(void*)) pJunc,
\t(void (*)(void*)) pRuleRef,
\t(void (*)(void*)) pToken,
\t(void (*)(void*)) pAction
};""",
"globals.c: fpPrint")

patch(globals_c,
b"""#ifdef __cplusplus
void\t(**fpTrans)(...),\t/* array of ptrs to funcs that translate nodes */
\t \t(**fpJTrans)(...);\t/*  ... that translate junctions */
#else
void\t(**fpTrans)(),\t\t/* array of ptrs to funcs that translate nodes */
\t \t(**fpJTrans)();\t\t/*  ... that translate junctions */
#endif""",
b"""void\t(**fpTrans)(void*),\t/* array of ptrs to funcs that translate nodes */
\t \t(**fpJTrans)(void*);\t/*  ... that translate junctions */""",
"globals.c: fpTrans/fpJTrans")

# ── proto.h ──────────────────────────────────────────────────

patch(proto_h,
b"#ifdef __cplusplus\nextern void (*fpPrint[])(...); \n#else\nextern void (*fpPrint[])();\n#endif",
b"extern void (*fpPrint[])(void*);", "proto.h: fpPrint (space)")
patch(proto_h,
b"#ifdef __cplusplus\nextern void (*fpPrint[])(...);\n#else\nextern void (*fpPrint[])();\n#endif",
b"extern void (*fpPrint[])(void*);", "proto.h: fpPrint")

patch(proto_h,
b"#ifdef __cplusplus\nextern struct _set (*fpReach[])(...);\n#else\nextern struct _set (*fpReach[])();\n#endif",
b"extern set (*fpReach[])(void*, int, set*);", "proto.h: fpReach")

patch(proto_h,
b"#ifdef __cplusplus\nextern struct _tree *(*fpTraverse[])(...);\n#else\nextern struct _tree *(*fpTraverse[])();\n#endif",
b"extern Tree *(*fpTraverse[])(void*, int, set*);", "proto.h: fpTraverse")

patch(proto_h,
b"#ifdef __cplusplus\nextern void (**fpTrans)(...);\n#else\nextern void (**fpTrans)();\n#endif",
b"extern void (**fpTrans)(void*);", "proto.h: fpTrans")

patch(proto_h,
b"#ifdef __cplusplus\nextern void (**fpJTrans)(...);\n#else\nextern void (**fpJTrans)();\n#endif",
b"extern void (**fpJTrans)(void*);", "proto.h: fpJTrans")

patch(proto_h,
b"#ifdef __cplusplus\nextern void (*C_Trans[NumNodeTypes+1])(...);\n#else\nextern void (*C_Trans[])();\n#endif",
b"extern void (*C_Trans[])(void*);", "proto.h: C_Trans")

patch(proto_h,
b"#ifdef __cplusplus\nextern void (*C_JTrans[NumJuncTypes+1])(...);\n#else\nextern void (*C_JTrans[])();\n#endif",
b"extern void (*C_JTrans[])(void*);", "proto.h: C_JTrans")

# ── gen.c ────────────────────────────────────────────────────

patch(gen_c,
b"""#ifdef __cplusplus
void (*C_Trans[NumNodeTypes+1])(...) = {
\tNULL,
\tNULL,\t\t\t\t\t/* See next table.
Junctions have many types */
\t(void (*)(...)) genRuleRef,
\t(void (*)(...)) genToken,
\t(void (*)(...)) genAction
 };
#else
void (*C_Trans[NumNodeTypes+1])() = {
\tNULL,
\tNULL,\t\t\t\t\t/* See next table.
Junctions have many types */
\tgenRuleRef,
\tgenToken,
\tgenAction
 };
#endif""",
b"""void (*C_Trans[NumNodeTypes+1])(void*) = {
\tNULL,
\tNULL,\t\t\t\t\t/* See next table.
Junctions have many types */
\t(void (*)(void*)) genRuleRef,
\t(void (*)(void*)) genToken,
\t(void (*)(void*)) genAction
 };""",
"gen.c: C_Trans")

patch(gen_c,
b"""#ifdef __cplusplus
void (*C_JTrans[NumJuncTypes+1])(...) = {
\tNULL,
\t(void (*)(...)) genSubBlk,
\t(void (*)(...)) genOptBlk,
\t(void (*)(...)) genLoopBlk,
\t(void (*)(...)) genEndBlk,
\t(void (*)(...)) genRule,
\t(void (*)(...)) genJunction,
\t(void (*)(...)) genEndRule,
\t(void (*)(...)) genPlusBlk,
\t(void (*)(...)) genLoopBegin
 };
#else
void (*C_JTrans[NumJuncTypes+1])() = {
\tNULL,
\tgenSubBlk,
\tgenOptBlk,
\tgenLoopBlk,
\tgenEndBlk,
\tgenRule,
\tgenJunction,
\tgenEndRule,
\tgenPlusBlk,
\tgenLoopBegin
 };
#endif""",
b"""void (*C_JTrans[NumJuncTypes+1])(void*) = {
\tNULL,
\t(void (*)(void*)) genSubBlk,
\t(void (*)(void*)) genOptBlk,
\t(void (*)(void*)) genLoopBlk,
\t(void (*)(void*)) genEndBlk,
\t(void (*)(void*)) genRule,
\t(void (*)(void*)) genJunction,
\t(void (*)(void*)) genEndRule,
\t(void (*)(void*)) genPlusBlk,
\t(void (*)(void*)) genLoopBegin
 };""",
"gen.c: C_JTrans")

# ── syn.h ────────────────────────────────────────────────────

patch(syn_h,
b"(*(fpJTrans[((Junction *)(p))->jtype]))( p );",
b"(*(C_JTrans[((Junction *)(p))->jtype]))( p );",
"syn.h TRANS: fpJTrans -> C_JTrans")
patch(syn_h,
b"(*(fpTrans[(p)->ntype]))( p );}",
b"(*(C_Trans[(p)->ntype]))( p );}",
"syn.h TRANS: fpTrans -> C_Trans")

# ── antlr/main.c ─────────────────────────────────────────────

antlr_main = os.path.join(antlr, "main.c")

patch(antlr_main,
b"#ifdef __cplusplus\n\t\t\tvoid (*process)(...);\n#else\n\t\t\tvoid (*process)();\n#endif",
b"\t\t\tvoid (*process)(const char*, ...);",
"antlr/main.c: process field")

# ── dlg/main.c ───────────────────────────────────────────────

patch(dlg_main,
b"#ifdef __cplusplus\ntypedef void (*WildFunc)(...);\n#else\ntypedef void (*WildFunc)();\n#endif",
b"typedef void (*WildFunc)(const char*, ...);",
"dlg/main.c: WildFunc")

# ── makefiles: 残存する K&R スタイル警告を抑制 ───────────────

GCC14_FLAGS = (b"-Wno-error=incompatible-pointer-types"
               b"  -Wno-error=strict-prototypes"
               b"  -Wno-error=implicit-function-declaration")

add_build_cflags(antlr_mk, GCC14_FLAGS, "antlr/makefile: GCC14 flags")
add_build_cflags(dlg_mk,   GCC14_FLAGS, "dlg/makefile: GCC14 flags")

print("EDK2 GCC14 patch completed successfully.")
