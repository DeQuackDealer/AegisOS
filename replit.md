# Aegis OS Build System

## Overview

Aegis OS is a conceptual Linux distribution build system with multiple tiered editions, ranging from a free Freemium version to enterprise Server editions. The project consists of two main components:

1. **Build System** - Automated ISO creation using Buildroot for multiple OS editions
2. **Promotional Website** - Flask-based marketing website showcasing features and pricing tiers

The system is designed to demonstrate a tiered software licensing model with different feature sets (Freemium, Basic, Gamer, AI Developer, Server, Workplace) and includes obfuscation tools for code protection.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Build System Architecture

**Core Technology**: Buildroot-based Linux compilation system

The build system uses Python scripts to orchestrate the creation of bootable ISO images:

- **build-aegis.sh** - Main launcher script that presents edition choices and triggers builds
- **build-replit.py** - Replit-optimized build orchestrator that manages the compilation process
- **obfuscate.py** - Code protection tool using base64 encoding and variable name randomization
- **deploy.py** - Deployment pipeline that obfuscates, builds, and packages the OS

**Design Pattern**: Multi-stage build pipeline
1. Source code obfuscation (protection layer)
2. Buildroot compilation (OS generation)
3. Filesystem image creation
4. ISO packaging and distribution

**Build Outputs**: 
- Kernel modules (aegis_lkm.c)
- Filesystem overlays (custom configurations per tier)
- Bootable ISO images

**Testing**: test-simulation.py validates Buildroot configurations and component availability

### Promotional Website Architecture

**Framework**: Flask (Python web framework)

**Server Files**:
- **server.py** - Production server with enterprise-grade security features
- **server-secure.py** - Hardened version with additional security middleware

**Security Features**:
- Rate limiting with IP-based tracking
- Security headers (CSP, HSTS, X-Frame-Options, etc.)
- JWT-based authentication
- CSRF token protection
- Audit logging with cryptographic signatures
- Failed login attempt tracking

**Commercial Terms (Legal Protection)**:
- "Sold as-is without implied warranties" - standard commercial software terms
- "Liability limited to purchase price" - caps legal exposure
- "Support available separately" - no bundled support promises, optional paid support
- "Based on Linux Lite 7.2 (GPL)" - proper third-party attribution
- 30-day money-back guarantee on paid editions

**API Design**: RESTful endpoints for:
- License management
- System health monitoring
- Analytics and metrics
- User authentication

**Tier System**: Six editions with different feature sets and pricing stored in TIER_FEATURES.json

**Frontend**: Static HTML pages with inline CSS, Windows 10-inspired design aesthetic

**Legal Compliance**: Multiple scripts (apply_legal_updates.py, fix_html_files.py, process_all_html.py) ensure legal disclaimers are present and admin links are removed from public-facing pages

### Directory Structure

```
aegis-os-freemium/     - Freemium edition build system
aegis-promotional/     - Marketing website and server
  ├── html/            - Static HTML pages
  ├── css/             - Stylesheets
  ├── downloads/       - Build guides and documentation
  └── server.py        - Flask application
```

## External Dependencies

### Build System Dependencies

**Linux Build Tools**:
- Buildroot - Embedded Linux build system
- GCC/Make - Compilation toolchain
- Python 3 - Build orchestration scripts

**System Requirements**:
- Ubuntu 20.04+ or Debian 11+
- 20-30GB disk space
- 8-16GB RAM

### Web Server Dependencies

**Python Packages**:
- Flask - Web framework
- PyJWT - JWT token handling (implied by code)

**Security Libraries**:
- hashlib (standard library) - Cryptographic hashing
- hmac (standard library) - Message authentication
- secrets (standard library) - Secure token generation

**Data Formats**:
- JSON - Tier configuration and API responses
- Markdown - Documentation

### Third-Party Services (Conceptual)

The promotional website references but does not implement:
- Payment processing (pricing tiers defined)
- License validation systems
- Cloud backup services
- Analytics platforms

**Note**: Aegis OS is a commercial Linux distribution based on Linux Lite 7.2. The installers download the real Linux Lite ISO (~2.1GB) and create actual bootable USB drives using raw disk writes (dd-style). Stripe integration handles real payments.

### Design Decisions

**Build System Choice**: Buildroot was chosen for creating minimal, customized Linux distributions with precise control over package selection and kernel configuration.

**Obfuscation Strategy**: Base64 encoding and variable renaming provide basic code protection while maintaining Python executability. This is suitable for demonstration purposes but not cryptographically secure.

**Flask for Web**: Lightweight framework chosen for simplicity and rapid development of the promotional site. Security features were added incrementally through middleware layers.

