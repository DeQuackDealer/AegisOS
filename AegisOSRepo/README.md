# Aegis OS Repository

Raw source code for Aegis OS - The Ultimate Gaming Linux Distribution.

## Branches

### `basic` - Foundation Branch (Freemium)
Core system components that form the foundation for all Aegis OS editions.

**Includes:**
- Arch Linux base with optimizations
- Proton/Wine integration for Windows games
- DXVK & VKD3D-Proton for DirectX translation
- Basic gaming utilities
- License management system
- Steam, Lutris integration

**Use:** This is the Freemium edition base. Free for personal use.

### `gamer` - Premium Gaming Branch ($49 lifetime / $10 annual)
Advanced gaming features exclusive to the Gamer Edition.

**Includes:**
- Dual GPU split-frame rendering
- 8 background system services
- StreamForge capture stack (8ms latency)
- Latency FastPath (1000Hz USB polling)
- VRAM Heatmap Balancer
- NetBoost network optimizer
- Shader pre-cache engine
- Audio zero-latency (2.7ms)
- Thermal Guard

**Use:** Requires Gamer Edition license.

## Building

This is raw, uncompilable source code. To build:

```bash
# Clone repository
git clone https://github.com/DeQuackDealer/AegisOSRepo.git
cd AegisOSRepo

# Build basic branch first
git checkout basic
./build.sh

# Then build gamer branch
git checkout gamer
./build.sh
```

### Build Requirements
- Arch Linux or Arch-based system
- `archiso` package
- Python 3.10+
- Root privileges

## Structure

```
AegisOSRepo/
├── basic/              # Foundation (Freemium base)
│   ├── src/            # Core source code
│   ├── configs/        # System configurations
│   ├── services/       # Systemd services
│   └── build.sh        # Build script
│
└── gamer/              # Premium features
    ├── src/            # Premium source code
    ├── configs/        # Gaming configurations
    ├── services/       # 8 gaming services
    └── build.sh        # Build script
```

## License

- **Freemium Edition:** Free for personal use
- **Gamer Edition:** $49 lifetime / $10 annual

Hardware-bound RSA-2048 licensing. Purchase at: https://aegis-os.replit.app

## Links

- Website: https://aegis-os.replit.app
- Main Repository: https://github.com/DeQuackDealer/AegisOS
- Issues: https://github.com/DeQuackDealer/AegisOS/issues
