# Aegis OS Core Components

This directory contains the actual OS components for Aegis OS.

## Components

### 1. License Server (`license-server/`)

Flask-based REST API server for license validation and JWT token issuance.

**Files:**
- `aegis_license_server.py` - Main server application

**Features:**
- License activation with hardware binding
- JWT token generation
- Anti-spoofing protection
- Mock database for testing

**Running:**
```bash
cd license-server
python3 aegis_license_server.py
```

### 2. License Client (`license-client/`)

Python client application that runs on Aegis OS machines.

**Files:**
- `aegis_license_client.py` - Client application

**Features:**
- Hardware ID generation
- Server communication with exponential backoff
- Token delivery to kernel module
- Configuration persistence

**Usage:**
```bash
cd license-client
python3 aegis_license_client.py AEGIS-GAMER-2024-ACTIVE --test
```

### 3. Kernel Module (`kernel-module/`)

Loadable kernel module stub for reading and validating JWT tokens.

**Files:**
- `aegis_lkm_stub.c` - Kernel module source
- `Makefile` - Build configuration

**Features:**
- Token file reading from `/etc/aegis/auth.token`
- Stub validation logic
- Feature activation based on tier
- Module metadata (Proprietary license)

**Note:** This is a demonstration stub. Production kernels would include full cryptographic JWT validation.

## License Tiers and Features

### Freemium
- No kernel module activation needed
- Basic OS features only

### Basic ($49/year)
- Priority security updates
- Kernel module validates "basic" tier

### Gamer ($99/year)
- Gaming optimizations enabled
- AI-powered frame optimization
- P2P network tuning

### AI Developer ($149/year)
- Container optimization
- GPU resource management
- Docker integration

### Server ($199/year)
- Rebootless patching (kpatch)
- Multi-tenant isolation
- High-performance networking
- AI server acceleration

## Integration Flow

```
User Machine                License Server
    |                            |
    | 1. Generate Hardware ID    |
    |--------------------------->|
    |                            |
    | 2. Request License Check   |
    |--------------------------->|
    |                            | 3. Validate License
    |                            | 4. Generate JWT
    |<---------------------------|
    | 5. Receive JWT Token       |
    |                            |
    | 6. Write to /etc/aegis/auth.token
    |
    | 7. Kernel Module Reads Token
    |
    | 8. Features Activated
```

## Security Features

1. **Hardware Binding**: Prevents license sharing
2. **JWT Expiration**: 60-minute token validity
3. **Anti-Spoofing**: Hardware ID validation
4. **Cryptographic Signing**: JWT tokens are signed
5. **One-Time Activation**: License tied to first hardware

## Development Notes

- Use test mode (`--test` flag) for development
- Mock database includes sample licenses
- Token files fall back to local directory if `/etc/aegis/` is not writable
- Production deployments should use PostgreSQL for license storage

## Production Checklist

- [ ] Replace mock database with PostgreSQL
- [ ] Configure strong SESSION_SECRET
- [ ] Enable HTTPS for license server
- [ ] Implement rate limiting
- [ ] Add audit logging
- [ ] Deploy kernel module with full JWT crypto validation
- [ ] Set up license management dashboard
- [ ] Configure backup and recovery
- [ ] Enable monitoring and alerting
