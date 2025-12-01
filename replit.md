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

### RSA License Signing System (December 2025)

The licensed installer uses RSA-2048 asymmetric cryptography to prevent license forgery:

**Security Model:**
- **Private Key**: Stored as `LICENSE_SIGNING_PRIVATE_KEY` secret (PEM format)
- **Public Key**: Embedded in HTA installer as base64-encoded XML (PowerShell 5 compatible)
- **Signatures**: RSA-SHA256 for each license entry and cache integrity
- **Hash Function**: Two-part hash combining h=((h*31)+c)&0x7FFFFFFF and r=((r^c)*17)&0xFFFF

**PowerShell 5 Compatibility (Critical):**
- Uses XML format `<RSAKeyValue><Modulus>...</Modulus><Exponent>...</Exponent></RSAKeyValue>`
- This format works with `FromXmlString()` in PowerShell 5 (standard on Windows 10/11)
- Previous DER format (`ImportSubjectPublicKeyInfo`) required PowerShell 7+ which most users don't have
- **Important:** Modulus bytes must have a leading 0x00 if high bit is set (otherwise .NET treats it as negative)

**Fail-Closed Design:**
- Server returns HTTP 503 if private key not configured (no unsigned installers generated)
- HTA rejects validation if public key is placeholder (no bypass for unsigned builds)
- All validation functions default to False and require valid RSA signatures

**Operational Procedures:**
1. Generate RSA-2048 key pair (private key in PEM format)
2. Set `LICENSE_SIGNING_PRIVATE_KEY` secret with private key contents
3. Server automatically derives public key and embeds in installers (XML format)
4. HTA uses PowerShell .NET crypto (RSACryptoServiceProvider.FromXmlString) for offline RSA verification

**Key Rotation:**
1. Generate new RSA-2048 key pair
2. Update `LICENSE_SIGNING_PRIVATE_KEY` secret
3. All new installer downloads will contain new public key
4. Existing installers continue working until user re-downloads

**Demo Licenses (for testing):**
- BSIC-DEMO-TEST-2024 (Basic)
- WORK-DEMO-TEST-2024 (Workplace)
- GAME-DEMO-TEST-2024 (Gamer)
- AIDV-DEMO-TEST-2024 (AI Developer)
- GMAI-DEMO-TEST-2024 (Gamer+AI)
- SERV-DEMO-TEST-2024 (Server)

### Free Period & No-License Installers (December 2025)

**Free Period Mode:**
The admin panel can enable "free mode" where all editions are available without license validation. This bypasses the license system temporarily for promotions or while license issues are being fixed.

- **Admin Endpoints:**
  - `GET /api/admin/free-period` - View free period status
  - `POST /api/admin/free-period` - Enable/configure free period
  - `DELETE /api/admin/free-period` - Disable free period

- **Public Endpoints (during free period):**
  - `GET /api/free/editions` - List available free editions
  - `GET /api/free/download/{edition}` - Download edition HTA (rate limited)

**Rate Limiting (Anti-Bot):**
- 5 downloads per IP per hour
- 10 downloads per IP per day
- HTTP 429 returned when limit exceeded

**Edition-Specific HTAs (No License Validation):**
Located in `build-system/editions/`:
- `aegis-installer-basic.hta` - Basic edition
- `aegis-installer-workplace.hta` - Workplace edition
- `aegis-installer-gamer.hta` - Gamer edition
- `aegis-installer-aidev.hta` - AI Developer edition
- `aegis-installer-gamer-ai.hta` - Gamer+AI edition
- `aegis-installer-server.hta` - Server edition (admin-only)

These HTAs are pre-configured for their specific edition and skip the license validation step entirely.

### Auto-Update System (December 2025)

The server provides a REST API for Aegis OS installations to check for updates. Works with both Freemium (no license) and paid editions (with license key).

**API Endpoints:**

1. **GET/POST /api/v1/updates/check** - Check for available updates
   - Query params: `license_key`, `current_version`, `hardware_id`, `edition`
   - Returns: `update_available`, `latest_version`, `changelog`, `download_url`, `features`
   - Response is RSA-signed for verification

2. **GET /api/v1/updates/changelog** - Get full version changelog

3. **GET /api/v1/updates/download-info** - Get ISO download URLs and checksums
   - Query params: `license_key` (optional)
   - Returns mirror URLs, SHA256 checksum, installer type

**Edition-Specific Features:**
- Freemium: Stable channel, manual updates only
- Basic/Workplace: Priority updates, auto-update enabled
- Gamer/AI Developer/Gamer+AI: Beta channel access, early access features
- Server: LTS channel, priority patches

**Client Integration:**
- `aegis-update-manager` tool reads server URL from `/etc/aegis/update-config.json`
- License key stored in `/etc/aegis/license.json`
- Current version from `/etc/aegis/version`

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

### AI Security Tiering System

All editions include AI-powered security with progressive capabilities:
- **Freemium**: Basic heuristics, signature-based scanning
- **Basic**: + Real-time file monitoring, process scanning
- **Gamer/Workplace**: + Behavioral AI analysis, anomaly detection
- **AI Developer**: + ML-powered threat intelligence, model-based detection
- **Server**: Full XDR (Extended Detection & Response), eBPF monitoring, zero-trust enforcement, SIEM integration

Configuration files: `tier-security.json` per edition, `aegis_ai_security.py` module with edition-specific `TIER_LIMIT` values.

### Freemium Lite Tools

Freemium edition includes toggleable lite versions of premium features:
- **aegis-gaming-optimizer-lite**: Basic game detection, simple performance mode (no overclocking)
- **aegis-ai-toolkit-lite**: Read-only model browser, basic inference (no training, no downloads)
- **aegis-workplace-lite**: Meeting launcher, view-only remote desktop, expense tracker (10 entries max)
- **aegis-wallpaper-engine-lite**: Static wallpapers only
- **aegis-stream-lite**: 720p30 max, watermark, no audio
- **aegis-security-center-lite**: Basic firewall + AI heuristics (no ClamAV/realtime)
- **aegis-backup-lite**: Manual local backup only (no scheduling, no cloud)

**Tier Limitations (Freemium vs Full):**
- security-center: Basic firewall + AI heuristics vs full ClamAV/UFW + behavioral AI
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