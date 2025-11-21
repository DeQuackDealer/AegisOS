# Aegis OS Basic Edition

**$49/year** - Security & support included

## 🔒 What's New in Basic

- **Real-time Security Monitoring** - Threat detection 24/7
- **AI Anomaly Detection** - ML-powered intrusion detection
- **Firewall Enabled** - Network protection
- **Priority Security Updates** - Patches within 48 hours
- **Email Support** - Direct assistance
- **File Integrity Checking** - Monitor for unauthorized changes

## 🛠️ Building

```bash
chmod +x build.sh post-build.sh
./build.sh
```

**Output**: `output/aegis-os-basic.iso` (bootable, ~2.5GB)

## 📥 Installation

1. Download Balena Etcher: https://balena.io/etcher
2. Flash `aegis-os-basic.iso` to USB 8GB+
3. Boot from USB
4. Auto-login as `aegis`
5. Activate license: `aegis-cli activate --key YOUR-KEY`

## 🔐 Security Features

| Feature | Freemium | Basic |
|---------|----------|-------|
| Security Scanner | ❌ | ✓ |
| AI Threat Detection | ❌ | ✓ |
| Firewall | ❌ | ✓ |
| File Integrity | ❌ | ✓ |
| Priority Updates | ❌ | ✓ |
| Email Support | ❌ | ✓ |

## 🚀 Running Security Scan

```bash
sudo aegis-security scan

# Output:
# ✓ File Integrity Scan
# ✓ AI Threat Detection
# ✓ Firewall Status
# ✓ Process Analysis
# ✓ System Updates
```

## 📖 Documentation

See `BASIC_EDITION.md` for complete guide.
