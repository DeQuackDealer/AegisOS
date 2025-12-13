# Aegis OS Gamer Edition

**The ultimate Linux gaming experience - SteamOS-inspired, community-driven**

[![License](https://img.shields.io/badge/License-Open%20Source-green.svg)]()
[![Arch Linux](https://img.shields.io/badge/Based%20on-Arch%20Linux-1793D1.svg)]()
[![Steam](https://img.shields.io/badge/Steam-Ready-000000.svg)]()
[![Proton](https://img.shields.io/badge/Proton--GE-Included-1A9FFF.svg)]()

---

## Overview

Aegis OS Gamer Edition is built for PC gamers who want the best Linux gaming experience. Inspired by SteamOS, it comes pre-configured with Steam, Lutris, Heroic Games Launcher, and all the tools you need to run Windows games at maximum performance.

**This is an open-source preview** - Help us build the ultimate gaming distro!

---

## Features

### Game Launchers
- **Steam** with Big Picture mode
- **Lutris** for GOG, Epic, Origin, Ubisoft
- **Heroic Games Launcher** for Epic/GOG
- **Bottles** for Windows apps and games

### Proton & Wine
- **Proton-GE** (latest community build)
- **Wine-GE** for non-Steam games
- **DXVK** for DirectX 9/10/11
- **VKD3D-Proton** for DirectX 12
- **Winetricks** for dependencies

### Performance Tools
- **MangoHUD** - FPS counter and stats overlay
- **GameMode** - Automatic CPU/GPU optimization
- **GameScope** - SteamOS compositor
- **CoreCtrl** - GPU overclocking (AMD)
- **GreenWithEnvy** - GPU monitoring (NVIDIA)

### Controller Support
- Xbox controllers (wired & wireless)
- PlayStation DualShock/DualSense
- Nintendo Switch Pro Controller
- Steam Controller
- Generic gamepads

### Desktop
- **XFCE4** with gaming-optimized theme
- Low latency audio (PipeWire)
- Quick game launch shortcuts
- System tray with performance monitor

---

## Package List

### Gaming Platforms
```
steam
steam-native-runtime
lutris
heroic-games-launcher-bin (AUR)
bottles
```

### Proton/Wine
```
wine-staging
wine-mono
wine-gecko
winetricks
proton-ge-custom-bin (AUR)
dxvk-bin
vkd3d-proton-bin
```

### Performance
```
gamemode
lib32-gamemode
mangohud
lib32-mangohud
gamescope
corectrl
```

### Graphics Drivers
```
# NVIDIA
nvidia
nvidia-utils
lib32-nvidia-utils
nvidia-settings

# AMD
mesa
lib32-mesa
vulkan-radeon
lib32-vulkan-radeon
```

### Controllers
```
game-devices-udev
xpadneo-dkms (AUR)
dualsensectl (AUR)
```

### Utilities
```
protontricks
protonup-qt
steamtinkerlaunch
goverlay
```

See `build-system/archiso/packages/gamer.txt` for the complete list.

---

## Building from Source

### Prerequisites
- Arch Linux system (or VM)
- Root access
- 15GB+ free disk space
- archiso package

### Build Steps

```bash
# Clone the repository
git clone https://github.com/DeQuackDealer/AegisOSRepo.git
cd AegisOSRepo

# Checkout the gamer preview branch
git checkout preview/gamer

# Install archiso
sudo pacman -S archiso

# Build the ISO
cd build-system
sudo python build-aegis.py --edition gamer --real-build
```

---

## Directory Structure

```
AegisOSRepo/
├── build-system/
│   ├── archiso/
│   │   ├── packages/
│   │   │   └── gamer.txt         # Gaming package list
│   │   └── airootfs/
│   │       └── etc/
│   │           └── gamemode.ini  # GameMode config
│   ├── overlays/
│   │   └── gamer/
│   │       ├── mangohud.conf     # MangoHUD preset
│   │       └── steam-tweaks/     # Steam optimizations
│   └── build-aegis.py
├── docs/
│   └── editions/
│       └── gamer/
│           └── README.md         # This file
└── CONTRIBUTING.md
```

---

## Performance Tuning

### MangoHUD Configuration

Default overlay shows:
- FPS (current, average, 1% low)
- Frame time graph
- CPU/GPU usage
- VRAM usage
- Temperature

Config location: `~/.config/MangoHud/MangoHud.conf`

```ini
fps
frame_timing
cpu_stats
gpu_stats
vram
gpu_temp
cpu_temp
```

### GameMode Settings

Enabled automatically when launching games. Optimizations:
- CPU governor set to performance
- I/O priority boost
- GPU power profile optimization
- Compositor bypass

### Proton-GE vs Standard Proton

| Feature | Proton | Proton-GE |
|---------|--------|-----------|
| Official Valve | Yes | No |
| Bleeding edge | No | Yes |
| Media codecs | Limited | Full |
| Game-specific fixes | Delayed | Fast |

We recommend **Proton-GE** for best compatibility.

---

## Controller Setup

### Xbox Controllers
Works out of the box with `xpadneo` driver.

### PlayStation Controllers
```bash
# Connect via Bluetooth or USB
# Configure with:
dualsensectl
```

### Steam Controller
Requires Steam running in the background.

---

## Customization

### Adding Game Launchers

1. Edit `build-system/archiso/packages/gamer.txt`
2. Add the package name
3. Test in a VM first
4. Submit a Pull Request

### Custom MangoHUD Presets

1. Create preset in `build-system/overlays/gamer/`
2. Name it `mangohud-custom.conf`
3. Document what it shows
4. Submit a Pull Request

### Game-Specific Tweaks

1. Add scripts to `build-system/archiso/airootfs/usr/local/bin/`
2. Prefix with `aegis-game-`
3. Document usage
4. Submit a Pull Request

---

## Contributing

We need your help! See [CONTRIBUTING.md](/CONTRIBUTING.md).

### Priority Contributions
- Game compatibility fixes
- Performance optimizations
- Controller support improvements
- Documentation for game setup

### Testing Games

Help us test games! Report compatibility:
1. Game name and launcher used
2. Works / Doesn't work / Partial
3. Any tweaks needed
4. Performance notes

---

## Game Compatibility

| Game | Status | Notes |
|------|--------|-------|
| Help us fill this! | - | Submit reports |

---

## Known Issues

| Issue | Status | Workaround |
|-------|--------|------------|
| None yet | - | - |

---

## Roadmap

- [ ] Pre-configured shader cache
- [ ] One-click Proton-GE installer
- [ ] Game-specific optimization profiles
- [ ] Recording/streaming integration
- [ ] RGB lighting support

---

## FAQ

**Q: Why not just use SteamOS?**
A: Aegis OS Gamer supports more launchers and is more customizable.

**Q: Can I use this as my main OS?**
A: Yes! It's a full Arch Linux system.

**Q: How do I update Proton-GE?**
A: Use ProtonUp-Qt in the applications menu.

---

## Links

- [ProtonDB](https://www.protondb.com/) - Game compatibility database
- [Main Repository](https://github.com/DeQuackDealer/AegisOSRepo)
- [Contributing Guide](/CONTRIBUTING.md)
- [Issue Tracker](https://github.com/DeQuackDealer/AegisOSRepo/issues)

---

**Game on with Aegis OS!**
