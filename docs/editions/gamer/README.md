# Aegis OS Gamer Edition

## Overview

Aegis OS Gamer Edition is the ultimate Linux gaming platform. Inspired by SteamOS and optimized for performance, it delivers a console-like gaming experience with the flexibility of a full desktop operating system. Built on Arch Linux with the linux-zen kernel, it's designed for gamers who want maximum performance without the complexity.

## Key Features

### Gaming-Optimized Kernel
- **Linux-zen Kernel** - Patched for lower latency and better gaming performance
- **Custom I/O Scheduler** - Optimized for game loading times
- **CPU Governor Tweaks** - Automatic performance scaling for games

### Wine & Proton Excellence
- **Wine Staging** - Latest Wine with all gaming patches
- **Proton GE** - Community Proton builds with extra game fixes
- **Aegis Wine Optimizer** - One-click Wine prefix management
- **DXVK/VKD3D** - DirectX 9/10/11/12 to Vulkan translation

### Game Launchers
| Launcher | Description |
|----------|-------------|
| Steam | Native Linux client with Proton |
| Lutris | Universal game launcher |
| Heroic | Epic Games & GOG launcher |
| Bottles | Wine prefix manager |

### Performance Tools
- **MangoHud** - In-game performance overlay (FPS, CPU, GPU, RAM)
- **GameMode** - Auto-apply performance optimizations when gaming
- **Aegis Performance Tuner** - System-wide performance profiles
- **Aegis Upscaler** - AI upscaling for better visuals at higher FPS

### Streaming & Recording
- **Aegis Stream Studio** - OBS-based streaming with one-click setup
- **Aegis Stream Deck** - Virtual stream deck for hotkeys
- **Hardware Encoding** - NVENC/VAAPI support for minimal CPU impact

## System Requirements

| Component | Minimum | Recommended | Best Experience |
|-----------|---------|-------------|-----------------|
| CPU | Quad-core 3GHz | 6-core 3.5GHz+ | 8-core 4GHz+ |
| RAM | 8 GB | 16 GB | 32 GB |
| GPU | GTX 1050 / RX 560 | RTX 3060 / RX 6600 | RTX 4070+ / RX 7800+ |
| Storage | 50 GB | 256 GB NVMe | 1TB+ NVMe |
| Display | 1080p 60Hz | 1440p 144Hz | 4K 120Hz+ |

### Supported Graphics Cards
- **NVIDIA**: GeForce GTX 900 series and newer (proprietary drivers included)
- **AMD**: GCN 1.0 and newer (open-source Mesa drivers)
- **Intel**: Arc GPUs and integrated graphics (Xe, UHD)

## Installation

