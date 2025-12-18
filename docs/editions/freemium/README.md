# Aegis OS Freemium Edition

## Overview

Aegis OS Freemium is the free entry point into the Aegis ecosystem. Built on Arch Linux with a Windows 10-inspired XFCE desktop, it provides a familiar, polished experience for users transitioning from Windows or trying Linux for the first time.

## Key Features

### Desktop Experience
- **XFCE4 Desktop Environment** - Lightweight yet powerful, customized to look and feel like Windows 10
- **Windows 10-Style Theming** - Familiar taskbar, start menu, and window controls
- **Aero Snap** - Drag windows to screen edges for quick tiling
- **Translucent Taskbar** - Modern visual effects without heavy resource usage

### Pre-installed Applications
| Category | Application | Description |
|----------|-------------|-------------|
| Browser | Firefox | Privacy-focused web browser |
| Office | LibreOffice | Full office suite (Writer, Calc, Impress) |
| Media | VLC Media Player | Plays virtually any media format |
| File Manager | Thunar | Fast, lightweight file manager |
| Archive | File Roller | Compress and extract archives |

### 30-Day Premium Trial
New installations include a 30-day trial of Premium features:
- **Aegis Theme Manager** - Full customization suite
- **Aegis Wallpaper Manager** - Dynamic wallpapers and slideshow
- **Aegis Security Basics** - Firewall management and system hardening
- **Priority Updates** - Faster access to system updates

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 64-bit dual-core 2GHz | Quad-core 3GHz+ |
| RAM | 2 GB | 4 GB+ |
| Storage | 20 GB | 50 GB+ SSD |
| Graphics | Intel HD 4000 / AMD GCN 1.0 | Dedicated GPU |

## Installation

### Download
1. Download the ISO from [aegis-os.com/download](https://aegis-os.com/download)
2. Verify the SHA256 checksum:
   ```bash
   sha256sum aegis-os-freemium-3.0.0.iso
   ```

### Create Bootable USB
Using Balena Etcher (recommended):
1. Download [Balena Etcher](https://www.balena.io/etcher/)
2. Select the Aegis OS ISO
3. Select your USB drive (8GB+ recommended)
4. Click "Flash!"

Or using dd (Linux/macOS):
```bash
sudo dd if=aegis-os-freemium-3.0.0.iso of=/dev/sdX bs=4M status=progress
sync
```

### Boot and Install
1. Insert the USB and restart your computer
2. Access boot menu (usually F12, F2, or Del during startup)
3. Select the USB drive
4. Follow the graphical installer

## Included Tools

### Aegis Welcome
First-run wizard that guides new users through:
- System tour and introduction
- Driver installation
- Update configuration
- Optional software installation

### Aegis Theme Manager
Customize your desktop appearance:
- Light and Dark themes
- Accent colors
- Icon packs
- Window button layouts

### Aegis Upgrade Prompt
Shows available premium features and upgrade paths to paid editions.

### Aegis Feature Gate
Manages trial period and premium feature access.

## Package Management

Aegis OS uses `pacman`, the Arch Linux package manager:

```bash
# Update system
sudo pacman -Syu

# Install a package
sudo pacman -S package-name

# Search for packages
pacman -Ss keyword

# Remove a package
sudo pacman -Rs package-name
```

### AUR Access
The Arch User Repository (AUR) provides community packages. Install `yay` for easy AUR access:

```bash
# Install yay (included in Aegis)
sudo pacman -S yay

# Install AUR package
yay -S aur-package-name
```

## Upgrading to Paid Editions

### Available Upgrades

| Edition | Price | Best For |
|---------|-------|----------|
| Basic | $69 | Productivity and general use |
| Gamer | $49 | Gaming with Wine/Proton |
| Workplace | $49 | Business and enterprise |
| AI Developer | $89 | Machine learning and data science |
| Gamer+AI | $129 | Gaming + AI development |
| Server | $129 | Server deployment |

### Upgrade Process
1. Visit [aegis-os.com/store](https://aegis-os.com/store)
2. Purchase your preferred edition
3. Receive license key via email
4. Run `aegis-license-manager` to activate
5. System will download and install edition-specific packages

## Support

### Documentation
- [docs.aegis-os.com](https://docs.aegis-os.com)

### Community
- [Discord](https://discord.gg/aegis-os)
- [Reddit](https://reddit.com/r/aegisos)
- [GitHub Discussions](https://github.com/DeQuackDealer/AegisOSRepo/discussions)

### Bug Reports
Report issues on GitHub: [github.com/DeQuackDealer/AegisOSRepo/issues](https://github.com/DeQuackDealer/AegisOSRepo/issues)

## Contributing

We welcome contributions! See [CONTRIBUTING.md](../../../CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
git clone https://github.com/DeQuackDealer/AegisOSRepo.git
cd AegisOSRepo
git checkout preview/freemium
```

### Building from Source
```bash
cd build-system
python3 build-aegis.py --edition freemium --simulate --verbose
```

## License

Aegis OS Freemium is provided free of charge for personal and educational use.
Commercial use requires a paid license.

See [LICENSE](../../../LICENSE) for full terms.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.0.0 | 2024-12 | Initial Arch Linux-based release |
| 2.x | Legacy | Ubuntu-based versions (deprecated) |

---

**Aegis OS Freemium** - Your gateway to the Aegis ecosystem.
