# Aegis OS Freemium Edition - Build Guide

## Building the ISO for Your Virtual Machine

### Prerequisites
- Linux machine (Ubuntu/Debian/Fedora recommended)
- 8GB RAM minimum, 16GB+ recommended
- 20GB+ free disk space
- Build tools installed

### Install Build Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y build-essential wget cpio unzip rsync bc libncurses5-dev
```

**Fedora/RHEL:**
```bash
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y wget cpio unzip rsync bc ncurses-devel
```

### Build Steps

```bash
# 1. Navigate to the build directory
cd aegis-os-freemium

# 2. Make the build script executable
chmod +x build.sh post-build.sh

# 3. Start the build (takes 1-2 hours)
./build.sh

# The build will:
# - Download Buildroot 2023.08
# - Configure with XFCE 4.18, Wine, gaming optimizations
# - Compile Linux kernel 6.6.7
# - Create bootable ISO
```

### Output Files

After successful build, you'll find these files in `aegis-os-freemium/output/`:

- **aegis-os-freemium.iso** - Bootable ISO (use this!)
- **aegis-os-freemium.ext4** - Root filesystem
- **aegis-kernel** - Compiled kernel
- **checksums.txt** - SHA256 checksums for verification

### Create Bootable Media

**For USB Drive (Linux):**
```bash
sudo dd if=output/aegis-os-freemium.iso of=/dev/sdX bs=4M status=progress
# Replace /dev/sdX with your USB device (use lsblk to find it)
sync
```

**Using balenaEtcher (Cross-platform):**
1. Download and install balenaEtcher
2. Select the ISO file
3. Select your USB drive
4. Click Flash

### VirtualBox Installation

1. **Create VM:**
   - Name: Aegis OS
   - Type: Linux
   - Version: Other Linux (64-bit)
   - Memory: 4GB+ RAM
   - Storage: 20GB+ virtual disk

2. **Configure:**
   - Under Display → Enable 3D Acceleration
   - Under Storage → Mount aegis-os-freemium.iso as CD/DVD

3. **Boot:**
   - Start the VM
   - It will auto-login as "aegis" user (no password)
   - XFCE desktop will start automatically

### VMware Installation

1. **Create VM:**
   - Linux x86_64
   - Allocate 4GB RAM, 20GB disk
   - Select "Ubuntu 64-bit" as guest OS type

2. **Configure:**
   - Under Video → Enable 3D graphics

3. **Mount ISO:**
   - VM Settings → CD/DVD
   - Select aegis-os-freemium.iso

4. **Boot and enjoy!**

### First Boot

- **Auto-login:** Username is "aegis" (no password required)
- **XFCE Desktop:** Full Windows 10-like interface
- **Gaming Ready:** Wine/Proton pre-configured for Steam
- **Optimization:** Gaming optimizations active by default

### Troubleshooting

**Build fails with "command not found":**
- Ensure all build dependencies are installed
- Run: `sudo apt-get install build-essential wget cpio unzip rsync bc libncurses5-dev`

**Build is slow:**
- Normal! Buildroot compilation takes 1-2 hours
- Monitor progress in the output - it's working

**ISO won't boot:**
- Verify ISO wasn't corrupted: `sha256sum -c checksums.txt`
- Try recreating bootable media
- Ensure VM has 3D acceleration enabled

**XFCE desktop doesn't start:**
- Check system logs: `journalctl -xe`
- Verify 3D graphics support in your VM

### Performance Tips

- Allocate 4GB+ RAM to VM for smooth operation
- Enable 3D acceleration in host GPU settings
- Use SSD storage for build and VM disks
- Consider 8+ CPU cores for faster build time

### What's Included

✅ Linux 6.6.7 kernel
✅ XFCE 4.18 desktop environment
✅ Wine 8.21 + Proton support
✅ Vulkan/OpenGL graphics acceleration
✅ PulseAudio sound system
✅ NetworkManager for easy networking
✅ Gaming optimizations active by default
✅ 10 Aegis system utilities
✅ 4 system monitoring services
✅ Completely free - no license required!

### Support

- **Documentation:** See README.md files in each folder
- **Community:** Visit https://aegis-os.com
- **Issues:** Check system logs with `journalctl`

Happy gaming! 🎮
