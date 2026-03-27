#!/bin/bash -ex

# スクリプト自身の場所からプロジェクトルートを自動検出
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OSBOOK_DIR="${OSBOOK_DIR:-$(dirname "$SCRIPT_DIR")}"
EDK2DIR="${EDK2DIR:-$OSBOOK_DIR/edk2}"

if [ ! -d "$EDK2DIR" ]
then
  git clone https://github.com/tianocore/edk2.git "$EDK2DIR"
fi

cd "$EDK2DIR"

make -C "$EDK2DIR/BaseTools/Source/C"

source ./edksetup.sh

sed -i '/ACTIVE_PLATFORM/ s:= .*$:= OvmfPkg/OvmfPkgX64.dsc:' Conf/target.txt
sed -i '/TARGET_ARCH/ s:= .*$:= X64:' Conf/target.txt
sed -i '/TOOL_CHAIN_TAG/ s:= .*$:= CLANG38:' Conf/target.txt

sed -i '/CLANG38/ s/-flto//' Conf/tools_def.txt

# clang-14 / lld-14 をこのビルドだけに明示指定
export CC=clang-14
export CXX=clang++-14
export LD=ld.lld-14

build
