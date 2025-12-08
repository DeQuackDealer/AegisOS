# Aegis OS ISO Builder

## Overview

This system builds real, bootable Aegis OS ISOs using GitHub Actions. The ISOs include:
- Ubuntu 24.04 LTS base
- XFCE desktop environment
- All Aegis custom tools
- Edition-specific software packages

## How to Build ISOs

### Using GitHub Actions (Recommended)

1. Push this repository to GitHub
2. Go to **Actions** tab
3. Click **Build Aegis OS ISOs** workflow
4. Click **Run workflow**
5. Select edition (or "all" for all editions)
6. Wait ~30-60 minutes for build to complete
7. Download ISO from **Artifacts** section

### Available Editions

| Edition | Description | Size (approx) |
|---------|-------------|---------------|
| freemium | Free edition with basic features | ~1.5 GB |
| basic | Essential productivity tools | ~2.0 GB |
| gamer | Optimized for gaming (Steam, Lutris) | ~2.5 GB |
| workplace | Enterprise productivity | ~2.2 GB |
| ai_developer | AI/ML development (VS Code, Python) | ~2.5 GB |
| gamer_ai | Gaming + AI features | ~3.0 GB |
| server | Server/infrastructure (Docker, Nginx) | ~1.8 GB |

## What Each Edition Includes

### All Editions (Base)
- Ubuntu 24.04 LTS kernel
- XFCE 4 desktop
- Firefox browser
- Network Manager
- Live boot support (runs from USB)

### Freemium
- Basic XFCE desktop
- Firefox
- File manager

### Basic
- LibreOffice
- VLC media player
- GIMP image editor
- ClamAV antivirus
- Backup tools

### Gamer
- Steam
- Lutris
- Wine/Proton
- GameMode
- MangoHud (FPS overlay)

### Workplace
- LibreOffice
- Thunderbird email
- Remmina remote desktop
- KeePassXC password manager

### AI Developer
- VS Code
- Python 3 + pip + venv
- Node.js
- Git
- Build tools

### Server
- SSH server
- Nginx
- Docker
- Fail2ban
- UFW firewall

## After Building

1. Download the ISO from GitHub Actions artifacts
2. Use [Balena Etcher](https://etcher.balena.io/) to flash to USB
3. Boot from USB to try Aegis OS
4. Default login: `aegis` / `aegis`

## File Structure

```
.github/workflows/build-iso.yml  - GitHub Actions workflow
build-system/aegis-tools/        - Aegis custom tools
build-system/iso-builder/        - This documentation
```

## Customization

Edit `.github/workflows/build-iso.yml` to:
- Change base packages
- Add/remove software
- Modify boot options
- Change branding
