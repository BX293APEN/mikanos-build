# LLVM バージョンをここで一括管理 (システムのデフォルトを変更しない)
LLD_LINK ?= lld-link-14

all: hello.efi

%.o: %.asm
	nasm -f win64 -o $@ $<

%.efi: %.o
	$(LLD_LINK) /subsystem:efi_application /entry:EfiMain /out:$@ $<

.PHONY: run
run: hello.efi
	../../devenv/run_qemu.sh hello.efi

clean:
	rm -f hello.efi
	rm -f disk.img
	rm -rf mnt
