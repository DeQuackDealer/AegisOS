================================================================================
                    AEGIS OS ISO BUILDER - RESOURCES DIRECTORY
================================================================================

This directory contains all the resources needed to build Aegis OS ISOs offline.
The ISO Builder embeds these resources into the executable, allowing users to
create ISOs without an internet connection.

================================================================================
DIRECTORY STRUCTURE
================================================================================

resources/
├── base_system.tar.xz          # Pre-built Linux base system (~2GB compressed)
├── kernel/
│   ├── vmlinuz                 # Linux kernel image
│   └── initrd.img              # Initial ramdisk
├── isolinux/
│   ├── isolinux.bin            # ISOLINUX bootloader binary
│   ├── ldlinux.c32             # LDLINUX module
│   ├── libutil.c32             # Utility library
│   ├── libcom32.c32            # COM32 library
│   └── vesamenu.c32            # VESA menu module
├── overlays/
│   ├── overlay_freemium.tar.xz # Freemium edition customizations
│   ├── overlay_basic.tar.xz    # Basic edition customizations
│   ├── overlay_workplace.tar.xz# Workplace edition customizations
│   ├── overlay_gamer.tar.xz    # Gamer edition customizations
│   ├── overlay_ai.tar.xz       # AI Developer edition customizations
│   ├── overlay_gamer_ai.tar.xz # Gamer+AI edition customizations
│   └── overlay_server.tar.xz   # Server edition customizations
├── icons/
│   └── aegis-builder.ico       # Application icon (256x256, 128x128, 64x64, 32x32, 16x16)
└── README.txt                  # This file

================================================================================
HOW TO POPULATE THIS DIRECTORY
================================================================================

1. BASE SYSTEM (base_system.tar.xz)
-----------------------------------
   This is a minimal Ubuntu/Debian-based system with:
   - Core system utilities
   - Xfce4 desktop environment
   - Network manager
   - Basic Aegis OS branding
   
   To create:
   $ sudo debootstrap --variant=minbase jammy rootfs
   $ sudo chroot rootfs apt-get install xfce4 network-manager
   $ sudo tar -cvJf base_system.tar.xz -C rootfs .
   
   Expected size: 1.5-2.5 GB compressed

2. KERNEL FILES (kernel/)
-------------------------
   Copy from an Ubuntu/Debian installation or build custom:
   
   $ cp /boot/vmlinuz-$(uname -r) resources/kernel/vmlinuz
   $ cp /boot/initrd.img-$(uname -r) resources/kernel/initrd.img
   
   Or build a custom kernel with Aegis patches.

3. ISOLINUX FILES (isolinux/)
-----------------------------
   These come from the syslinux package:
   
   Ubuntu/Debian:
   $ apt-get install syslinux isolinux
   $ cp /usr/lib/ISOLINUX/isolinux.bin resources/isolinux/
   $ cp /usr/lib/syslinux/modules/bios/ldlinux.c32 resources/isolinux/
   $ cp /usr/lib/syslinux/modules/bios/libutil.c32 resources/isolinux/
   $ cp /usr/lib/syslinux/modules/bios/libcom32.c32 resources/isolinux/
   $ cp /usr/lib/syslinux/modules/bios/vesamenu.c32 resources/isolinux/

4. EDITION OVERLAYS (overlays/)
-------------------------------
   Each overlay is a tarball containing files to overlay on the base system.
   
   Example structure for overlay_gamer.tar.xz:
   overlay_gamer/
   ├── etc/
   │   └── aegis/
   │       ├── edition.conf
   │       └── gaming-tweaks.conf
   ├── usr/
   │   └── share/
   │       └── applications/
   │           └── steam.desktop
   └── opt/
       └── aegis-gaming/
           └── ...
   
   To create:
   $ tar -cvJf overlay_gamer.tar.xz -C overlay_gamer .

5. ICON FILE (icons/aegis-builder.ico)
--------------------------------------
   Windows ICO file with multiple sizes for proper display:
   - 256x256 (Windows Vista+)
   - 128x128
   - 64x64
   - 48x48
   - 32x32
   - 16x16
   
   Create using ImageMagick:
   $ convert aegis-logo.png -define icon:auto-resize=256,128,64,48,32,16 aegis-builder.ico

================================================================================
SIZE CONSIDERATIONS
================================================================================

The final executable size will be approximately:
- Python runtime:     ~15 MB
- Tkinter:            ~5 MB
- Cryptography:       ~8 MB (licensed builder only)
- Base resources:     ~2 GB
- Overlays:           ~500 MB (all editions)
- Kernel/boot:        ~50 MB
-----------------------------------
Total (Freemium):     ~2.1 GB (single edition only)
Total (Licensed):     ~2.6 GB (all editions)

For the freemium builder, include only:
- base_system.tar.xz
- kernel/
- isolinux/
- overlay_freemium.tar.xz

For the licensed builder, include all overlays.

================================================================================
VERIFICATION CHECKSUMS
================================================================================

After populating the resources, create checksums for verification:

$ cd resources
$ sha256sum base_system.tar.xz > checksums.sha256
$ sha256sum kernel/* >> checksums.sha256
$ sha256sum isolinux/* >> checksums.sha256
$ sha256sum overlays/* >> checksums.sha256

================================================================================
BUILD INSTRUCTIONS
================================================================================

1. Populate all required resources in this directory
2. Run the build script:
   
   $ python build-executables.py
   
3. Executables will be created in dist/:
   - AegisBuilderFreemium.exe
   - AegisBuilderLicensed.exe

4. (Optional) Sign with code signing certificate:
   
   $ python build-executables.py --sign path/to/certificate.pfx

================================================================================
NOTES
================================================================================

- Resources are embedded using PyInstaller's --add-data feature
- Compressed resources (.xz) are decompressed at runtime
- The builder works 100% offline once built
- Keep overlays as small as possible for reasonable download sizes
- Test the built executables on a clean Windows installation

For questions or issues, contact: support@aegis-os.com

================================================================================
