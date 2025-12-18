# Aegis OS - Gamer Branch

Premium gaming features for the Gamer Edition ($49 lifetime / $10 annual). Extends the basic branch with advanced gaming optimizations.

## What's Included

### Premium Gaming Features
- **Dual GPU Rendering** - Split-frame rendering with mixed NVIDIA/AMD support
- **8 Background System Services** - Automatic gaming optimization
- **StreamForge Capture Stack** - 8ms encode latency streaming
- **Advanced Upscaling** - FSR 3.0, DLSS 3.5, XeSS, Neural Upscaler
- **Anti-Cheat Support** - EAC, BattlEye, GameGuard, PunkBuster

### 8 Integrated System Services
All run automatically via systemd:
1. **Adaptive RAM Guardian** - Memory optimization
2. **StreamForge Capture Stack** - Low-latency capture
3. **Latency FastPath** - Input latency reduction
4. **VRAM Heatmap Balancer** - GPU memory management
5. **NetBoost Network Optimizer** - Gaming traffic QoS
6. **Shader Pre-Cache Engine** - Background compilation
7. **Audio Zero-Latency** - 2.7ms audio latency
8. **Thermal Guard** - Temperature management

### Exclusive Gaming Apps
- **Aegis Game Library** - Unified launcher with Console Mode
- **StreamForge Studio** - One-click streaming
- **Aegis Wallpaper Engine** - Animated wallpapers
- **Desktop Style Manager** - 12 desktop layouts

### 22+ Console Emulators
PS1-PS3, Switch (Suyu), Wii U, Xbox 360, Arcade, and more

## Building

This is raw source code. Requires the basic branch as foundation.

```bash
# Clone the repository
git clone https://github.com/DeQuackDealer/AegisOSRepo.git
cd AegisOSRepo
git checkout gamer

# First build basic branch
git checkout basic
./build.sh

# Then build gamer additions
git checkout gamer
./build.sh
```

## Structure

```
gamer/
├── src/                    # Premium feature source code
│   ├── dual_gpu_render.py  # Split-frame rendering
│   ├── streamforge.py      # Capture/streaming
│   ├── latency_fastpath.py # Input optimization
│   ├── ram_guardian.py     # Memory management
│   ├── vram_balancer.py    # GPU memory
│   ├── netboost.py         # Network optimization
│   ├── shader_precache.py  # Shader compilation
│   ├── audio_zerlatency.py # Audio optimization
│   └── thermal_guard.py    # Temperature control
├── configs/                # Premium configurations
│   ├── dual_gpu.conf       # Dual GPU settings
│   ├── streaming.conf      # StreamForge config
│   └── services.conf       # Service configurations
├── services/               # Systemd service definitions
│   └── *.service           # 8 gaming services
└── build.sh               # Build script
```

## License

Aegis OS Gamer Edition - $49 lifetime / $10 annual
Hardware-bound RSA-2048 license required
