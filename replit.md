# Aegis OS Build System

## Overview
Aegis OS is a commercial Arch Linux-based distribution featuring seven distinct editions (Freemium, Basic, Gamer, AI Developer, Gamer+AI, Server, Workplace) with a tiered software licensing model. The project includes an automated `archiso`-based build system for ISO creation, a Flask-based promotional website, a comprehensive offline installer, and a payment/license management system. It aims to deliver a Windows 10-inspired desktop experience, optimized gaming via Wine/Proton, over 50 custom Python utilities, and AI-powered security features. Aegis OS targets a broad market, from casual users to AI professionals and enterprises.

## User Preferences
Preferred communication style: Simple, everyday language.

## Gamer Edition - Flagship Product ($69 lifetime / $10 annual)

### 8 Integrated System Services (Background Daemons)
All services run automatically via systemd - no user configuration needed:

1. **Adaptive RAM Guardian** - Memory reclamation, leak detection, gaming process prioritization
2. **StreamForge Capture Stack** - Kernel-mode capture (kmsgrab/NVFBC), 8ms encode latency
3. **Latency FastPath** - IRQ affinity steering, 1000Hz USB polling, CPU governor auto-switching
4. **VRAM Heatmap Balancer** - Real-time GPU memory monitoring, shader cache cleanup
5. **NetBoost Network Optimizer** - QoS for gaming traffic, BBR congestion control
6. **Shader Pre-Cache Engine** - Background DXVK/VKD3D shader compilation
7. **Audio Zero-Latency** - PipeWire optimization, 2.7ms competitive mode
8. **Thermal Guard** - Smart temperature monitoring, automatic fan curve adjustment

### OS-Level Features
- **Kernel**: BORE Scheduler, BFQ I/O, Transparent Huge Pages, NUMA-Aware Allocation
- **Wine/Proton**: ESYNC/FSYNC, DXVK Pre-Cached Shaders, VKD3D-Proton optimized
- **Dual GPU**: Split-Frame Rendering (60/40 split) via custom Vulkan layer, mixed NVIDIA/AMD support
- **Upscaling**: FSR 3.0, DLSS 3.5, XeSS, Anime4K, Aegis Neural Upscaler

### Website Marketing Sections (gamer.html)
- Hero with pricing cards ($69 lifetime / $10 annual)
- Quick stats: 98%+ compatibility, <1ms latency, 5 anti-cheats, 8 services, 18+ emulators, 0 bloatware
- Flagship Premium Features showcase
- Integrated System Services grid (8 services)
- Kernel & System-Level Optimizations
- Comparison Table: Aegis vs Windows 11 vs SteamOS (11 metrics)
- Why Linux Gaming in 2025 section
- System Requirements (Minimum, 4K Gaming, Dual GPU)
- FAQ section (6 questions)
- Controller Support, Streaming, Performance sections

## System Architecture

### Build System
The core build system uses `archiso` to create bootable ISOs for all seven editions. Full Aegis branding with custom `profiledef.sh`, `/etc/os-release` codenames, LightDM greeter, Plymouth boot splash, and pre-configured `aegis` user.

### Promotional Website
Flask-based marketing website with security features (rate limiting, JWT, CSRF, audit logging). RESTful APIs for license management, Stripe payments, and admin panel.

### Installer System
Fully offline Python/tkinter GUI installer with PyInstaller packaging. SHA-256 ISO verification and RSA-2048 license signature verification.

### Payment & License System
Stripe integration using manual secrets (STRIPE_SECRET_KEY_LIVE, STRIPE_PUBLISHABLE_KEY_LIVE) instead of Replit's Stripe connector. SendGrid email delivery, unique license key generation. Admin panel with promotional "free period" modes.

**Note:** The Stripe connector in .replit cannot be removed via agent. To publish, may need to complete connector setup or contact Replit support to remove it.

## Pricing Structure
- **Gamer** (Flagship): $69 lifetime, $10/year
- **Basic**: $19 lifetime, $3/year
- **Workplace**: $9 lifetime, $2/year
- **AI Developer**: $79 lifetime, $12/year
- **Gamer+AI**: $119 lifetime, $17/year
- **Freemium**: Free
- **Server**: Contact Us

## External Dependencies
* **archiso**: ISO build system
* **Flask, PyJWT, SendGrid, Stripe**: Web & payment
* **Python 3, tkinter**: Tools & installer
* **Wine/Proton, DXVK, VKD3D**: Windows compatibility
* **PipeWire, FFmpeg, MPV**: Audio/video
* **Steam, Lutris, Heroic**: Game launchers
* **GameMode, MangoHud**: Gaming optimization
* **OpenRGB**: RGB peripheral control
