# Aegis OS Build System

## Overview
Aegis OS is a conceptual Linux distribution build system demonstrating a tiered software licensing model. It offers multiple OS editions (Freemium, Basic, Gamer, AI Developer, Server, Workplace) with varying features, targeting a commercial Linux distribution based on Linux Lite. The project includes an automated build system for creating bootable ISOs using Buildroot and a Flask-based promotional website for marketing these editions. Its ambition is to create a comprehensive ecosystem with custom tools and a structured payment/licensing system.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Build System
Leverages Buildroot and Python scripts for a multi-stage pipeline: source obfuscation, Buildroot compilation, filesystem image creation, and ISO packaging. It supports seven OS editions with specific kernel modules and filesystem overlays.

### Promotional Website
A Flask-based marketing website with a Windows 10-inspired static HTML frontend. Features robust security (rate limiting, JWT, CSRF, audit logging), manages six OS editions with features and pricing from `TIER_FEATURES.json`, and provides RESTful APIs for license management, monitoring, analytics, and user authentication.

### Installer System
Cross-platform GUI installers include Windows HTA (HTML Application) and macOS/Linux shell scripts with TUI. They handle ISO downloads, SHA256 verification, USB detection, and support Freemium and licensed editions with distinct UIs. Licensed installers utilize RSA-2048 asymmetric cryptography for license signature verification.

### Payment & License System
Manages user accounts, generates license keys (e.g., `PREFIX-XXXX-XXXX-XXXX`), and processes payments via Stripe. It tracks users, licenses, Stripe events, and email logs, sending confirmation emails with license keys via SendGrid. An admin panel supports "free period" mode for promotions, bypassing license validation.

### Auto-Update System
Provides a REST API for Aegis OS installations to check for and download updates, supporting both Freemium and paid editions. Updates are RSA-signed for verification and offer edition-specific channels (Stable, Priority, Beta, LTS).

### Desktop Environment
Offers a Windows 10-inspired desktop experience with XFCE, custom GTK themes (Light/Dark), and a configurable Aegis Theme Manager. Includes features like Aero Snap, a translucent taskbar, and Windows-compatible keyboard shortcuts.

### Wine/Proton Optimization
Aims for high Windows application compatibility through pre-configured Wine/Proton settings (`wine-optimization.conf`, `proton-config.json`) and an `Aegis Wine Optimizer` tool for managing optimized prefixes and dependencies.

### Aegis Exclusive Tools
Over 25 custom Python-based utilities (`/usr/local/bin/`) offering GUI (tkinter) and CLI modes, with tier-based feature gating and logging. Key tools include:
*   **aegis-wallpaper-engine**: AI-powered animated wallpaper system.
*   **aegis-stream**: Local game/desktop streaming solution.
*   **aegis-security-daemon**: Background security service for integrity monitoring and threat detection.
*   **aegis-sandbox-policy**: Application sandboxing via AppArmor/Firejail.
*   **Freemium Lite Tools**: The Freemium edition includes toggleable, limited versions of all premium features for previewing.

### AI Security Tiering System
All editions include AI-powered security with progressive capabilities, from basic heuristics in Freemium to full XDR and ML-powered threat intelligence in Server and AI Developer editions, configured via `tier-security.json` and `aegis_ai_security.py`.

## External Dependencies

### Build System Dependencies
*   **Buildroot**: Embedded Linux build system.
*   **Linux Build Tools**: GCC, Make, debootstrap, mksquashfs, xorriso, isolinux, squashfs-tools.
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