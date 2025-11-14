# Makefile for Aegis OS Kernel Module
# NOTE: This is a stub for demonstration purposes
# Building actual kernel modules requires kernel headers

obj-m += aegis_lkm_stub.o

KDIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	@echo "Aegis Kernel Module Build (Stub)"
	@echo "================================="
	@echo "Note: This is a demonstration stub."
	@echo "To build actual kernel modules, you need:"
	@echo "  - Linux kernel headers"
	@echo "  - GCC compiler"
	@echo "  - make utilities"
	@echo ""
	@echo "Command would be:"
	@echo "  make -C $(KDIR) M=$(PWD) modules"
	@echo ""
	@echo "For now, displaying module source info..."
	@wc -l aegis_lkm_stub.c
	@echo "Module: aegis_lkm_stub.c ($(shell wc -l < aegis_lkm_stub.c) lines)"

clean:
	@echo "Cleaning kernel module build files..."
	rm -f *.o *.ko *.mod.* .*.cmd Module.symvers modules.order
	rm -rf .tmp_versions

.PHONY: all clean
