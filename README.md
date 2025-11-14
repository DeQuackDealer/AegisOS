# Aegis OS - Complete Project

Welcome to the Aegis OS project! This repository contains all the components for Aegis OS, a Linux-based operating system designed for gamers, AI developers, and servers.

## Project Structure

```
aegis-os-project/
├── aegis-os-core/          # Core OS components (for actual OS)
│   ├── license-server/     # Flask-based license validation server
│   ├── license-client/     # Python client for license activation
│   └── kernel-module/      # C kernel module stub
│
└── aegis-promotional/      # Promotional website (marketing materials)
    ├── html/               # HTML pages for each edition
    ├── css/                # Windows 10-inspired styling
    ├── js/                 # JavaScript for interactivity
    └── assets/             # Images and media files
```

## Aegis OS Editions

### 1. **Freemium** (FREE)
- No license required
- Basic features and Proton/Wine support
- Community support

### 2. **Basic** ($49/year)
- Priority security updates
- Regular OS updates
- Email support
- License activation required

### 3. **Gamer** ($99/year)
- AI-powered game optimization
- Frame rate enhancement
- P2P network tuning
- Low-latency mode
- License activation required

### 4. **AI Developer** ($149/year)
- Docker pre-configured
- GPU acceleration support
- Container optimization
- ML frameworks included
- License activation required

### 5. **Server** ($199/year)
- AI server acceleration
- Multi-tenant isolation
- High-performance networking
- Rebootless patching
- 24/7 support
- License activation required

## Quick Start

### 1. License Server Setup

The license server manages license activation and JWT token generation.

```bash
cd aegis-os-core/license-server
python3 aegis_license_server.py
```

The server will start on `http://0.0.0.0:5000`

**Available Endpoints:**
- `GET /` - API information
- `GET /health` - Health check
- `POST /activate` - Activate a license key
- `POST /check_status` - Check license status

**Test License Keys:**
- `AEGIS-BASIC-2024-ACTIVE` (Basic tier)
- `AEGIS-GAMER-2024-ACTIVE` (Gamer tier)
- `AEGIS-AI-2024-ACTIVE` (AI tier)
- `AEGIS-SERVER-2024-ACTIVE` (Server tier)
- `AEGIS-BASIC-2024-EXPIRED` (Expired - for testing)
- `AEGIS-TEST-FREE` (Freemium tier)

### 2. License Client Usage

The client activates licenses and communicates with the server.

```bash
cd aegis-os-core/license-client

# Activate a license with test hardware ID
python3 aegis_license_client.py AEGIS-GAMER-2024-ACTIVE --test

# Check existing license status
python3 aegis_license_client.py --check
```

**Features:**
- Hardware ID generation (anti-spoofing)
- Exponential backoff for server communication
- JWT token delivery to kernel module
- License configuration persistence

### 3. Kernel Module

The kernel module stub demonstrates the architecture for reading and validating JWT tokens.

```bash
cd aegis-os-core/kernel-module

# Display module information
make

# Note: Building actual kernel modules requires kernel headers
# This is a demonstration stub showing the architecture
```

### 4. Promotional Website

View the promotional website locally:

```bash
cd aegis-promotional/html

# Open in browser (example using Python's http server)
python3 -m http.server 8080
```

Then visit `http://localhost:8080/index.html`

## Architecture Overview

### License Validation Flow

1. **User activates license** → License client generates hardware ID
2. **Client contacts server** → Server validates license key
3. **Server issues JWT token** → 60-minute expiration, contains tier info
4. **Token written to file** → `/etc/aegis/auth.token` (or local fallback)
5. **Kernel module reads token** → Enables tier-specific features

### Anti-Spoofing Measures

- **Hardware ID binding**: Licenses tied to unique hardware hash
- **JWT expiration**: Tokens expire after 60 minutes
- **Server-side validation**: All checks performed on server
- **Cryptographic signing**: JWT tokens signed with secret key

## API Documentation

### POST /activate

Activate a license key and bind it to a hardware ID.

**Request:**
```json
{
  "license_key": "AEGIS-GAMER-2024-ACTIVE",
  "hardware_id": "abc123def456..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "License activated successfully",
  "tier": "gamer",
  "expiry_date": "2026-06-30",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### POST /check_status

Check license status and get a new JWT token.

**Request:**
```json
{
  "license_key": "AEGIS-GAMER-2024-ACTIVE",
  "hardware_id": "abc123def456..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "License is valid",
  "tier": "gamer",
  "expiry_date": "2026-06-30",
  "status": "ACTIVE",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Development

### Requirements

- Python 3.11+
- Flask
- PyJWT
- requests
- GCC (for kernel module compilation)
- Linux kernel headers (for actual kernel module builds)

### Environment Variables

- `SESSION_SECRET`: Secret key for JWT signing (optional, defaults to demo key)
- `AEGIS_LICENSE_SERVER`: License server URL (default: `http://localhost:5000`)

### Testing

1. Start the license server
2. Run the client with a test license key
3. Check the generated token file
4. Verify kernel module can read the token

## Security Considerations

**For Production:**
- Replace `SESSION_SECRET` with a strong random key
- Use HTTPS for license server
- Implement rate limiting
- Add database persistence (replace mock database)
- Implement full JWT cryptographic validation in kernel module
- Add audit logging
- Implement license transfer controls

## Contributing

This is a demonstration project showing the architecture of a licensed OS system. The code includes:
- ✅ License server with JWT authentication
- ✅ License client with hardware binding
- ✅ Kernel module architecture stub
- ✅ Promotional website with Windows 10 styling
- ⚠️ Mock database (replace with PostgreSQL/MySQL for production)
- ⚠️ Simplified JWT validation in kernel (add full crypto for production)

## License

Aegis OS Core Components: Proprietary License
Promotional Website: For marketing purposes only

## Support

- **Community**: Forums and documentation
- **Basic/Gamer/AI**: Email support
- **Server**: 24/7 support with 4-hour SLA

---

**Copyright © 2024 Aegis OS Development Team. All rights reserved.**
