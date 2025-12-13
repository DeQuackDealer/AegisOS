# Aegis OS Gamer Tools (preview/gamer)

## What This Branch Contains

This branch contains **ONLY the gaming-specific tools and configurations** that are layered on top of the base OS to create the Gamer Edition. If you want to improve gaming performance, upscaling, streaming, or game management on Aegis OS, this is where you contribute.

## Included Gaming Tools

### Game Management
```
usr/local/bin/
├── aegis-game-center          # Unified game library (Steam, Lutris, Heroic)
├── aegis-game-hub             # Quick game launcher with stats
├── aegis-game-launcher        # Smart launcher with pre-launch optimization
├── aegis-game-scanner         # Detect installed games across platforms
└── aegis-proton-manager       # Proton/Wine version manager
```

### Performance & Optimization
```
usr/local/bin/
├── aegis-performance-tuner    # System performance profiles (Gaming/Balanced/Quiet)
├── aegis-gamer-performance    # Auto-apply gaming optimizations
├── aegis-upscaler             # AI upscaling (FSR, DLSS, ANU Neural)
├── aegis-render-orchestrator  # Multi-GPU management, eGPU support
├── aegis-gpu-manager          # GPU driver and settings management
└── aegis-mode-switch          # Quick toggle between gaming/desktop modes
```

### Wine & Compatibility
```
usr/local/bin/
├── aegis-wine-optimizer       # Wine prefix management and optimization
├── aegis-mangohud-config      # MangoHud overlay configuration
└── aegis-controller-config    # Game controller mapping and profiles
```

### Streaming & Recording
```
usr/local/bin/
├── aegis-stream               # Quick streaming to Twitch/YouTube
├── aegis-stream-studio        # Full OBS-based streaming setup
├── aegis-stream-deck          # Virtual stream deck with hotkeys
└── aegis-audio-router         # Per-app audio routing for streaming
```

### Desktop Enhancements
```
usr/local/bin/
├── aegis-wallpaper-engine     # Animated/video wallpapers
└── aegis-external-media-handler  # Auto-mount game drives
```

## System Configurations

### Performance Tuning
```
etc/sysctl.d/
├── 99-aegis-gaming.conf           # Basic gaming optimizations
└── 99-aegis-gaming-advanced.conf  # Advanced kernel tweaks

etc/profile.d/
└── aegis-wine-env.sh              # Wine environment variables
```

### Audio (Low Latency)
```
etc/pipewire/pipewire.conf.d/
└── 10-aegis-gaming.conf           # Low-latency audio settings
```

### Game Drive Auto-Mount
```
etc/udev/rules.d/
└── 99-aegis-external-games.rules  # Auto-detect game drives
```

### Systemd Services
```
etc/systemd/system/
├── aegis-gamer-performance.service   # Apply gaming tweaks at boot
├── aegis-render-orchestrator.service # GPU management daemon
└── aegis-license-check.service       # License verification

etc/systemd/user/
└── aegis-wallpaper-engine.service    # Animated wallpaper daemon
```

### Edition Configuration
```
etc/aegis/
├── tier.json                  # Gamer tier definition
├── gamer-packages.list        # Gamer-specific packages
├── gamer-performance.json     # Performance profile defaults
├── proton-config.json         # Proton/Wine settings
├── upscaler-config.json       # Upscaler defaults
├── wine-optimization.conf     # Wine tweaks
└── dual_gpu_profiles.json     # Hybrid graphics profiles
```

## What You Can Contribute

### Priority Areas

1. **Upscaler Improvements**
   - Better FSR/DLSS integration
   - Custom ANU Neural models
   - Per-game profile presets

2. **Game Compatibility**
   - Wine prefix templates for specific games
   - Proton-GE integration
   - Anti-cheat workarounds (where legal)

3. **Performance Tuning**
   - Better CPU governor profiles
   - GPU overclocking presets
   - Memory optimization

4. **Streaming Features**
   - Better OBS scene templates
   - Audio routing improvements
   - Stream alerts integration

5. **Controller Support**
   - More controller mappings
   - Steam Input integration
   - Gyro support

### How to Contribute

1. Fork and clone the repository
2. Switch to this branch:
   ```bash
   git checkout preview/gamer
   ```
3. Make your changes to the gaming tools
4. Test with actual games
5. Submit a pull request to `preview/gamer`

### Testing Your Changes

```bash
# Test upscaler
python3 usr/local/bin/aegis-upscaler --test

# Test game scanner
python3 usr/local/bin/aegis-game-scanner --scan ~/.steam

# Validate all Python scripts
for f in usr/local/bin/aegis-*; do
  python3 -m py_compile "$f" && echo "OK: $f"
done

# Test with GameMode
gamemoderun ./your-test-game
```

## Files NOT in This Branch

This branch does NOT contain:
- Base OS tools (those are in `preview/base-os`)
- AI/ML tools (those are in `preview/aidev`)
- Website code
- Build system
- Other editions (workplace, server, basic)

## Syncing with Main

Gaming tools here are merged into `main` when ready:
```bash
# Maintainers merge approved changes to main
git checkout main
git merge preview/gamer --no-ff -m "Merge gaming improvements"
```

## Gamer Edition Packages

Additional packages installed with Gamer Edition:

### Gaming Kernel
- `linux-zen`, `linux-zen-headers`

### Graphics
- `mesa`, `lib32-mesa`
- `vulkan-icd-loader`, `lib32-vulkan-icd-loader`
- `nvidia-dkms` (NVIDIA systems)

### Wine/Proton
- `wine-staging`, `wine-mono`, `wine-gecko`
- `winetricks`, `lib32-gnutls`, `lib32-libpulse`

### Game Launchers
- `steam`, `lutris`

### Performance
- `gamemode`, `lib32-gamemode`
- `mangohud`, `lib32-mangohud`

## Questions?

- Open an issue with the `gamer` label
- Join [Discord #gaming-dev](https://discord.gg/aegis-os)
- Check [ProtonDB](https://www.protondb.com/) for game compatibility info
