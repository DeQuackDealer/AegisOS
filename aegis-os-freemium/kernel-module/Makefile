
# Aegis OS Kernel Module Makefile
# Builds the aegis_lkm.ko kernel module

obj-m += aegis_lkm.o

# Kernel build directory (use running kernel if not specified)
KERNEL_SOURCE ?= /lib/modules/$(shell uname -r)/build

# Default target
all:
	@echo "Building Aegis OS Kernel Module..."
	$(MAKE) -C $(KERNEL_SOURCE) M=$(PWD) modules
	@echo "✅ Kernel module built successfully"

# Install module
install: all
	@echo "Installing Aegis OS Kernel Module..."
	sudo $(MAKE) -C $(KERNEL_SOURCE) M=$(PWD) modules_install
	sudo depmod -a
	@echo "✅ Kernel module installed"

# Load module
load: install
	@echo "Loading Aegis OS Kernel Module..."
	sudo modprobe aegis_lkm
	@echo "✅ Kernel module loaded"
	@echo "SysFS interface: /sys/kernel/aegis/"

# Unload module
unload:
	@echo "Unloading Aegis OS Kernel Module..."
	-sudo modprobe -r aegis_lkm
	@echo "✅ Kernel module unloaded"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	$(MAKE) -C $(KERNEL_SOURCE) M=$(PWD) clean
	rm -f Module.symvers modules.order
	@echo "✅ Clean complete"

# Show module info
info:
	@echo "Aegis OS Kernel Module Information:"
	@echo "====================================="
	@modinfo aegis_lkm.ko 2>/dev/null || echo "Module not built yet"

# Test module functionality
test: load
	@echo "Testing Aegis OS Kernel Module..."
	@echo "====================================="
	@echo "Tier: $$(cat /sys/kernel/aegis/tier 2>/dev/null || echo 'N/A')"
	@echo "Version: $$(cat /sys/kernel/aegis/version 2>/dev/null || echo 'N/A')"
	@echo "Status: $$(cat /sys/kernel/aegis/status 2>/dev/null || echo 'N/A')"
	@echo ""
	@echo "Enabled Features:"
	@cat /sys/kernel/aegis/features 2>/dev/null || echo "N/A"
	@echo ""
	@echo "Disabled Features:"
	@cat /sys/kernel/aegis/disabled_features 2>/dev/null || echo "N/A"

.PHONY: all install load unload clean info test
