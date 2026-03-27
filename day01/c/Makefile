# LLVM バージョンをここで一括管理 (システムのデフォルトを変更しない)
CLANG   ?= clang-14
LLD_LINK ?= lld-link-14

all: hello.efi

%.o: %.c
	$(CLANG) -target x86_64-pc-win32-coff -o $@ -c $<

%.efi: %.o
	$(LLD_LINK) /subsystem:efi_application /entry:EfiMain /out:$@ $<

.PHONY: run
run: hello.efi
	../../devenv/run_qemu.sh hello.efi

clean:
	rm -f hello.efi
	rm -f disk.img
	rm -rf mnt
