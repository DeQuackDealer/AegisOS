# Aegis OS Build System

## Overview

Aegis OS is a conceptual Linux distribution build system designed to demonstrate a tiered software licensing model. It provides multiple OS editions (Freemium, Basic, Gamer, AI Developer, Server, Workplace) with varying feature sets. The project includes an automated build system for creating bootable ISOs using Buildroot and a Flask-based promotional website to market these editions. Its ambition is to simulate a commercial Linux distribution based on Linux Lite, offering a comprehensive ecosystem of custom tools and a structured payment/licensing system.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Build System

The build system leverages Buildroot for creating customized Linux distributions. Python scripts orchestrate a multi-stage pipeline: source code obfuscation, Buildroot compilation, filesystem image creation, and ISO packaging. Key scripts include `build-aegis.py` (main launcher), `build-replit.py` (Replit orchestrator), `obfuscate.py` (code protection), and `deploy.py` (deployment pipeline). It supports seven distinct OS editions, each with specific kernel modules and filesystem overlays.

### Promotional Website

The marketing website is built with Flask, featuring a Windows 10-inspired static HTML frontend with inline CSS. It incorporates robust security measures including rate limiting, security headers, JWT authentication, CSRF protection, and audit logging. The site manages six distinct OS editions with features and pricing defined in `TIER_FEATURES.json`. RESTful APIs are provided for license management, system monitoring, analytics, and user authentication. Legal compliance is ensured through scripts that apply disclaimers and manage public-facing content.

### Installer System

The project includes cross-platform GUI installers: Windows HTA (HTML Application) installers and macOS/Linux shell scripts with TUI. These installers handle ISO downloads, SHA256 verification, USB drive detection, and progress display. They support both Freemium and licensed editions, with distinct UI themes and functionality.

### Payment & License System

A robust payment and license system is integrated, managing user accounts, license key generation (e.g., `PREFIX-XXXX-XXXX-XXXX` format with checksums), and Stripe-based payment processing. Database models track users, licenses, Stripe events, and email logs. Confirmation emails with license keys are sent via SendGrid.

### Aegis Exclusive Tools

Each OS edition includes 25+ custom Python-based utilities located in `/usr/local/bin/`. All tools support GUI (tkinter) and CLI modes, tier-based feature gating, and logging.

**Key Tools:**

1. **aegis-wallpaper-engine v3.1** - AI-powered animated wallpaper system
   - MPV-based rendering (no Chrome dependency)
   - AI preference learning (time-based, category-based suggestions)
   - Weekly update checks from Aegis servers
   - Video: MP4, AVI, MKV, WebM, MOV, HEVC, VP9, AV1
   - Image: JPG, PNG, GIF, WebP, TIFF, SVG, HEIC
   - Audio control, gaming mode auto-pause

2. **aegis-stream v1.0** - Local game/desktop streaming
   - Host mode: Screen capture, hardware encoding (NVENC/VAAPI/AMF)
   - Client mode: Low-latency playback, input forwarding
   - Quality presets: Ultra (4K60) to Potato (480p30)
   - PIN-based pairing, auto-discovery on LAN
   - Freemium: 720p30 max, no audio, watermark

3. **aegis-security-daemon** - Background security service
   - File integrity monitoring with hash verification
   - Suspicious process detection
   - Auth rate limiting
   - Privilege separation
   - Secure IPC via Unix sockets

4. **aegis-sandbox-policy** - Application sandboxing
   - AppArmor/Firejail profile management
   - Filesystem/network access control
   - Per-tool security policies

**Tier Limitations (Freemium vs Full):**
- security-center: Basic firewall only vs full ClamAV/UFW
- backup-pro: Manual only, 5GB max vs scheduled, unlimited
- gaming-optimizer: Basic mode vs custom profiles/overclocking
- desktop-effects: Basic transparency vs blur/animations
- app-store: 5 installs/month vs unlimited

### Admin Panel

A comprehensive admin panel provides API endpoints for managing the system, including analytics (sales, edition breakdown, trends), user management (listing, details, updates), system health monitoring (database, disk, memory), bulk operations (license creation, email sending), and reporting (monthly sales, data export).

## External Dependencies

### Build System Dependencies

*   **Buildroot**: Embedded Linux build system.
*   **Linux Build Tools**: GCC, Make, debootstrap, mksquashfs, xorriso, isolinux, squashfs-tools.
*   **Python 3**: For build orchestration scripts.

### Web Server Dependencies

*   **Flask**: Python web framework.
*   **PyJWT**: For JSON Web Token handling.
*   **Python Standard Libraries**: `hashlib`, `hmac`, `secrets` for security features.
*   **JSON**: For configuration and API responses.
*   **SendGrid**: For transactional email (requires API key).
*   **Stripe**: For payment processing.

### Aegis Tools Dependencies

*   **Python 3**: Core for all tools.
*   **tkinter**: For GUI components of Aegis tools.
*   **MPV**: Primary renderer for `aegis-wallpaper-engine` and `aegis-stream`.
*   **FFmpeg**: Video processing, encoding, format conversion.
*   **ClamAV, UFW**: For `aegis-security-center`.
*   **rsync**: For `aegis-backup-pro`.
*   **Steam, Lutris, Heroic**: Integrations for `aegis-game-library`.
*   **KDE Connect, Barrier/Synergy**: Integrations for device linking.
*   **GameMode**: Integration for `aegis-gaming-optimizer`.
*   **NVIDIA drivers**: For `aegis-nvidia-info` and hardware encoding.
*   **AppArmor/Firejail**: For `aegis-sandbox-policy`.
*   **PipeWire/PulseAudio**: For audio capture in `aegis-stream`.