# Aegis OS Build System

## Building ISOs with GitHub Actions

Push this repo to GitHub and use the included workflow to build real ISOs:

1. **Push to GitHub**: Create a repo and push this code
2. **Run the workflow**: Go to Actions > "Build Aegis OS ISOs" > Run workflow
3. **Select edition**: Choose which edition to build (or "all" for all 7)
4. **Download artifacts**: ISOs appear as downloadable artifacts when complete

The workflow runs on an Arch Linux container with all required tools (archiso, mkarchiso, etc).

## Overview
Aegis OS is a commercial Linux distribution based on Arch Linux, offering 7 distinct OS editions (Freemium, Basic, Gamer, AI Developer, Gamer+AI, Server, Workplace) with a tiered software licensing model. The project encompasses an automated `archiso`-based build system for creating bootable ISOs, a Flask-based promotional website, a comprehensive offline installer system, and a payment/license management system. It aims to provide a Windows 10-inspired desktop experience, optimized gaming through Wine/Proton, and a suite of over 50 custom Python-based utilities, along with AI-powered security features across all editions. The project's ambition is to capture various market segments, from casual users to AI developers and enterprise clients.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Build System
The core build system utilizes `archiso` for creating bootable ISOs, supporting 7 editions with different Linux kernels (`linux`, `linux-zen`, `linux-lts`). Edition-specific package lists and configurations define the software included in each ISO.

**Custom Branding (Fully Aegis-branded, not renamed Arch):**
- Custom `profiledef.sh` with Aegis ISO naming (`aegis-os-{edition}-x.x.x-x86_64.iso`), volume label (`AEGIS_YYYYMM`), and publisher info
- Custom `/etc/os-release` identifying as "Aegis OS" with edition-specific codenames
- LightDM greeter configuration with Aegis-Win10 theme and autologin to `aegis` user
- Custom Plymouth boot splash theme with Aegis branding colors
- Fastfetch configuration displaying Aegis OS info
- Pre-configured `aegis` user with passwordless sudo and group memberships
- First-boot service for post-install user setup

### Promotional Website
A Flask-based marketing website with a static, Windows 10-inspired HTML frontend. It features robust security (rate limiting, JWT, CSRF, audit logging) and showcases OS editions, features, and pricing data from `TIER_FEATURES.json`. It provides RESTful APIs for license management, monitoring, analytics, and user authentication.

### Installer System
A fully offline, cross-platform Python/tkinter GUI installer, packaged via PyInstaller. It supports both Freemium (`aegis-installer-freemium.py`) and licensed (`aegis-installer-licensed.py`) editions. ISO verification is done via SHA-256 checksums from `manifest.json`, and licensed editions include RSA-2048 signature verification of license files using `cryptography` (PKCS1v15 + SHA-256).

### Payment & License System
Manages user accounts, generates unique license keys (e.g., `PREFIX-XXXX-XXXX-XXXX`), and processes payments via Stripe. It tracks users, licenses, Stripe events, and email logs, sending license keys via SendGrid. An admin panel supports promotional "free period" modes.

### Auto-Update System
A REST API allows Aegis OS installations to check for and download RSA-signed updates. It supports edition-specific update channels (Stable, Priority, Beta, LTS).

### Desktop Environment
Based on XFCE, offering a Windows 10-inspired user experience with custom GTK themes (Light/Dark), an Aegis Theme Manager, Aero Snap, translucent taskbar, and Windows-compatible keyboard shortcuts.

### Wine/Proton Optimization
Achieves high Windows application compatibility through pre-configured Wine/Proton settings and an `Aegis Wine Optimizer` tool for managing optimized prefixes and dependencies.

