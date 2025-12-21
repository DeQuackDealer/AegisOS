# Aegis OS Build System

## Overview
Aegis OS is a commercial Arch Linux-based distribution featuring 3 core editions (Freemium, Basic, Gamer) with a tiered software licensing model. The project includes an automated `archiso`-based build system for ISO creation, a Flask-based promotional website, a comprehensive offline installer, and a payment/license management system. It aims to deliver a Windows 10-inspired desktop experience, optimized gaming via Wine/Proton, over 50 custom Python utilities, and AI-powered security features.

## User Preferences
Preferred communication style: Simple, everyday language.

## Core Selling Points

### 1. Built-in Upscalers (Any Game Can Be Upscaled)
- FSR 3.0, DLSS 3.5, XeSS integration
- Anime4K for animated content
- Aegis Neural Upscaler (custom AI upscaling)
- Works with ANY game, not just supported titles

### 2. Dual GPU Rendering (Focal + Border Split)
- Primary GPU: Renders focal/center region (60%)
- Secondary GPU: Renders border/edge region (40%)
- **Overlap Blending**: 8-pixel overlap zone where both GPUs render, then averaged for seamless transitions
- Mixed vendor support (NVIDIA + AMD together)
- Custom Vulkan layer implementation

### 3. Heavy RAM Optimization via AI
- Adaptive RAM Guardian service
- AI-powered memory reclamation
- Gaming process prioritization
- Leak detection and prevention
- Minimal OS footprint (800MB idle)

### 4. AI Security Checker
- Scans every file before download/execution
- Flags suspicious files with detailed warnings
- Can modify/quarantine malicious files
- Real-time protection daemon
- Signature + behavior analysis

## Gamer Edition - Flagship Product ($49 lifetime / $10 annual)

### 9 Integrated System Services (Background Daemons)
All services run automatically via systemd - no user configuration needed:

1. **Adaptive RAM Guardian** - Memory reclamation, leak detection, gaming process prioritization
2. **StreamForge Capture Stack** - Kernel-mode capture, NDI dual-PC streaming, AV1 encoding, Replay Buffer
3. **Latency FastPath** - IRQ affinity steering, 1000Hz USB polling, CPU governor auto-switching, input optimization
4. **VRAM Heatmap Balancer** - Real-time GPU memory monitoring, shader cache cleanup
5. **NetBoost Network Optimizer** - QoS for gaming traffic, BBR congestion control
6. **Shader Pre-Cache Engine** - Background DXVK/VKD3D shader compilation
7. **Audio Zero-Latency** - PipeWire optimization, Spatial Audio, AI Noise Suppression, EQ presets
8. **Thermal Guard** - Smart temperature monitoring, automatic fan curve adjustment
9. **Gamer Performance** - Display optimization, kernel tuning, VRR/FreeSync, performance profiles

### OS-Level Features
- **Kernel**: BORE Scheduler, BFQ I/O, Transparent Huge Pages, NUMA-Aware Allocation
- **Wine/Proton**: ESYNC/FSYNC, DXVK Pre-Cached Shaders, VKD3D-Proton optimized
- **Dual GPU**: Split-Frame Rendering (60/40 split) with 8-pixel overlap blending via custom Vulkan layer
- **Upscaling**: FSR 3.0, DLSS 3.5, XeSS, Anime4K, Aegis Neural Upscaler

### 4 Exclusive Gaming Apps (Aegis-only)
1. **Aegis Game Library** - Unified launcher with Console Mode & SD card support
2. **StreamForge Studio** - One-click streaming with 8ms encode latency
3. **Aegis Wallpaper Engine** - Animated/interactive wallpapers
4. **Desktop Style Manager** - 12 pre-built desktop layouts

### Legal & Marketing Notes (Updated Dec 2025)
- **Anti-cheat claims**: Only claim EAC, BattlEye, GameGuard, PunkBuster support. Valorant/Fortnite do NOT work on Linux due to kernel-level anti-cheat.
- **Emulators**: Use Suyu (Switch) and Lime3DS (3DS) instead of Yuzu/Citra which were legally shut down by Nintendo.
- **Performance claims**: Use "High compatibility" and "Low latency" instead of specific percentages or milliseconds.
- **Benchmarks**: All benchmarks marked as "Estimated" with disclaimer about hardware variance.
- **Update guarantee**: Guaranteed updates through January 1, 2028 with "likely continuation beyond" language.
- **RGB support**: All RGB is via OpenRGB (community-driven), not official vendor integrations.

## System Architecture

### Build System
The core build system uses `archiso` to create bootable ISOs for all editions. Full Aegis branding with custom `profiledef.sh`, `/etc/os-release` codenames, LightDM greeter, Plymouth boot splash, and pre-configured `aegis` user.

### Promotional Website
Flask-based marketing website with security features (rate limiting, JWT, CSRF, audit logging). RESTful APIs for license management, Stripe payments, and admin panel.

### Installer System
Fully offline Python/tkinter GUI installer with PyInstaller packaging. SHA-256 ISO verification and RSA-2048 license signature verification.

### Payment & License System
Stripe integration using manual secrets (STRIPE_SECRET_KEY_LIVE, STRIPE_PUBLISHABLE_KEY_LIVE) instead of Replit's Stripe connector. SendGrid email delivery, unique license key generation. Admin panel with promotional "free period" modes.

**Note:** The Stripe connector in .replit cannot be removed via agent. To publish, may need to complete connector setup or contact Replit support to remove it.

## Pricing Structure (3 Core Editions)
- **Freemium**: Free
- **Basic**: $19 lifetime, $3/year
- **Gamer** (Flagship): $49 lifetime, $10/year

*More Specialised Editions Coming Soon*

## AegisOSRepo Structure
Raw source code repository with 2 branches:
- **basic branch**: Core foundation (Freemium base) - Proton/Wine integration, basic gaming
- **gamer branch**: Premium features ($49) - Dual GPU, 9 services, StreamForge, etc.

Located at: `AegisOSRepo/` directory

## Verification Summary (December 2025)
- **36 Gamer Tools**: 32,592 total lines of code (all genuine implementations)
- **9 System Services**: Real systemd daemons with D-Bus/cgroups/sysfs integration
- **4 Exclusive Apps**: Full GTK applications (Game Library 2009 LOC, StreamForge Studio 2429 LOC, Wallpaper Engine 2358 LOC, Desktop Style Manager 1886 LOC)
- **24 Desktop Entries**: Full application menu integration
- **234 Packages**: Complete gaming stack including emulators (RetroArch, Dolphin, PCSX2, PPSSPP), launchers (Steam, Lutris, Heroic, Bottles), and utilities
- **RGB Control**: OpenRGB integration with CLI and GTK GUI
- **Dual GPU Rendering**: Vulkan layer split-frame with Gamescope/vkBasalt integration
- **Upscaling**: FSR 3.0/DLSS/XeSS/Anime4K with per-game profiles
- **System Tuning**: sysctl optimizations, security limits, udev rules for gaming

## External Dependencies
* **archiso**: ISO build system
* **Flask, PyJWT, SendGrid, Stripe**: Web & payment
* **Python 3, tkinter**: Tools & installer
* **Wine/Proton, DXVK, VKD3D**: Windows compatibility
* **PipeWire, FFmpeg, MPV**: Audio/video
* **Steam, Lutris, Heroic**: Game launchers
* **GameMode, MangoHud**: Gaming optimization
* **OpenRGB**: RGB peripheral control
