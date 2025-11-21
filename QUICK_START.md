# Aegis OS - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Option 1: Download ISO (No Build Needed)
```bash
# 1. Download Balena Etcher
Visit: https://balena.io/etcher

# 2. Download ISO from website
Visit: http://localhost:5000/download/iso

# 3. Flash to USB
- Open Etcher
- Select ISO
- Select USB drive
- Click Flash

# 4. Boot
- Insert USB
- Boot from USB
- Login: aegis / password
```

### Option 2: Build Your Own ISO
```bash
# 1. On Linux machine (Ubuntu/Debian):
sudo apt-get install build-essential wget cpio unzip rsync bc libncurses5-dev

# 2. Download build scripts
git clone https://github.com/aegis-os/os-builds.git
cd aegis-os-freemium

# 3. Build (takes 90-120 minutes)
chmod +x build.sh post-build.sh
./build.sh

# 4. Find ISO
ls output/aegis-os-freemium.iso
```

---

## 📦 Using APIs

### Python Example
```python
from aegis import AegisClient

client = AegisClient(
    api_key='your-api-key',
    user_id='your-user-id'
)

# Register user
user = client.register('user@example.com', 'password123')

# Validate license
license = client.validate_license('AEGIS-BASIC-2024-XXXXX')

# Get tier details
tier = client.get_tier('basic')
print(f"Price: ${tier['price']}")

# Check security status
security = client.check_security()
print(f"Threat Level: {security['threat_level']}")

# Schedule backup
backup = client.schedule_backup('daily', retention_days=30)
```

### JavaScript Example
```javascript
const { AegisClient } = require('aegis-os-sdk');

const client = new AegisClient({
    apiKey: 'your-api-key',
    userId: 'your-user-id'
});

// Register user
const user = await client.register('user@example.com', 'password123');

// Validate license
const license = await client.validateLicense('AEGIS-BASIC-2024-XXXXX');

// Get analytics
const analytics = await client.getAnalytics();
console.log(`Downloads: ${analytics.downloads}`);

// List marketplace apps
const apps = await client.listApps();
apps.forEach(app => {
    console.log(`${app.name}: ${app.downloads} downloads`);
});
```

### cURL Examples
```bash
# Register user
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}'

# Validate license
curl -X POST http://localhost:5000/api/v1/license/validate \
  -H "Content-Type: application/json" \
  -d '{"key":"AEGIS-BASIC-2024-XXXXX"}'

# Get all tiers
curl http://localhost:5000/api/v1/tiers

# Check security
curl http://localhost:5000/api/v1/security/check

# Get system health
curl http://localhost:5000/api/v1/system/health
```

---

## 🔑 Managing Licenses

### Activate License
```bash
aegis-cli activate --key AEGIS-BASIC-2024-XXXXX
```

### Check Status
```bash
aegis-cli status
```

### Run Security Scan
```bash
aegis-cli security scan
```

### Enable 2FA
```bash
aegis-cli user 2fa enable
```

---

## 🔒 Security Features

### For Paid Tiers (Basic+):
- ✅ Real-time security monitoring
- ✅ AI threat detection
- ✅ Firewall protection (UFW)
- ✅ File integrity checking
- ✅ Network intrusion detection
- ✅ Process behavior analysis
- ✅ Priority security updates
- ✅ 24/7 support

### For Freemium:
- ❌ No security features
- ❌ Community support only
- ✅ Base OS included
- ✅ Wine + Proton support

---

## 📊 Admin Dashboard

Access at: `http://localhost:5000/html/admin.html`

Features:
- Real-time metrics
- User management
- License tracking
- Payment history
- System health
- Audit logging

---

## 🛠️ System Management

### Check System Status
```bash
aegis-cli info
```

### Schedule Backups
```bash
# API endpoint
curl -X POST http://localhost:5000/api/v1/backup/schedule \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"schedule":"daily","retention_days":30}'
```

### Install Marketplace Apps
```bash
# Via API
curl -X POST http://localhost:5000/api/v1/marketplace/app/app-001/install \
  -H "X-API-Key: your-key"
```

### View Audit Log
```bash
# API endpoint
curl http://localhost:5000/api/v1/analytics/audit \
  -H "X-API-Key: your-key"
```

---

## 📈 Monitoring & Analytics

```bash
# Get dashboard
curl http://localhost:5000/api/v1/analytics/dashboard \
  -H "X-API-Key: your-key" \
  -H "X-User-ID: your-user-id"

# Response:
{
  "downloads": 10247,
  "activations": 1823,
  "errors": 12,
  "active_users": 1823,
  "uptime_percent": 99.95,
  "avg_response_time_ms": 145
}
```

---

## 🪝 Webhooks

### Register Webhook
```bash
curl -X POST http://localhost:5000/api/v1/webhooks/register \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://yourapp.com/webhook",
    "events": ["payment.completed", "license.activated", "security.threat_detected"]
  }'
```

### List Webhooks
```bash
curl http://localhost:5000/api/v1/webhooks \
  -H "X-API-Key: your-key"
```

### Delete Webhook
```bash
curl -X DELETE http://localhost:5000/api/v1/webhooks/webhook-id \
  -H "X-API-Key: your-key"
```

---

## 🌐 Deployment

### Deploy to Production
```bash
# 1. Get domain
domain="your-domain.com"

# 2. Setup SSL
# Use Let's Encrypt or your SSL provider

# 3. Deploy backend
# Python server with Gunicorn/Nginx

# 4. Configure environment
export AEGIS_API_KEY="production-key"
export DATABASE_URL="your-db-url"

# 5. Run
gunicorn --bind 0.0.0.0:5000 --workers 4 server:app
```

---

## 📞 Support

- **Email**: support@aegis-os.dev
- **Docs**: https://docs.aegis-os.dev
- **GitHub**: https://github.com/aegis-os
- **Forum**: https://forum.aegis-os.dev

---

**Aegis OS v2.0 - Ready to Use!**
