# Aegis OS Build System

## Overview
This directory contains the build system for creating **real, bootable** Aegis OS ISO images using `archiso` (the official Arch Linux ISO creation tool).

## Quick Start - Building Real ISOs

### Option 1: GitHub Actions (Recommended)

The repository includes a GitHub Actions workflow that builds real, bootable ISOs automatically:

1. **Push to GitHub** - Push your changes to the repository
2. **Run the workflow**:
   - Go to Actions → "Build Aegis OS ISOs"
   - Click "Run workflow"
   - Select the edition (freemium, basic, gamer, or all)
3. **Download the ISO** from the workflow artifacts (~30-60 min build time)

The workflow runs in an Arch Linux container with `mkarchiso` to create genuine bootable ISOs.

### Option 2: Local Build (Arch Linux Required)

To build locally, you need an Arch Linux system:

```bash
# Install archiso
sudo pacman -S archiso

# Navigate to build directory
cd build-system

# Build an edition (requires root)
sudo ./build.sh gamer

# Or build all core editions
sudo ./build-all.sh
```

### Prerequisites for Local Build
- Arch Linux or Arch-based system (Manjaro, EndeavourOS)
- `archiso` package installed
- Root privileges
- 20-30GB free disk space
- 4GB+ RAM

## Available Editions

| Edition | Price | Description |
|---------|-------|-------------|
| `freemium` | FREE | Base desktop with XFCE |
| `basic` | $19 | Productivity tools + backup |
| `gamer` | $49 | Steam, Wine, 11 gaming services |
| `workplace` | $69 | Enterprise collaboration tools |
| `aidev` | $89 | ML/AI frameworks + CUDA |
| `server` | $129 | Enterprise stack + monitoring |

## Build Process

The build system follows these steps:

1. **Profile Setup**
   - Copies official archiso releng profile
   - Applies Aegis branding and configuration

2. **Package Installation**
   - Installs base Arch Linux packages
   - Adds edition-specific packages
   - Enables Chaotic-AUR for additional packages

3. **Overlay Application**
   - Copies Aegis tools to `/usr/local/bin/`
   - Configures systemd services
   - Sets up desktop environment

4. **ISO Generation**
   - Creates squashfs filesystem
   - Configures UEFI and BIOS bootloaders
   - Generates bootable ISO with checksums

## Directory Structure

```
build-system/
├── archiso/
│   ├── profiles/
│   │   └── releng/           # Base archiso profile
│   │       ├── profiledef.sh # ISO configuration
│   │       ├── packages.x86_64
│   │       ├── pacman.conf
│   │       ├── airootfs/     # Live system files
│   │       ├── syslinux/     # BIOS boot config
│   │       ├── grub/         # UEFI boot config
│   │       └── efiboot/      # EFI boot entries
│   └── packages/             # Edition-specific packages
├── overlays/                 # Edition-specific files
│   ├── common/               # Shared across all editions
│   ├── freemium/
│   ├── basic/
│   ├── gamer/                # Game Library, optimization services
│   └── ...
├── build.sh                  # Main build script (uses mkarchiso)
├── build-all.sh              # Build all editions
└── output/                   # Generated ISOs
```

## Testing the ISO

After building, test your ISO:

### VirtualBox/VMware
1. Create VM with 4GB+ RAM
2. **Enable EFI** in VM settings (important!)
3. Boot from the ISO

### QEMU
```bash
qemu-system-x86_64 -enable-kvm -m 4G -bios /usr/share/ovmf/OVMF.fd \
  -cdrom output/aegis-gamer-2.0.0.iso
```

### Real Hardware
1. Create bootable USB with Ventoy, Rufus, or `dd`:
   ```bash
   sudo dd if=output/aegis-gamer-2.0.0.iso of=/dev/sdX bs=4M status=progress
   ```
2. Boot from USB

## Verification

Each ISO includes checksums:
```bash
sha256sum -c aegis-gamer-2.0.0.sha256
```

## Troubleshooting

**"No bootable medium" error:**
- Enable EFI in VM settings
- The ISO supports both UEFI and BIOS boot

**Build fails on non-Arch system:**
- `mkarchiso` only works on Arch Linux
- Use the GitHub Actions workflow instead

**Package not found:**
- Workflow enables Chaotic-AUR for extra packages
- Check if package exists in Arch repos

**Build takes too long:**
- First build downloads packages (~2GB)
- Subsequent builds use cached packages
