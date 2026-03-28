#!/usr/bin/env python3
"""
EDK2 edk2-stable202208 の GCC 14 互換パッチ。
VfrCompile/Pccts/dlg/main.c の WildFunc 型定義を修正する。

問題:
  C++ モードでは (...) を使い、C モードでは () を使う #ifdef 分岐があるが、
  GCC 14 の strict-prototypes では () が「引数不明」としてエラーになる。
  かつ WildFunc は実際に引数ありで呼ばれるため (void) にもできない。

修正:
  #ifdef 分岐ごと削除し、C/C++ 両モードで (...) を使う定義に統一する。
"""
import sys
import os

edk2_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/osbook/edk2")
path = os.path.join(edk2_dir, "BaseTools/Source/C/VfrCompile/Pccts/dlg/main.c")

with open(path, "rb") as f:
    data = f.read()

old = (
    b"#ifdef __cplusplus\r\n"
    b"typedef void (*WildFunc)(...);\r\n"
    b"#else\r\n"
    b"typedef void (*WildFunc)();\r\n"
    b"#endif"
)
new = b"typedef void (*WildFunc)(...);"

if old not in data:
    # 既にパッチ済みか、改行コードが異なる場合
    if b"typedef void (*WildFunc)(...);" in data and b"typedef void (*WildFunc)();" not in data:
        print("already patched — no change")
    else:
        print(f"ERROR: pattern not found in {path}", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)

with open(path, "wb") as f:
    f.write(data.replace(old, new))

print(f"patched: {path}")
