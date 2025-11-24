# Aegis OS Build System

## Overview
This directory contains the build scripts and configuration files for creating Aegis OS ISO images.

## Quick Build Instructions

### Prerequisites
- Ubuntu 20.04+ or Debian 11+
- 30-50GB free disk space
- 8-16GB RAM
- 2-4 hours build time

### Install Dependencies
```bash
sudo apt update
sudo apt install -y build-essential git wget cpio rsync bc bison flex
sudo apt install -y libssl-dev libncurses5-dev libelf-dev python3 python3-pip
sudo apt install -y genisoimage isolinux xorriso squashfs-tools
```

### Building an ISO

1. **Run the build script:**
```bash
cd build-system
chmod +x build-aegis.py
python3 build-aegis.py --edition=freemium
```

2. **Available editions:**
- `freemium` - Basic Linux with XFCE (FREE)
- `basic` - 500+ professional applications ($69)
- `gamer` - Gaming optimizations + Wine/Proton ($89)
- `ai` - ML/AI frameworks + CUDA support ($109)
- `server` - Enterprise stack + monitoring (Contact)

3. **Build output:**
- ISO files will be created in `build-system/output/`
- Logs available in `build-system/logs/`

## Build Process

The build system follows these steps:

1. **Base System Creation**
   - Downloads Ubuntu base system
   - Installs kernel and drivers
   - Configures boot loader

2. **Package Installation**
   - Installs edition-specific packages
   - Configures desktop environment
   - Sets up default applications

3. **Customization**
   - Applies Aegis branding
   - Configures system settings
   - Installs license manager

4. **ISO Generation**
   - Creates squashfs filesystem
   - Generates bootable ISO
   - Adds UEFI/BIOS support

## Directory Structure

```
build-system/
├── build-aegis.py        # Main build script
├── configs/              # Edition configurations
│   ├── freemium.json
│   ├── basic.json
│   ├── gamer.json
│   ├── ai.json
│   └── server.json
├── packages/             # Package lists per edition
├── scripts/              # Build helper scripts
├── overlays/            # Custom files/configs
└── output/              # Generated ISOs
```

## Configuration Files

Each edition has a JSON configuration file defining:
- Package lists
- System settings
- Desktop environment
- Default applications
- License requirements

## Testing

Test ISOs in VirtualBox:
```bash
# Create VM with 4GB RAM, 20GB disk
# Mount ISO and boot
# Test installation process
```

## Troubleshooting

**Out of space error:**
- Ensure 50GB free space in /tmp and build directory

**Package not found:**
- Update package lists: `sudo apt update`

**Build fails:**
- Check logs in `build-system/logs/`
- Ensure all dependencies installed

## License

Build system is for demonstration purposes only.
All trademarks belong to respective owners.

**Disclaimer:** Anything represented may not be true. Use at your own risk.