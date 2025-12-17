# Aegis OS Build System

## Overview
Aegis OS is a commercial Arch Linux-based distribution featuring seven distinct editions (Freemium, Basic, Gamer, AI Developer, Gamer+AI, Server, Workplace) with a tiered software licensing model. The project includes an automated `archiso`-based build system for ISO creation, a Flask-based promotional website, a comprehensive offline installer, and a payment/license management system. It aims to deliver a Windows 10-inspired desktop experience, optimized gaming via Wine/Proton, over 50 custom Python utilities, and AI-powered security features. Aegis OS targets a broad market, from casual users to AI professionals and enterprises.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Build System
The core build system uses `archiso` to create bootable ISOs for all seven editions, each configured with specific Linux kernels and package lists. It features full Aegis branding, including custom `profiledef.sh`, `/etc/os-release` codenames, a Windows 10-themed LightDM greeter, custom Plymouth boot splash, Fastfetch integration, and a pre-configured `aegis` user.

### Promotional Website
A Flask-based marketing website with a Windows 10-inspired static HTML frontend. It includes security features (rate limiting, JWT, CSRF, audit logging) and displays OS editions, features, and pricing from `TIER_FEATURES.json`. The site provides RESTful APIs for license management, monitoring, analytics, and user authentication.

### Installer System
A fully offline, cross-platform Python/tkinter GUI installer, packaged with PyInstaller. It supports both Freemium and licensed installations. ISO integrity is verified via SHA-256 checksums from `manifest.json`, and licensed editions include RSA-2048 signature verification for license files.

### Payment & License System
Manages user accounts, generates unique license keys, processes payments via Stripe, and tracks Stripe events and email logs. License keys are sent via SendGrid. An admin panel supports promotional "free period" modes.

### Auto-Update System
A REST API enables Aegis OS installations to check for and download RSA-signed updates, supporting edition-specific channels (Stable, Priority, Beta, LTS).

### Desktop Environment
Based on XFCE, it provides a Windows 10-inspired user experience with custom GTK themes, an Aegis Theme Manager, Aero Snap, a translucent taskbar, and Windows-compatible keyboard shortcuts.

### Wine/Proton Optimization
Offers high Windows application compatibility through pre-configured Wine/Proton settings and an `Aegis Wine Optimizer` tool for managing optimized prefixes and dependencies.

### Aegis Exclusive Tools
Over 50 custom Python-based utilities (GUI/CLI) are included, with features tiered by OS edition. These tools cover office suites, multimedia, system care, gaming optimization, AI/ML development, and enterprise management. They leverage `pkexec` for privileged operations and secure `subprocess` calls.

### AI Security Tiering System
All editions integrate AI-powered security, from basic heuristics to XDR and ML-driven threat intelligence, configured via `tier-security.json` and `aegis_ai_security.py`.

### Aegis Neural Upscaler (ANU) System
Custom AI upscaling technology for gaming editions, featuring `aegis-upscaler` (GTK3 GUI/CLI with multiple backends) and `aegis-game-launcher` for unified game launching and upscaler injection.

## External Dependencies

*   **archiso**: Arch Linux ISO build system.
*   **Flask**: Python web framework.
*   **PyJWT**: JSON Web Token handling.
*   **SendGrid**: Transactional email service.
*   **Stripe**: Payment processing.
*   **Python 3**: Core language for many components and tools.
*   **tkinter**: Python GUI library.
*   **MPV**: Renderer for wallpaper engine and streaming.
*   **FFmpeg**: Video processing.
*   **ClamAV, UFW**: Security tools.
*   **rsync**: Backup utility.
*   **Steam, Lutris, Heroic**: Game library integrations.
*   **KDE Connect, Barrier/Synergy**: Device linking.
*   **GameMode**: Gaming optimization.
*   **NVIDIA drivers**: Hardware encoding.
*   **AppArmor/Firejail**: Sandboxing.
*   **PipeWire/PulseAudio**: Audio processing.
*   **rclone**: Cloud storage integration.
*   **Ollama, llama.cpp, vLLM, ONNX Runtime**: AI inference backends.
*   **Docker/Podman**: Container management.
*   **Samba, NFS**: Network Attached Storage.