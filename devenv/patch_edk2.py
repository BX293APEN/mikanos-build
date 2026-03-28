#!/usr/bin/env python3
import sys
import os

def read_lf(path):
    with open(path, "rb") as f:
        return f.read().replace(b"\r\n", b"\n")

def write_lf(path, data):
    with open(path, "wb") as f:
        f.write(data)

def replace_exact(path, old, new, desc):
    data = read_lf(path)
    if old in data:
        data = data.replace(old, new)
        write_lf(path, data)
        print(f"patched: {desc}")
    else:
        print(f"already patched: {desc}")

edk2_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/Programs/mikanos-build/edk2"
)

antlr     = os.path.join(edk2_dir, "BaseTools/Source/C/VfrCompile/Pccts/antlr")
dlg       = os.path.join(edk2_dir, "BaseTools/Source/C/VfrCompile/Pccts/dlg")
globals_c = os.path.join(antlr, "globals.c")
proto_h   = os.path.join(antlr, "proto.h")
gen_c     = os.path.join(antlr, "gen.c")
syn_h     = os.path.join(antlr, "syn.h")
dlg_main  = os.path.join(dlg,   "main.c")
antlr_mk  = os.path.join(antlr, "makefile")

# ① fpReach
replace_exact(globals_c,
    b"set (*fpReach[NumNodeTypes+1])() =",
    b"set (*fpReach[NumNodeTypes+1])(... /* Node*,int,set* */) =",
    "fpReach definition")
replace_exact(proto_h,
    b"extern struct _set (*fpReach[])();",
    b"extern struct _set (*fpReach[])(... /* Node*,int,set* */);",
    "fpReach prototype")

# ② fpTraverse
replace_exact(globals_c,
    b"Tree *(*fpTraverse[NumNodeTypes+1])() =",
    b"Tree *(*fpTraverse[NumNodeTypes+1])(... /* Node*,int,set* */) =",
    "fpTraverse definition")
replace_exact(proto_h,
    b"extern struct _tree *(*fpTraverse[])();",
    b"extern struct _tree *(*fpTraverse[])(... /* Node*,int,set* */);",
    "fpTraverse prototype")

# ③ fpTrans / fpJTrans
replace_exact(globals_c,
    b"#else\nvoid\t(**fpTrans)(),\t\t/* array of ptrs to funcs that translate nodes */\n\t \t(**fpJTrans)();\t\t/*  ... that translate junctions */",
    b"#else\nvoid\t(**fpTrans)(...),\t/* array of ptrs to funcs that translate nodes */\n\t \t(**fpJTrans)(...);\t/*  ... that translate junctions */",
    "fpTrans/fpJTrans #else definition")
replace_exact(proto_h,
    b"extern void (**fpTrans)();",
    b"extern void (**fpTrans)(...);",
    "fpTrans #else extern prototype")
replace_exact(proto_h,
    b"extern void (**fpJTrans)();",
    b"extern void (**fpJTrans)(...);",
    "fpJTrans #else extern prototype")

# ④ C_Trans / C_JTrans 宣言
replace_exact(gen_c,
    b"void (*C_Trans[NumNodeTypes+1])() = {",
    b"void (*C_Trans[NumNodeTypes+1])(... ) = {",
    "C_Trans C-block definition")
replace_exact(gen_c,
    b"void (*C_JTrans[NumJuncTypes+1])() = {",
    b"void (*C_JTrans[NumJuncTypes+1])(... ) = {",
    "C_JTrans C-block definition")
replace_exact(proto_h,
    b"extern void (*C_Trans[])();",
    b"extern void (*C_Trans[])(...);",
    "C_Trans #else extern prototype")
replace_exact(proto_h,
    b"extern void (*C_JTrans[])();",
    b"extern void (*C_JTrans[])(...);",
    "C_JTrans #else extern prototype")

# ⑤ syn.h TRANS マクロ
replace_exact(syn_h,
    b"(*(fpJTrans[((Junction *)(p))->jtype]))( p );",
    b"(*(C_JTrans[((Junction *)(p))->jtype]))( p );",
    "syn.h TRANS macro: fpJTrans -> C_JTrans")
replace_exact(syn_h,
    b"(*(fpTrans[(p)->ntype]))( p );}",
    b"(*(C_Trans[(p)->ntype]))( p );}",
    "syn.h TRANS macro: fpTrans -> C_Trans")

# ⑥ WildFunc: (...) は ISO C では「名前付き引数なし」でエラーになるため元の () のまま残し、
#    makefile 側で -Wno-strict-prototypes を追加して対処する
#    (すでに (...) にパッチ済みの場合は () に戻す)
replace_exact(dlg_main,
    b"typedef void (*WildFunc)(...);",
    b"typedef void (*WildFunc)();",
    "WildFunc typedef: revert (...) -> () (suppress via makefile instead)")
# 未パッチの場合は何もしない（元から () なので問題なし）

import re

# ⑦ GCC14 対策: antlr の makefile に -Wno-incompatible-pointer-types を追加
# gen.c の初期化子に具体的な型の関数ポインタを渡しているため警告がエラーになる
antlr_mk_data = read_lf(antlr_mk)
FLAG_INCOMPAT = b"-Wno-incompatible-pointer-types"
if FLAG_INCOMPAT in antlr_mk_data:
    print("already patched: antlr makefile CFLAGS (-Wno-incompatible-pointer-types)")
else:
    patched = re.sub(
        rb'(CFLAGS\s*=\s*[^\n]+)',
        lambda m: m.group(0) + b"  " + FLAG_INCOMPAT,
        antlr_mk_data,
        count=1
    )
    if patched != antlr_mk_data:
        write_lf(antlr_mk, patched)
        print("patched: antlr makefile CFLAGS add -Wno-incompatible-pointer-types")
    else:
        print("WARNING: could not find CFLAGS line in antlr makefile")

# ⑧ GCC14 対策: dlg の makefile に -Wno-strict-prototypes -Wno-incompatible-pointer-types を追加
# main.c の WildFunc など古い K&R スタイルのプロトタイプが strict-prototypes エラーになる
dlg_mk = os.path.join(dlg, "makefile")
dlg_mk_data = read_lf(dlg_mk)
FLAG_STRICT = b"-Wno-strict-prototypes"
if FLAG_STRICT in dlg_mk_data:
    print("already patched: dlg makefile CFLAGS (-Wno-strict-prototypes)")
else:
    flags_to_add = b"  " + FLAG_STRICT + b"  " + FLAG_INCOMPAT
    patched = re.sub(
        rb'(CFLAGS\s*=\s*[^\n]+)',
        lambda m: m.group(0) + flags_to_add,
        dlg_mk_data,
        count=1
    )
    if patched != dlg_mk_data:
        write_lf(dlg_mk, patched)
        print("patched: dlg makefile CFLAGS add -Wno-strict-prototypes -Wno-incompatible-pointer-types")
    else:
        print("WARNING: could not find CFLAGS line in dlg makefile")

print("EDK2 GCC14 patch completed successfully.")
