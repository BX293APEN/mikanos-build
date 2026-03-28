# mikanos-build

このリポジトリは uchan が開発している教育用 OS [MikanOS](https://github.com/uchan-nos/mikanos) をビルドする手順およびツールを収録しています。

ここで紹介する手順は Linux のコマンド操作にある程度慣れていることを前提に書かれています。
Linux のコマンドに不慣れな方は、まず [これだけは知っておきたい Linux コマンド](https://github.com/uchan-nos/os-from-zero/wiki/Basic-Linux-Commands) を読むことをお勧めします。

MikanOS のビルド手順は大きく次の 4 段階です。

1. ビルド環境の構築
2. MikanOS のソースコードの入手
3. ブートローダーのビルド
4. MikanOS のビルド

## ビルド環境の構築

ブートローダーおよび MikanOS 本体のビルドに必要なツールやファイルを揃えます。

### リポジトリのダウンロード

まずは Git をインストールして，mikanos-build リポジトリをダウンロードします。

```bash
sudo apt update
sudo apt install git
git clone https://github.com/BX293APEN/mikanos-build
```

### 開発ツールの導入

次に Clang，Nasm といった開発ツールや，EDK II のセットアップを行います。
`ansible_provision.yml` に必要なツールが記載されています。
Ansible を使ってセットアップを行うと楽です。

```bash
sudo apt install ansible
cd mikanos-build/devenv
sudo ansible-playbook -K -i ansible_inventory ansible_provision.yml -e "run_dir=$(pwd)"
```

セットアップが上手くいけば `iasl` というコマンドがインストールされ，`$HOME/osbook/edk2` というディレクトリが生成されているはずです。
これらがなければセットアップが失敗しています。

```bash
iasl -v
ls ../edk2
sudo chmod 777 -R ../edk2
```

### 環境変数の再読み込み(WSLのみ)

```bash
source $HOME/.profile
```

### 標準ライブラリのライセンスについて

加えて，上記の `ansible-playbook` コマンドはビルド済みの標準ライブラリを `mikanos-build/devenv/x86_64-elf` にダウンロードします。

このディレクトリに含まれるファイルは [Newlib](https://sourceware.org/newlib/)，[libc++](https://libcxx.llvm.org/)，[FreeType](https://www.freetype.org/) をビルドしたものです。
それらのライセンスはそれぞれのライブラリ固有のライセンスに従います。
MikanOS や mikanos-build リポジトリ全体のライセンスとは異なりますので注意してください。

次のファイル群は Newlib 由来です。ライセンスは `x86_64-elf/LICENSE.newlib` を参照してください。

    x86_64-elf/lib/
        libc.a
        libg.a
        libm.a
    x86_64-elf/include/
        c++/ を除くすべて

次のファイル群は libc++ 由来です。ライセンスは `x86_64-elf/LICENSE.libcxx` を参照してください。

    x86_64-elf/lib/
        libc++.a
        libc++abi.a
        libc++experimental.a
    x86_64-elf/include/c++/v1/
        すべて

次のファイル群は FreeType 由来です。ライセンスは `x86_64-elf/LICENSE.freetype` を参照してください。

    x86_64-elf/lib/
        libfreetype.a
    x86_64-elf/include/freetype2/
        すべて

## MikanOS のソースコードの入手

- 同梱されています
```bash
cd ../mikanos
```

## ブートローダーのビルド

```bash
cd ../edk2
ln -s ../mikanos/MikanLoaderPkg ./
```

ブートローダーのソースコードが正しく見えればリンク成功です。

```bash
ls MikanLoaderPkg/Main.c
```

次に，`edksetup.sh` を読み込むことで EDK II のビルドに必要な環境変数を設定します。

```bash
source edksetup.sh
```

### 設定の変更

`edksetup.sh` ファイルを読み込むと，環境変数が設定される他に `Conf/target.txt` が自動的に生成されます。
このファイルをエディタで開き，次の項目を修正します。

#### コマンド
```bash
nano Conf/target.txt
```

#### エディタ

```bash
ACTIVE_PLATFORM     = MikanLoaderPkg/MikanLoaderPkg.dsc 
TARGET              = DEBUG                             
TARGET_ARCH         = X64                               
TOOL_CHAIN_TAG      = CLANG38                           
```

設定が終わったらブートローダーをビルドします。

```bash
build
```

- 「ModuleNotFoundError: No module named 'distutils.util'」というエラーが出る場合は、`sudo apt install python3-setuptools` を実行してから再度 `build` を実行すると上手くいく可能性があります。試してみてください。
- 「Instance of library class [RegisterFilterLib] is not found」というエラーが出てビルドが失敗する場合は [RegisterFilterLib 関係のエラーで MikanLoaderPkg がビルドできません](https://github.com/uchan-nos/os-from-zero/blob/main/faq.md#registerfilterlib-%E9%96%A2%E4%BF%82%E3%81%AE%E3%82%A8%E3%83%A9%E3%83%BC%E3%81%A7-mikanloaderpkg-%E3%81%8C%E3%83%93%E3%83%AB%E3%83%89%E3%81%A7%E3%81%8D%E3%81%BE%E3%81%9B%E3%82%93) を参照してください。

Loader.efi ファイルが出力されていればビルド成功です。

```bash
ls Build/MikanLoaderX64/DEBUG_CLANG38/X64/Loader.efi
```

## MikanOS のビルド

ビルドに必要な環境変数を読み込みます。

```bash
source ../devenv/buildenv.sh
```

ビルドします。
```bash
cd ../mikanos
./build.sh
```

QEMU で起動するには `./build.sh` に `run` オプションを指定します。

```bash
./build.sh run
```
apps ディレクトリにアプリ群を入れ、フォントなどのリソースをも含めたディスクイメージを作るには APPS_DIR と RESOURCE_DIR 変数を指定します。

```bash
APPS_DIR=apps RESOURCE_DIR=resource ./build.sh run
```