**Tier-Based Architecture**: JSON configuration file (TIER_FEATURES.json) separates business logic from code, making it easy to modify pricing and features without changing the application.

**Static HTML with Inline Styles**: Reduces HTTP requests and simplifies deployment, though at the cost of maintainability. Chosen for performance on the promotional site.

### Cross-Platform GUI Installers

**Windows Installers** (HTA - HTML Application):
- **aegis-installer-freemium.hta** - Freemium edition with cyan/green theme
- **aegis-installer-licensed.hta** - Premium editions with gold theme (requires license key)

**macOS/Linux Installers** (Shell scripts with TUI):
- **aegis-installer-freemium.sh** - Terminal-based GUI for free edition
- **aegis-installer-licensed.sh** - Premium installer with license validation

**Windows Features**:
- Modern glassmorphism UI with animated SVG shield logo
- Step indicators (Step 1 of 4) with visual progress dots
- USB drive detection via Windows WMI
- Animated progress bars with shimmer effects
- "What's Included" feature cards
- License key validation with edition detection

**macOS/Linux Features**:
- ASCII art branding with color theming
- USB drive detection via diskutil (macOS) or lsblk (Linux)
- Progress bars with Unicode block characters
- Same step-by-step flow as Windows version
- Edition-specific feature lists

**Endpoints**:
- `/download-installer` or `/download-installer-freemium.hta` - Windows Freemium
- `/download-installer-licensed.hta` - Windows Licensed
- `/download-installer-freemium.sh` or `/download-installer-mac` - macOS/Linux Freemium
- `/download-installer-licensed.sh` - macOS/Linux Licensed

**Note**: HTA files run natively on Windows 7/8/10/11. Shell scripts require `chmod +x` before running on macOS/Linux.

### Payment & License System

**Database Models** (models.py):
- User: accounts with email, password hash, Stripe customer ID
- License: license keys with edition, type (annual/lifetime), status, Stripe session ID
- StripeEvent: webhook event tracking for idempotency
- EmailLog: transactional email tracking

**License Key Generation**:
- Edition-specific prefixes: BSIC (Basic), WORK (Workplace), GAME (Gamer), AIDV (AI Developer), GMAI (Gamer+AI), SERV (Server)
- Format: PREFIX-XXXX-XXXX-XXXX with checksum validation (sum % 7 == 0)

**Payment Flow**:
1. Stripe checkout creates session with tier metadata
2. On success page: verify payment, generate license key
3. Create/find user in database, save license
4. Send confirmation email via SendGrid (if API key configured)

**SendGrid Integration**: 
- Requires SENDGRID_API_KEY secret to enable email functionality
- SENDGRID_FROM_EMAIL defaults to riley.liang@hotmail.com
- Sends purchase confirmation with license key, invoice details, next steps

### Aegis Exclusive Tools (16 Total per Edition)

All editions include 16 custom Aegis-branded Python utilities located in `/usr/local/bin/`:

**System Utilities**:
- `aegis-system-monitor` - Real-time system resource monitoring (CPU, RAM, disk, network)
- `aegis-system-info` - Hardware detection and system information display
- `aegis-vm-optimizer` - Virtual machine performance tuning
- `aegis-kernel-interface` - Kernel parameter configuration

**Desktop Customization**:
- `aegis-desktop-effects` - Window compositing and transparency effects
- `aegis-wallpaper-engine` - Animated wallpaper support
- `aegis-taskbar-manager` - Taskbar layout and behavior customization

**Security & Backup** (NEW):
- `aegis-security-center` - All-in-one security dashboard with ClamAV/UFW integration
- `aegis-backup-pro` - Scheduled rsync-based backup system with incremental snapshots

**App Management** (NEW):
- `aegis-app-store` - Curated marketplace with 62 apps, apt/flatpak installation
- `aegis-game-library` - Unified game launcher (Steam, Lutris, Heroic, native)

**Device Integration** (NEW):
- `aegis-mobile-link` - Phone integration with notifications, file transfer, KDE Connect
- `aegis-desklink` - Multi-computer mouse/keyboard sharing (Barrier/Synergy compatible)

**Graphics & Gaming**:
- `aegis-gaming-optimizer` - Game performance tuning (GameMode integration)
- `aegis-nvidia-info` - NVIDIA GPU monitoring and fan control
- `aegis-nouveau-optimizer` - Open-source driver optimization

**Core**:
- `aegis-welcome` - First-run experience and quick settings
- `aegis-license-manager` - License activation and validation

All tools support:
- Both GUI (tkinter) and CLI modes
- Configuration in `/etc/aegis/`
- Logging to `/var/log/aegis/`
- Graceful degradation when dependencies missing