### Download
1. Download from [aegis-os.com/download/gamer](https://aegis-os.com/download/gamer)
2. Verify checksum:
   ```bash
   sha256sum aegis-os-gamer-3.0.0.iso
   ```

### Create Bootable USB
```bash
# Linux/macOS
sudo dd if=aegis-os-gamer-3.0.0.iso of=/dev/sdX bs=4M status=progress

# Windows - Use Balena Etcher or Rufus (DD mode)
```

### Installation Options
- **Full Install** - Replaces existing OS
- **Dual Boot** - Install alongside Windows
- **Steam Deck Mode** - Console-like boot straight to Steam Big Picture

## Included Aegis Tools

### Gaming Tools

#### Aegis Game Center (`aegis-game-center`)
Central hub for all your games across platforms:
- Unified library view
- Per-game settings
- Playtime tracking
- Achievement display

#### Aegis Game Launcher (`aegis-game-launcher`)
Smart game launcher with:
- Pre-launch optimization
- Upscaler injection
- Post-game performance reports
- Wine prefix auto-selection

#### Aegis Performance Tuner (`aegis-performance-tuner`)
System performance profiles:
- **Gaming Mode**: Max performance, disable power saving
- **Balanced**: Good performance with power efficiency
- **Quiet**: Low fan noise, reduced performance
- **Custom**: Create your own profiles

#### Aegis Wine Optimizer (`aegis-wine-optimizer`)
Wine management made easy:
- One-click prefix creation
- Dependency installer (DirectX, .NET, VCRedist)
- DXVK/VKD3D configuration
- Game-specific tweaks database

#### Aegis Upscaler (`aegis-upscaler`)
AI-powered upscaling:
- **ANU Neural**: Custom Aegis neural network
- **FSR**: AMD FidelityFX Super Resolution
- **DLSS**: NVIDIA Deep Learning (RTX cards)
- Per-game profiles

#### Aegis Render Orchestrator (`aegis-render-orchestrator`)
Multi-GPU and hybrid graphics management:
- NVIDIA Optimus support
- AMD Switchable Graphics
- External GPU (eGPU) support
- Per-game GPU assignment

### Streaming Tools

#### Aegis Stream Studio (`aegis-stream-studio`)
Professional streaming setup:
- Pre-configured OBS scenes
- Audio routing with PipeWire
- Webcam and green screen setup
- Stream alerts integration

#### Aegis Stream Deck (`aegis-stream-deck`)
Virtual stream deck:
- Customizable button grid
- Scene switching
- Sound effects
- Chat integration

### System Tools

#### Aegis Wallpaper Engine (`aegis-wallpaper-engine`)
Animated desktop wallpapers:
- Video wallpapers
- Interactive wallpapers
- Steam Workshop support (via Wallpaper Engine)
- Low resource usage

#### Aegis Audio Router (`aegis-audio-router`)
Advanced audio management:
- Per-application volume
- Game/voice chat separation
- Virtual audio cables
- Low-latency audio

## Performance Optimization

### Automatic Optimizations
Aegis Gamer applies these optimizations automatically:

```ini
# /etc/sysctl.d/99-aegis-gaming.conf
vm.swappiness=10
vm.vfs_cache_pressure=50
kernel.sched_autogroup_enabled=0
net.ipv4.tcp_congestion_control=bbr
```

### GPU Drivers

#### NVIDIA Setup
Drivers are pre-installed. To update:
```bash
sudo pacman -S nvidia-dkms nvidia-utils lib32-nvidia-utils
```

#### AMD Setup
Open-source drivers are included. For latest Mesa:
```bash
sudo pacman -S mesa lib32-mesa vulkan-radeon lib32-vulkan-radeon
```

### External Game Drives
Aegis automatically mounts external drives with game-optimized settings:
- NTFS support for Windows game drives
- ext4/btrfs for Linux game libraries
- Fast permission handling

## Game Compatibility

### Proton Compatibility
Most Windows games work out of the box. Check compatibility:
- [ProtonDB](https://www.protondb.com/) - Community ratings
- [Aegis Compatibility DB](https://aegis-os.com/games) - Aegis-tested games

### Native Linux Games
Many games have native Linux versions:
- Most indie games
- Valve games (CS2, Dota 2, TF2)
- Unity/Unreal games with Linux exports

### Anti-Cheat Status
| Anti-Cheat | Status | Notes |
|------------|--------|-------|
| Easy Anti-Cheat | Works | Must be enabled by developer |
| BattlEye | Works | Must be enabled by developer |
| Vanguard (Valorant) | Not Working | Kernel-level, no Linux support |
| FACEIT | Not Working | Requires Windows |

## Configuration Files

### MangoHud Config
```ini
# ~/.config/MangoHud/MangoHud.conf
fps
gpu_stats
cpu_stats
ram
frame_timing
position=top-left
font_size=18
background_alpha=0.3
```

### GameMode Config
```ini
# /etc/gamemode.ini
[general]
renice=10
ioprio=0

[gpu]
apply_gpu_optimisations=accept-responsibility
gpu_device=0
nv_powermizer_mode=1
```

## Pricing & Licensing

**Price: $69 (one-time)**

Includes:
- Lifetime license for Gamer Edition
- All future 3.x updates
- Priority support (1 year)
- Access to Gamer beta channel

### Upgrade Paths
| From | To | Price |
|------|-----|-------|
| Freemium | Gamer | $69 |
| Gamer | Gamer+AI | $60 |
| Basic | Gamer | $40 |

## Support

### Documentation
- [docs.aegis-os.com/gamer](https://docs.aegis-os.com/gamer)
- [Wiki: Game Optimization Guides](https://wiki.aegis-os.com/gaming)

### Community
- [Discord #gaming](https://discord.gg/aegis-os)
- [Reddit r/AegisOSGaming](https://reddit.com/r/aegisosgaming)

### Troubleshooting

#### Game won't launch
1. Check ProtonDB for known issues
2. Try different Proton version
3. Run `aegis-wine-optimizer --diagnose`
4. Check game logs: `~/.steam/steam/steamapps/compatdata/<appid>/pfx/`

#### Poor performance
1. Enable GameMode: `gamemoderun %command%`
2. Check GPU drivers are up to date
3. Use `aegis-performance-tuner --profile gaming`
4. Disable compositor during games

## Contributing

### Development
```bash
git clone https://github.com/DeQuackDealer/AegisOSRepo.git
cd AegisOSRepo
git checkout preview/gamer
```

### Testing
Help test game compatibility:
1. Play games and report results
2. Submit fixes for Wine issues
3. Share optimized game configs

See [CONTRIBUTING.md](../../../CONTRIBUTING.md) for guidelines.

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 3.0.0 | 2024-12 | Arch Linux base, linux-zen kernel |
| 2.5.0 | Legacy | Ubuntu-based (deprecated) |

---

**Aegis OS Gamer** - Built for gamers. By gamers.
