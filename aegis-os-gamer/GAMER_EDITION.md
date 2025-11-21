# Aegis OS Gamer Edition

**$99/year** - AI-powered gaming with maximum performance

## What's Included

### Core Gaming Features
- ✓ **Linux 6.6.7** - Low-latency performance kernel
- ✓ **XFCE 4.18** - Lightweight & responsive desktop
- ✓ **Wine 8.21** - Windows game compatibility
- ✓ **Proton** - Steam games run native speed
- ✓ **Vulkan & OpenGL** - Maximum graphics
- ✓ **Mesa3D** - GPU acceleration

### AI-Powered Optimizations
- ✓ **Game Optimizer AI** - Auto-detects games, optimizes settings
- ✓ **Frame Rate Boost** - AI predictions for higher FPS
- ✓ **Graphics Tuning** - Auto adjust resolution/quality
- ✓ **CPU/GPU Balancing** - Intelligent resource allocation
- ✓ **Network Optimization** - Low-ping gaming

### Gaming Tools & Utilities
- ✓ **Lutris** - Game launcher (1000+ games)
- ✓ **GameMode** - Performance tweaks
- ✓ **MangoHUD** - FPS/stats overlay
- ✓ **ProtonGE** - Enhanced Proton versions
- ✓ **DXVK** - DirectX to Vulkan translation
- ✓ **VKD3D** - DirectX 12 support
- ✓ 50+ gaming utilities pre-installed

### Gaming Libraries Pre-Installed
- DirectX 9, 10, 11, 12
- Vulkan with ray tracing
- OpenGL 4.6
- SDL/SDL2
- Qt5/Qt6
- ALSA/PulseAudio

### Performance Tweaks
- Low-latency kernel (500Hz)
- Preemption disabled for gaming
- CPU governor: performance
- I/O scheduler: deadline
- Swappiness: 10 (minimal swap)
- Transparent hugepages enabled

### Support & Updates
- ✓ All Freemium features
- ✓ AI game optimizer updates
- ✓ Priority security patches
- ✓ Gaming library updates
- ✓ Email support
- ✓ License activation

## Building Aegis OS Gamer

### Requirements
- Linux machine (Ubuntu 20.04+)
- 8GB+ RAM (16GB recommended)
- 20GB free disk space
- 90-120 minutes build time

### Quick Build
```bash
cd aegis-os-gamer
chmod +x build.sh
./build.sh
```

### Output Files
- `aegis-os-gamer.iso` - Bootable ISO
- `aegis-os-gamer.ext4` - Filesystem
- `aegis-kernel-gamer` - Optimized kernel
- `checksums.txt` - Verification

## Installing on USB

### Step 1: Download Balena Etcher
https://balena.io/etcher

### Step 2: Flash ISO
- Open Etcher
- Select: `aegis-os-gamer.iso`
- Select: USB drive (8GB+)
- Click Flash

### Step 3: Boot & Login
- Insert USB into gaming PC
- Boot from USB
- Auto-login as `aegis`
- Open Lutris or Steam

## Testing in VirtualBox

### Minimum VM Settings
- CPU: 4 cores minimum
- Memory: 8GB minimum
- GPU: 3D acceleration enabled
- Storage: 20GB dynamic

### Enable Gaming Features
1. Settings → System → Processor → 4+ cores
2. Settings → Display → Video Memory → 128MB
3. Settings → Display → 3D Acceleration → Enabled
4. Start VM

## License Activation

```bash
# Test activation
aegis-cli activate --key AEGIS-GAMER-2024-ACTIVE

# Check status
aegis-cli status

# Update optimizations
aegis-cli update
```

## Gaming Performance Tips

### For Maximum FPS
1. Run: `gamemoderun <game>`
2. Open MangoHUD overlay (Shift+F12)
3. Monitor AI optimizer in background

### For Game Compatibility
1. Use Lutris for unknown games
2. Enable Proton if needed
3. Run in windowed mode first
4. Check game-specific settings

### For Network Gaming
1. Enable low-latency network
2. Reduce network jitter
3. Use wired connection (Ethernet)
4. Disable background updates during play

## Troubleshooting

**Game won't launch:**
- Check Lutris for this game
- Try different Proton version
- Enable compatibility mode

**Low FPS:**
- Check AI optimizer is running
- Disable effects (shadows, bloom)
- Lower resolution to 1080p
- Check GPU temperature

**Audio issues:**
- Switch between ALSA/PulseAudio
- Check volume levels
- Restart audio service

## Advanced Configuration

### Overclock GPU
```bash
sudo aegis-optimizer --gpu-mode aggressive
```

### Enable Ray Tracing
```bash
sudo aegis-optimizer --raytracing on
```

### Monitor Performance
```bash
mangoplus  # Shows live stats
```

---

**Aegis OS Gamer** - Built for competitive gaming, 60+ FPS, AI-optimized.

Ready to game? Download the ISO and start building! 🎮
