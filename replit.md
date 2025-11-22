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

**Note**: This is a demonstration/promotional project. The referenced features, pricing, and integrations are conceptual and not connected to actual services.

### Design Decisions

**Build System Choice**: Buildroot was chosen for creating minimal, customized Linux distributions with precise control over package selection and kernel configuration.

**Obfuscation Strategy**: Base64 encoding and variable renaming provide basic code protection while maintaining Python executability. This is suitable for demonstration purposes but not cryptographically secure.

**Flask for Web**: Lightweight framework chosen for simplicity and rapid development of the promotional site. Security features were added incrementally through middleware layers.

**Tier-Based Architecture**: JSON configuration file (TIER_FEATURES.json) separates business logic from code, making it easy to modify pricing and features without changing the application.

**Static HTML with Inline Styles**: Reduces HTTP requests and simplifies deployment, though at the cost of maintainability. Chosen for performance on the promotional site.