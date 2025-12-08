# Aegis OS RSA Key Management

## Overview

Aegis OS uses RSA-2048 digital signatures for license verification. This ensures licenses cannot be forged or tampered with, enabling 100% offline verification in installers.

## Key Pair Components

| File | Purpose | Storage |
|------|---------|---------|
| `aegis-private.pem` | Signs licenses | **NEVER in repo** - secure offline storage only |
| `aegis-public.pem` | Verifies signatures | Embedded in installers, safe to distribute |

## Generating a New Key Pair

### Prerequisites
```bash
pip install cryptography
```

### Generate Keys
```bash
python generate-keys.py
```

This creates:
- `aegis-private.pem` - Private key for signing (SECURE THIS!)
- `aegis-public.pem` - Public key for verification

### Securing the Private Key

**CRITICAL: The private key must NEVER be:**
- Committed to version control
- Stored on networked computers
- Shared via email or messaging

**Recommended storage:**
1. Hardware security module (HSM) for production
2. Air-gapped computer for signing operations
3. Encrypted USB drive stored in secure location
4. Multiple encrypted backups in separate physical locations

## License Signing Process

### Sign a New License
```bash
python sign-license.py \
    --edition basic \
    --license-key "BSIC-ABCD-1234-EFGH" \
    --email "customer@example.com" \
    --expiry "2099-12-31" \
    --private-key aegis-private.pem \
    --output customer-license.json
```

### License Format
```json
{
    "license_key": "BSIC-ABCD-1234-EFGH",
    "edition": "basic",
    "customer_email": "customer@example.com",
    "issued_date": "2025-01-01",
    "expiry_date": "2099-12-31",
    "signature": "base64_encoded_rsa_signature"
}
```

### Available Editions
| Edition | Prefix | Description |
|---------|--------|-------------|
| basic | BSIC | Basic Edition |
| workplace | WORK | Workplace Edition |
| gamer | GAME | Gamer Edition |
| aidev | AIDV | AI Developer Edition |
| gamer_ai | GMAI | Gamer + AI Edition |
| server | SERV | Server Edition |

## Embedding Public Key in Installers

The public key is embedded directly in the installer Python code:

```python
RSA_PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
<paste contents of aegis-public.pem>
-----END PUBLIC KEY-----"""
```

Update this in:
- `build-system/installers/aegis-installer-licensed.py`

## Verification Algorithm

The installer verifies licenses using:
1. **Algorithm**: RSA-2048 with PKCS#1 v1.5 padding
2. **Hash**: SHA-256
3. **Data signed**: JSON string with sorted keys, no spaces

Verification code:
```python
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

signature_data = {
    "license_key": license_data["license_key"],
    "edition": license_data["edition"],
    "customer_email": license_data.get("customer_email", ""),
    "issued_date": license_data.get("issued_date", ""),
    "expiry_date": license_data.get("expiry_date")
}
data_to_verify = json.dumps(signature_data, sort_keys=True, separators=(',', ':'))

public_key.verify(
    signature,
    data_to_verify.encode('utf-8'),
    padding.PKCS1v15(),
    hashes.SHA256()
)
```

## Rotating Keys

When rotating to a new key pair:

1. Generate new key pair with `generate-keys.py`
2. Securely store new private key
3. Update public key in all installers
4. New licenses signed with new private key
5. Old licenses remain valid until expiry (old installers still verify them)

## Security Considerations

- Keep private key offline when not signing
- Use separate development and production key pairs
- The `aegis-public.pem.test` in this repo is for TESTING ONLY
- Regenerate production keys and NEVER commit the private key