### Aegis Exclusive Tools
Over 50 custom Python-based utilities (`/usr/local/bin/`) with both GUI (tkinter) and CLI interfaces. Tools are tier-gated and include:
- **Pro Baseline Tools (All Paid Editions):** `aegis-office-hub`, `aegis-meet`, `aegis-resolve-studio`, `aegis-creative-suite`, `aegis-desktop-link`, `aegis-network-display`, `aegis-file-share`, `aegis-mobile-link`, `aegis-home-nas`, `aegis-browser-hub`, `aegis-cloud-sync`, `aegis-screenshot-pro`, `aegis-system-monitor`, `aegis-layout-switcher`, `aegis-audio-enhance`.
- **Basic Edition Tools:** `aegis-getting-started`, `aegis-system-care`, `aegis-security-suite`, `aegis-backup-suite`, `aegis-media-suite`, `aegis-customization`, `aegis-productivity`, `aegis-internet`.
- **Gamer Edition Tools:** `aegis-game-scanner`, `aegis-game-hub`, `aegis-proton-manager`, `aegis-performance-tuner`, `aegis-wine-optimizer`, `aegis-stream-studio`, `aegis-mangohud-config`, `aegis-controller-config`, `aegis-upscaler`, `aegis-render-orchestrator`, `aegis-vpn-manager` (WireGuard/ProtonVPN integration), `aegis-screen-split` (window tiling for streamers).
- **Workplace Edition Tools:** `aegis-workspace-hub`, `aegis-it-toolkit`, `aegis-document-vault`, `aegis-enterprise-suite`, `aegis-collaboration`, `aegis-document-management`, `aegis-productivity-tools`, `aegis-it-management`.
- **AI Developer Edition Tools:** `aegis-ml-studio`, `aegis-compute-stack`, `aegis-model-hub`, `aegis-inference-engine`, `aegis-gpu-tools`, `aegis-data-science`, `aegis-llm-tools`.
- **Gamer+AI Edition Tools:** `aegis-ai-gaming`, `aegis-neural-upscaling`, `aegis-ai-streaming`, `aegis-game-modding`, `aegis-performance-ai`.
- **Common Tools:** `aegis-wallpaper-engine`, `aegis-stream`, `aegis-security-daemon`.
Tools leverage `pkexec` for privileged operations and use secure `subprocess` calls.

### AI Security Tiering System
All editions integrate AI-powered security, from basic heuristics to XDR and ML-powered threat intelligence, configured via `tier-security.json` and `aegis_ai_security.py`.

### Aegis Neural Upscaler (ANU) System
Custom AI upscaling technology for gaming editions, featuring `aegis-upscaler` (GTK3 GUI/CLI, multiple backends including ANU Neural, per-game profiles) and `aegis-game-launcher` (unified launcher with pre-launch upscaler injection and post-game performance reports).

## External Dependencies

### Build System Dependencies
*   **archiso**: Arch Linux ISO build system.
*   **Linux Build Tools**: GCC, Make, pacman, mksquashfs, xorriso, syslinux, squashfs-tools.
*   **Python 3**: For build orchestration.

### Web Server Dependencies
*   **Flask**: Python web framework.
*   **PyJWT**: JSON Web Token handling.
*   **SendGrid**: Transactional email service.
*   **Stripe**: Payment processing.

### Aegis Tools Dependencies
*   **Python 3**
*   **tkinter**: GUI components.
*   **MPV**: Renderer for wallpaper engine and streaming.
*   **FFmpeg**: Video processing.
*   **ClamAV, UFW**: For security tools.
*   **rsync**: For backup.
*   **Steam, Lutris, Heroic**: Game library integrations.
*   **KDE Connect, Barrier/Synergy**: Device linking integrations.
*   **GameMode**: Gaming optimization.
*   **NVIDIA drivers**: Hardware encoding.
*   **AppArmor/Firejail**: Sandboxing.
*   **PipeWire/PulseAudio**: Audio capture.
*   **rclone**: Cloud storage integration.
*   **Ollama, llama.cpp, vLLM, ONNX Runtime**: AI inference backends.
*   **Docker/Podman**: Container management.
*   **Samba, NFS**: Network Attached Storage.

## Recent Changes (December 2025)

### ISO Boot Failure Fixes - Missing Dependencies and Import Guards

