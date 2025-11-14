# Aegis OS - Quick Start Guide

Get up and running with Aegis OS in 5 minutes!

## 🚀 What You Have

This project contains a complete demonstration of Aegis OS:
- **License Server** (Flask API) - Already running!
- **License Client** (Python) - Ready to test
- **Kernel Module** (C stub) - Architecture demonstration
- **Promotional Website** (HTML/CSS/JS) - Marketing materials

## 📁 Project Organization

```
aegis-os-core/          ← ACTUAL OS COMPONENTS
├── license-server/     ← Flask REST API
├── license-client/     ← Python activation client  
└── kernel-module/      ← C kernel module

aegis-promotional/      ← MARKETING WEBSITE
├── html/               ← 6 edition pages
├── css/                ← Windows 10 styling
└── js/                 ← Interactivity
```

## ✅ Quick Test (3 steps)

### 1. Verify License Server
The server is already running! Test it:
```bash
curl http://localhost:5000/health
```

Expected output:
```json
{
  "status": "healthy",
  "service": "Aegis License Server",
  "version": "1.0.0"
}
```

### 2. Activate a License
```bash
cd aegis-os-core/license-client
python3 aegis_license_client.py AEGIS-GAMER-2024-ACTIVE --test
```

You should see:
```
[SUCCESS] License activated for tier: gamer
[SUCCESS] Token written to ./aegis_auth.token
[SUCCESS] License validation complete!
```

### 3. Check the Token
```bash
cat aegis_auth.token
```

You'll see a JWT token like:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🎮 Test License Keys

Try these license keys:

| License Key | Tier | Status | Price |
|------------|------|--------|-------|
| `AEGIS-TEST-FREE` | Freemium | Active | FREE |
| `AEGIS-BASIC-2024-ACTIVE` | Basic | Active | $49/year |
| `AEGIS-GAMER-2024-ACTIVE` | Gamer | Active | $99/year |
| `AEGIS-AI-2024-ACTIVE` | AI Dev | Active | $149/year |
| `AEGIS-SERVER-2024-ACTIVE` | Server | Active | $199/year |
| `AEGIS-BASIC-2024-EXPIRED` | Basic | Expired | Test only |

## 🌐 View the Website

Open any of these files in your browser:
- `aegis-promotional/html/index.html` - Main landing page
- `aegis-promotional/html/gamer.html` - Gaming edition
- `aegis-promotional/html/server.html` - Server edition (terminal UI!)

Or serve them locally:
```bash
cd aegis-promotional/html
python3 -m http.server 8080
```

Then visit: `http://localhost:8080/index.html`

## 🔧 How It Works

```
1. Client generates hardware ID
   ↓
2. Client sends license key + hardware ID to server
   ↓
3. Server validates and issues JWT token (60 min expiry)
   ↓
4. Token written to /etc/aegis/auth.token (or local fallback)
   ↓
5. Kernel module reads token and activates features
```

## 🛡️ Security Features

- ✅ Hardware ID binding (prevents license sharing)
- ✅ JWT with expiration (60-minute tokens)
- ✅ Cryptographic signing (SESSION_SECRET)
- ✅ Anti-spoofing validation
- ✅ One-time hardware activation

## 📚 Learn More

- **Full Documentation**: See `README.md`
- **Core Components**: See `aegis-os-core/README.md`
- **Website Details**: See `aegis-promotional/README.md`

## 🔍 API Endpoints

The license server provides:

**GET /**
```bash
curl http://localhost:5000/
```
Returns API information

**POST /activate**
```bash
curl -X POST http://localhost:5000/activate \
  -H "Content-Type: application/json" \
  -d '{"license_key": "AEGIS-GAMER-2024-ACTIVE", "hardware_id": "TEST-HWID-Aegis123"}'
```

**POST /check_status**
```bash
curl -X POST http://localhost:5000/check_status \
  -H "Content-Type: application/json" \
  -d '{"license_key": "AEGIS-GAMER-2024-ACTIVE", "hardware_id": "TEST-HWID-Aegis123"}'
```

## 🎯 What Each Edition Does

### Freemium (FREE)
- Basic Aegis OS
- Proton/Wine support
- Community support

### Basic ($49/year)
- Priority security updates
- Email support
- License required

### Gamer ($99/year)
- AI game optimization
- Frame rate boost
- P2P network tuning
- Low-latency mode

### AI Developer ($149/year)
- Pre-configured Docker
- GPU acceleration
- ML frameworks (TensorFlow, PyTorch)
- Container optimization

### Server ($199/year)
- AI server acceleration
- Multi-tenant isolation
- Rebootless patching
- 24/7 support

## 🚨 Common Issues

**"Connection failed"**
→ Make sure the license server is running (it should auto-start)

**"Permission denied"**
→ Files automatically fall back to local directory (this is normal)

**"Hardware mismatch"**
→ License is bound to a different hardware ID (anti-spoofing works!)

**"License expired"**
→ Try using `AEGIS-GAMER-2024-ACTIVE` instead

## 💡 Next Steps

1. ✅ Test all license tiers
2. ✅ Explore the promotional website
3. ✅ Read the kernel module stub (`aegis-os-core/kernel-module/aegis_lkm_stub.c`)
4. ✅ Check out the server code (`aegis-os-core/license-server/aegis_license_server.py`)

## 🔐 Production Checklist

Before deploying to production:
- [ ] Replace mock database with PostgreSQL
- [ ] Set strong SESSION_SECRET environment variable
- [ ] Enable HTTPS on license server
- [ ] Implement rate limiting
- [ ] Add audit logging
- [ ] Complete JWT validation in kernel module
- [ ] Create license management dashboard

---

**Ready to explore Aegis OS? Start with the Quick Test above!** 🚀
