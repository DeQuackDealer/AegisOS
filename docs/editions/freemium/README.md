# Aegis OS Freemium Edition

**The open-source base for Aegis OS - Your gateway to Linux gaming and productivity**

[![License](https://img.shields.io/badge/License-Open%20Source-green.svg)]()
[![Arch Linux](https://img.shields.io/badge/Based%20on-Arch%20Linux-1793D1.svg)]()
[![Wine](https://img.shields.io/badge/Wine-Enabled-722F37.svg)]()
[![Proton](https://img.shields.io/badge/Proton-Ready-1A9FFF.svg)]()

---

## Overview

Aegis OS Freemium is the foundational edition of Aegis OS, designed to provide a seamless transition from Windows to Linux. Built on Arch Linux with a Windows 10-inspired interface, it includes Wine and Proton for running Windows applications.

**This is an open-source preview** - Community contributions are welcome!

---

## Features

### Desktop Environment
- **XFCE4** with Windows 10-inspired theme
- Familiar taskbar, start menu, and system tray
- Dark and light theme support
- Custom icon pack

### Windows Compatibility
- **Wine 9.x** pre-configured
- **Proton** for Steam games
- Windows application launcher
- File association for .exe files

### Core Applications
- Firefox ESR (web browser)
- LibreOffice (office suite)
- VLC (media player)
- Thunar (file manager)
- GNOME Terminal

### System Tools
- NetworkManager (network configuration)
- PipeWire (modern audio)
- CUPS (printing)
- Timeshift (system backup)

---

## Package List

The Freemium edition includes the following packages:

### Base System
```
base
base-devel
linux
linux-firmware
linux-headers
```

### Desktop
```
xfce4
xfce4-goodies
lightdm
lightdm-gtk-greeter
thunar
thunar-volman
```

### Wine/Proton
```
wine
wine-mono
wine-gecko
winetricks
lib32-gnutls
lib32-libpulse
lib32-openal
lib32-mesa
```

### Applications
```
firefox
libreoffice-fresh
vlc
gimp
```

### Utilities
```
neofetch
htop
vim
nano
git
wget
curl
unzip
p7zip
```

See `build-system/archiso/packages/freemium.txt` for the complete list.

---

## Building from Source

### Prerequisites
- Arch Linux system (or VM)
- Root access
- 10GB+ free disk space
- archiso package

### Build Steps

```bash
# Clone the repository
git clone https://github.com/DeQuackDealer/AegisOSRepo.git
cd AegisOSRepo

# Checkout the freemium preview branch
git checkout preview/freemium

# Install archiso
sudo pacman -S archiso

# Build the ISO
cd build-system
sudo python build-aegis.py --edition freemium --real-build
```

The ISO will be created in `build-system/output/`.

---

## Directory Structure

```
AegisOSRepo/
├── build-system/
│   ├── archiso/
│   │   ├── packages/
│   │   │   └── freemium.txt      # Package list
│   │   ├── airootfs/             # Root filesystem overlay
│   │   │   ├── etc/              # System configuration
│   │   │   └── usr/local/bin/    # Custom scripts
│   │   ├── profiledef.sh         # ISO profile
│   │   └── pacman.conf           # Package manager config
│   ├── overlays/
│   │   └── freemium/             # Edition-specific files
│   └── build-aegis.py            # Build script
├── docs/
│   └── editions/
│       └── freemium/
│           └── README.md         # This file
└── CONTRIBUTING.md               # Contribution guidelines
```

---

## Customization

### Adding Packages

1. Edit `build-system/archiso/packages/freemium.txt`
2. Add one package per line
3. Use `pacman -Ss <name>` to find exact package names
4. Submit a Pull Request

### Adding Custom Scripts

1. Place scripts in `build-system/archiso/airootfs/usr/local/bin/`
2. Make them executable: `chmod +x script-name`
3. Document the script's purpose
4. Submit a Pull Request

### Modifying Desktop Theme

1. Theme files go in `build-system/overlays/freemium/`
2. GTK themes: `usr/share/themes/`
3. Icons: `usr/share/icons/`
4. XFCE config: `etc/skel/.config/xfce4/`

---

## Contributing

We welcome contributions! Please read [CONTRIBUTING.md](/CONTRIBUTING.md) before submitting.

### Good First Issues
- Adding useful packages
- Improving documentation
- Creating custom scripts
- Bug fixes

### How to Contribute
1. Fork the repository
2. Checkout `preview/freemium`
3. Create a feature branch
4. Make your changes
5. Submit a Pull Request

---

## Testing

### In a Virtual Machine
1. Build or download the ISO
2. Create a VM (VirtualBox, QEMU, VMware)
3. Boot from the ISO
4. Test functionality

### Checklist
- [ ] System boots to desktop
- [ ] Network connectivity works
- [ ] Wine runs Windows apps
- [ ] Audio works
- [ ] Applications launch correctly

---

## Known Issues

| Issue | Status | Workaround |
|-------|--------|------------|
| None yet | - | - |

Report bugs via [GitHub Issues](https://github.com/DeQuackDealer/AegisOSRepo/issues).

---

## Roadmap

- [ ] Improve Windows theme accuracy
- [ ] Better Wine integration
- [ ] One-click Windows app installer
- [ ] System restore points
- [ ] Auto-update mechanism

---

## License

This is an open-source preview edition. See LICENSE file for details.

---

## Links

- [Main Repository](https://github.com/DeQuackDealer/AegisOSRepo)
- [Contributing Guide](/CONTRIBUTING.md)
- [Issue Tracker](https://github.com/DeQuackDealer/AegisOSRepo/issues)
- [Discussions](https://github.com/DeQuackDealer/AegisOSRepo/discussions)

---

**Built with love by the Aegis OS community**
