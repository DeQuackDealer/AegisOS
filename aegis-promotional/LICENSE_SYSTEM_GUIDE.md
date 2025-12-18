# Aegis OS Licensing System Documentation

## Overview
Aegis OS uses a comprehensive licensing system that validates licenses on boot and manages feature access based on the user's tier (Freemium, Basic, Gamer, AI Developer, or Server).

## License Types

### 1. Lifetime License
- **One-time payment** for perpetual use
- Never expires
- Bound to hardware ID (optional)
- Format: `AEGIS-XXX-XXXXX-XXXXX-XXXXX`

### 2. Annual Subscription
- **Recurring yearly payment** at lower cost
- Expires after 365 days
- Auto-renewal through Stripe
- Same format as lifetime but with expiration date

## Pricing Structure

| Edition | Lifetime | Annual |
|---------|----------|--------|
| Freemium | FREE | FREE |
| Basic | $19 | $3/year |
| Workplace | $9 | $2/year |
| Gamer | $69 | $10/year |
| AI Developer | $79 | $12/year |
| Gamer + AI | $119 | $17/year |
| Server | Contact | Contact |

## How It Works

### 1. Purchase Flow
```
Customer → Website → Stripe Checkout → Payment → License Generation → Email Delivery
```

### 2. Boot Process
```
OS Boot → License Check → Validate Online/Offline → Apply Features → Start Services
```

### 3. Feature Activation

#### Freemium (No License)
- Basic XFCE desktop
- Open-source Nouveau drivers
- Community support only
- 4GB RAM limit, 2 CPU cores

#### Basic ($19 lifetime / $3 annual)
- Enhanced security suite
- Encrypted storage
- VPN client
- Password manager
- Anti-ransomware
- Email support
- 16GB RAM, 8 CPU cores

#### Gamer ($69 lifetime / $10 annual)
- NVIDIA/AMD proprietary drivers
- Gaming mode optimization
- Ray tracing & DLSS 3
- <5ms input latency
- RGB ecosystem support
- Game optimizer
- 32GB RAM, 16 CPU cores

#### AI Developer ($79 lifetime / $12 annual)
- CUDA 12.3 toolkit
- PyTorch & TensorFlow
- Jupyter Lab
- 100+ ML libraries
- Docker & Kubernetes
- 24/7 support
- 64GB RAM, 32 CPU cores

#### Server (Contact for pricing)
- Enterprise security
- Kubernetes orchestration
- High availability
- Auto-scaling
- 100K+ RPS support
- 24/7 SLA support
- Unlimited resources

## License Validation

### Online Validation (Primary)
The OS connects to `https://aegis-os.com/api/validate-license` on boot to verify:
- License authenticity
- Expiration status (for annual licenses)
- Hardware binding (if enabled)
- Feature entitlements

### Offline Fallback
If no internet connection:
- Uses cached license from `/etc/aegis/license.json`
- Validates signature locally
- Allows 30-day grace period for annual licenses

### Hardware Binding
Licenses can optionally be bound to hardware using:
- Product UUID
- Network MAC address
- CPU identifier hash

## ISO Distribution

### Pre-Licensed ISOs
For volume customers, we can generate ISOs with embedded licenses:
```bash
python3 generate_iso_with_license.py base.iso gamer "AEGIS-GAM-XXXXX-XXXXX-XXXXX" "customer@email.com"
```

### Generic ISOs
Standard downloads prompt for license on first boot:
1. User downloads appropriate tier ISO
2. On first boot, system prompts for license
3. License validated and cached
4. Features activated based on tier

## License Management

### For Customers
- **View License**: Check `/etc/aegis/license.json`
- **Change License**: Run `sudo aegis-license-update`
- **Check Status**: Run `aegis-license-status`

### For Administrators
- **Generate License**: Use admin panel at `/admin`
- **Revoke License**: Update database and sync
- **Transfer License**: Contact support with proof of purchase

## Integration Points

### 1. Website Integration
- Stripe webhook on successful payment
- Automatic license generation
- Email delivery with download link

### 2. OS Integration
- Systemd service: `aegis-license.service`
- Boot script: `/usr/local/bin/aegis-license-check`
- Config location: `/etc/aegis/`

### 3. Feature Gates
Features are controlled via:
- Kernel modules (drivers)
- Systemd services
- Package availability
- Resource limits (cgroups)

## Security

### License Protection
- HMAC-SHA256 signatures
- Encrypted storage of sensitive data
- Rate limiting on validation API
- Hardware fingerprinting

### Anti-Piracy
- Online validation required every 30 days
- Hardware binding for enterprise licenses
- Unique license keys per purchase
- Revocation list for compromised keys

## Troubleshooting

### Common Issues

1. **"Invalid License" on boot**
   - Check internet connection
   - Verify license format
   - Ensure not expired (annual)
   - Contact support if persistent

2. **Features not activating**
   - Run `systemctl status aegis-license`
   - Check `/var/log/aegis_license.log`
   - Verify tier in `/etc/aegis/features.json`

3. **License expired (annual)**
   - Renew through website
   - Update payment method in Stripe
   - System allows 7-day grace period

## API Endpoints

### License Validation
```
POST /api/validate-license
{
  "license_key": "AEGIS-XXX-XXXXX-XXXXX-XXXXX",
  "hardware_id": "optional-hardware-fingerprint"
}

Response:
{
  "valid": true,
  "tier": "gamer",
  "features": {...},
  "expires_at": "2025-11-24T00:00:00Z"  // For annual only
}
```

### License Generation (Admin)
```
POST /api/admin/generate-license
{
  "tier": "gamer",
  "type": "lifetime",
  "email": "customer@email.com",
  "stripe_session_id": "cs_test_..."
}

Response:
{
  "license_key": "AEGIS-GAM-XXXXX-XXXXX-XXXXX",
  "download_url": "https://aegis-os.com/download/...",
  "expires_at": null
}
```

## Support

For license-related issues:
- Email: riley.liang@hotmail.com
- Include: Order ID, License key (first 10 chars), Hardware ID

## Legal

- Licenses are non-transferable without approval
- Refunds available within 30 days
- Annual subscriptions auto-renew
- Enterprise licenses require signed agreement