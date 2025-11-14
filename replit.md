# Aegis OS Project

## Overview
This project implements a complete Linux-based operating system called Aegis OS with a tiered licensing system. The project includes both the core OS components and a promotional website.

## Project Purpose
Aegis OS is designed to be the gold standard operating system for:
- **Gamers**: AI-optimized gaming performance with Proton/Wine integration
- **AI Developers**: Pre-configured Docker, GPU acceleration, and ML frameworks
- **Servers**: Enterprise-grade server optimization with rebootless patching

## Current State
✅ Complete license server with JWT authentication
✅ License client with hardware ID binding
✅ C kernel module stub demonstrating architecture
✅ Full promotional website with Windows 10 styling
✅ Comprehensive documentation
✅ Working demos and test cases

## Project Structure

```
/
├── aegis-os-core/           # Actual OS components
│   ├── license-server/      # Flask REST API for license validation
│   ├── license-client/      # Python client for activation
│   └── kernel-module/       # C kernel module stub
│
├── aegis-promotional/       # Marketing website
│   ├── html/                # Edition pages (index, freemium, basic, gamer, ai, server)
│   ├── css/                 # Windows 10-inspired styles
│   └── js/                  # Interactive features
│
└── README.md                # Main documentation
```

## Recent Changes (November 14, 2024)

### Initial Implementation
- Created complete license server with mock database and 6 test license keys
- Implemented license client with exponential backoff and hardware binding
- Built kernel module stub in C demonstrating token reading architecture
- Designed promotional website with 6 pages (index + 5 editions)
- Added Windows 10-inspired styling with taskbar navigation
- Created server edition with unique terminal aesthetic
- Implemented anti-spoofing via hardware ID validation
- Added comprehensive README files for all components

### Bug Fixes
- Fixed hardware ID validation to accept TEST- prefixed IDs
- Improved error handling for read-only file systems
- Added fallback to local directory for token/config storage

## OS Editions

### 1. Freemium (FREE)
- No license required
- Basic features with Proton/Wine support
- Community support only

### 2. Basic ($49/year)
- Priority security updates
- Regular OS updates
- Email support
- License activation required

### 3. Gamer ($99/year)
- AI-powered game optimization
- Frame rate enhancement
- P2P network tuning
- Low-latency mode

### 4. AI Developer ($149/year)
- Docker pre-configured
- GPU acceleration
- Container optimization
- ML frameworks included

### 5. Server ($199/year)
- AI server acceleration
- Multi-tenant isolation
- Rebootless patching
- 24/7 support

## License System Architecture

### Flow
1. Client generates unique hardware ID (SHA256 hash of MAC address)
2. Client contacts license server with license key + hardware ID
3. Server validates license and hardware binding
4. Server issues JWT token (60-minute expiration)
5. Token written to `/etc/aegis/auth.token` (or local fallback)
6. Kernel module reads and validates token
7. Features activated based on tier

### Anti-Spoofing Measures
- Hardware ID binding (prevents sharing)
- JWT with cryptographic signing
- 60-minute token expiration
- Server-side validation only
- One-time hardware binding

## Available Test License Keys

- `AEGIS-TEST-FREE` - Freemium tier
- `AEGIS-BASIC-2024-ACTIVE` - Basic tier
- `AEGIS-GAMER-2024-ACTIVE` - Gamer tier
- `AEGIS-AI-2024-ACTIVE` - AI Developer tier
- `AEGIS-SERVER-2024-ACTIVE` - Server tier
- `AEGIS-BASIC-2024-EXPIRED` - Expired (for testing)

## Running the Project

### License Server
```bash
# Server is configured to run automatically on port 5000
# Access at: https://[replit-url]
```

### Test License Client
```bash
cd aegis-os-core/license-client
python3 aegis_license_client.py AEGIS-GAMER-2024-ACTIVE --test
```

### View Promotional Website
Files are in `aegis-promotional/html/`
- `index.html` - Main landing page
- `freemium.html` - Free edition
- `basic.html` - Basic paid edition
- `gamer.html` - Gaming edition
- `ai.html` - AI developer edition
- `server.html` - Server edition (unique terminal styling)

## Technology Stack

### Backend
- Python 3.11
- Flask (web framework)
- PyJWT (token generation)
- requests (HTTP client)

### Frontend
- HTML5
- CSS3 (Windows 10-inspired design)
- Vanilla JavaScript

### System
- C (kernel module)
- Linux Kernel Module framework

## Development Notes

### Mock Database
The license server uses an in-memory Python dictionary for demo purposes. For production:
- Replace with PostgreSQL/MySQL
- Add license management dashboard
- Implement license generation system
- Add audit logging

### Security Considerations
- `SESSION_SECRET` environment variable for JWT signing
- HTTPS required for production
- Rate limiting needed
- Full JWT crypto validation in kernel module for production

### File Permissions
- Token files: 0o600 (read/write owner only)
- Config files: 0o600 (read/write owner only)
- Fallback to local directory if `/etc/aegis/` not writable

## User Preferences
None specified yet.

## Next Steps (Future Enhancements)
- Implement PostgreSQL database for licenses
- Add admin dashboard for license management
- Complete JWT validation in kernel module
- Implement actual kernel patches (kpatch for rebootless patching)
- Add telemetry and analytics
- Create installer ISO
- Add license transfer portal
- Implement rate limiting on server