**Package List Updates (build-system/archiso/packages/)**:
- **base.txt**: Added python-psutil, python-zeroconf, gtk3, gobject-introspection, wmctrl, xdotool, xrandr, barrier
- **gamer.txt**: Added python-evdev, python-cairo, pango for controller/screen utilities
- **freemium.txt**: Added python-psutil for system tools
- **basic.txt**: Added gtk3, python-gobject, gobject-introspection, python-psutil
- **aidev.txt**: Added gtk3, python-gobject, gobject-introspection, python-psutil
- **server.txt**: Added gtk3, python-gobject, gobject-introspection, python-psutil
- **workplace.txt**: Added gtk3, python-gobject, gobject-introspection, python-psutil, tk
- **gamer-ai.txt**: Added gtk3, python-gobject, gobject-introspection, python-psutil, python-evdev, python-cairo, pango

**GTK Import Guards** (39 utilities fixed):
- Added try/except guards around GTK imports with `GTK_AVAILABLE` flag
- Scripts now exit gracefully instead of crashing if GTK3 is missing
- Gamer: aegis-controller-config, aegis-screen-split, aegis-game-hub, aegis-vpn-manager, aegis-wine-optimizer, aegis-proton-manager, aegis-game-scanner, aegis-stream-studio, aegis-gpu-manager, aegis-upscaler, aegis-mangohud-config, aegis-performance-tuner
- Basic: aegis-system-care, aegis-security-suite, aegis-productivity, aegis-media-suite, aegis-getting-started, aegis-customization, aegis-backup-suite
- Workplace: aegis-productivity-tools, aegis-it-management, aegis-enterprise-suite, aegis-document-management, aegis-collaboration
- AI Developer: aegis-training-optimizer, aegis-model-hub, aegis-ml-studio, aegis-llm-tools, aegis-inference-engine, aegis-gpu-tools, aegis-dataset-manager, aegis-data-science, aegis-compute-stack, aegis-ai-monitor
- Server: aegis-server-security, aegis-monitoring, aegis-load-balancer, aegis-container-tools, aegis-backup-enterprise
- Gamer+AI: aegis-performance-ai, aegis-neural-upscaling, aegis-game-modding, aegis-ai-streaming, aegis-ai-gaming

**Tkinter Import Guards** (22 utilities improved):
- Enhanced error handling with stderr output for missing tkinter
- Gamer: aegis-game-launcher, aegis-stream-deck, aegis-audio-router, aegis-stream, aegis-game-center
- Workplace: aegis-workspace-hub, aegis-it-toolkit, aegis-document-vault
- Pro: aegis-screenshot-pro, aegis-network-display, aegis-mobile-link, aegis-layout-switcher, aegis-home-nas, aegis-file-share, aegis-desktop-link, aegis-creative-suite, aegis-cloud-sync, aegis-browser-hub, aegis-audio-enhance
- Pro-Productivity: aegis-resolve-studio, aegis-office-hub, aegis-meet

### Critical Regression Fixes for Aegis Utilities

**aegis-system-monitor**:
- Added missing `pathlib.Path` import for home directory operations
- Fixed logging initialization to work in both dashboard and service modes
- Added fallback CSV export paths (`~/.aegis/exports` → home directory) when `/var/lib/aegis/exports` is not writable

**aegis-screen-split**:
- Fixed `MonitorManager.detect_monitors()` with xrandr availability check before calling
- Converted `_toggle_zones`, `_apply_layout`, `_learn_windows` to async subprocess calls
- Added graceful fallback to default 1920x1080 monitor when xrandr unavailable

**aegis-controller-config**:
- Verified proper `poll_timeout_id` tracking for GLib timeout cleanup
- Resource cleanup (`_on_window_destroy`) properly closes file descriptors

**aegis-desklink**:
- JSON parsing errors properly handled with `JSONDecodeError` exception block

### Known Limitations
- `MonitorManager.detect_monitors()` uses synchronous subprocess.run during initialization (has 5-second timeout to prevent hangs)
- Future improvement: Make monitor detection fully async for better UI responsiveness during startup