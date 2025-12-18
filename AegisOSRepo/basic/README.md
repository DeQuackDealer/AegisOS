# Aegis OS - Basic Branch

Core foundation for all Aegis OS editions. This branch contains the base system components that form the Freemium edition.

## What's Included

### Core System
- Arch Linux base with custom kernel optimizations
- Basic Proton/Wine integration for Windows game compatibility
- PipeWire audio system
- NetworkManager with basic optimizations

### Gaming Foundation
- Steam (native Linux client)
- Lutris game manager
- Basic Proton-GE support
- DXVK shader cache
- VKD3D-Proton for DirectX 12

### Aegis Core Utilities
- `aegis-welcome` - First-run welcome wizard
- `aegis-driver-manager` - GPU driver installation
- `aegis-system-info` - System information display
- `aegis-update-manager` - Package updates
- `aegis-app-store` - Software center
- `aegis-license-manager` - License activation

### System Services
- `aegis-license-manager.service` - License validation daemon
- `aegis-system-monitor.service` - Basic system monitoring

## Building

This is raw source code. To build:

```bash
# Clone the repository
git clone https://github.com/DeQuackDealer/AegisOSRepo.git
cd AegisOSRepo
git checkout basic

# Build requires archiso and build dependencies
sudo pacman -S archiso base-devel

# Run the build script
./build.sh
```

## Structure

```
basic/
├── src/                    # Source code for Aegis utilities
│   ├── aegis_core.py       # Core library
│   ├── license_manager.py  # License management
│   ├── driver_manager.py   # GPU driver detection
│   └── proton_setup.py     # Proton/Wine configuration
├── configs/                # System configurations
│   ├── proton.conf         # Proton environment variables
│   ├── wine.conf           # Wine configuration
│   └── pipewire.conf       # Audio configuration
├── services/               # Systemd service definitions
│   ├── aegis-license.service
│   └── aegis-monitor.service
└── build.sh               # Build script
```

## License

Aegis OS Freemium - Free for personal use
