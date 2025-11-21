# Aegis OS Basic Edition

**$49/year** - Secure & supported with priority updates

## What's Included

### Core Features
- ✓ **Linux 6.6.7** - Stable kernel
- ✓ **XFCE 4.18** - Responsive desktop
- ✓ **Wine 8.21** - Windows compatibility
- ✓ **Proton** - Steam games support
- ✓ **Vulkan & OpenGL** - Graphics support

### Security Features (PAID)
- ✓ **Real-time Security Monitoring** - 24/7 threat detection
- ✓ **AI Threat Detection** - Machine learning-powered anomaly detection
- ✓ **Firewall (UFW)** - Network security
- ✓ **File Integrity Checker** - Detect unauthorized changes
- ✓ **SSL/TLS Support** - Encrypted connections
- ✓ **Permission Hardening** - Secure file permissions
- ✓ **Process Analysis** - Monitor for suspicious activity
- ✓ **Network Security** - Connection monitoring

### Support & Updates
- ✓ **Priority Security Updates** - Patches within 48 hours
- ✓ **Email Support** - Direct assistance
- ✓ **License System** - Activation & validation
- ✓ **System Monitoring** - Performance tracking
- ✓ **Update Notifications** - Stay current

### NOT Included (Freemium Only)
- ❌ Security checker disabled on Freemium
- ❌ AI threat detection not available
- ❌ Firewall monitoring not included
- ❌ Priority support not available

## Running Security Scanner

```bash
# Check license and enable security
aegis-security-checker

# Full security scan (auto-runs daily)
sudo aegis-security scan

# Get security report
sudo aegis-security report

# Enable real-time monitoring
sudo systemctl enable aegis-security-monitor
```

## AI Threat Detection Features

### How It Works
1. **Baseline Learning** - Learns normal system behavior
2. **Pattern Analysis** - Detects anomalies
3. **Threat Scoring** - Rates threat level
4. **Auto-Response** - Can auto-quarantine threats
5. **Reporting** - Detailed threat reports

### Threat Detection Covers
- Suspicious process behavior
- Network intrusions
- File system anomalies
- Memory exploits
- Privilege escalation attempts
- Malware signatures

### Example: Running Scan
```bash
$ sudo aegis-security scan

🔒 Aegis Security Scan Starting...
📋 Tier: BASIC

✓ File Integrity Scan
✓ System Permissions
✓ Network Security
✓ Process Analysis
✓ AI Threat Detection
✓ System Updates
✓ Firewall Status

✅ Security scan complete
Threat Level: LOW
Last Update: Nov 21, 2025
```

## Building Aegis OS Basic

### Requirements
- Linux machine (Ubuntu 20.04+)
- 8GB+ RAM
- 20GB free disk space
- 90-120 minutes

### Quick Build
```bash
cd aegis-os-basic
chmod +x build.sh post-build.sh
./build.sh
```

### Output Files
- `aegis-os-basic.iso` - Bootable ISO
- `aegis-os-basic.ext4` - Filesystem
- `aegis-kernel-basic` - Kernel
- `checksums.txt` - Verification

## Installation on USB

```bash
# 1. Download Balena Etcher
https://balena.io/etcher

# 2. Flash ISO
# Open Etcher → Select aegis-os-basic.iso → Select USB → Flash

# 3. Boot from USB
# Insert USB → Boot → Login as 'aegis'

# 4. Activate License
# Run: aegis-cli activate --key YOUR-LICENSE-KEY
```

## License Activation

```bash
# Test license key
aegis-cli activate --key AEGIS-BASIC-2024-ACTIVE

# Check license status
aegis-cli status

# Verify security features enabled
aegis-security status
```

## First Steps After Install

1. **Boot the system**
   ```bash
   # Auto-login as 'aegis' user
   ```

2. **Activate License**
   ```bash
   aegis-cli activate --key YOUR-LICENSE-KEY
   ```

3. **Enable Security Features**
   ```bash
   sudo systemctl enable aegis-security-monitor
   sudo systemctl start aegis-security-monitor
   ```

4. **Run Initial Security Scan**
   ```bash
   sudo aegis-security scan
   ```

5. **Update System**
   ```bash
   sudo apt-get update
   sudo apt-get upgrade
   ```

## Comparison: Freemium vs Basic

| Feature | Freemium | **Basic** |
|---------|----------|----------|
| Cost | FREE | $49/year |
| Security Scanner | ❌ | ✓ |
| AI Threat Detection | ❌ | ✓ |
| Firewall | ❌ | ✓ |
| File Integrity | ❌ | ✓ |
| Priority Updates | ❌ | ✓ |
| Email Support | ❌ | ✓ |
| License Activation | — | ✓ |
| Gaming Tools | ✓ | ✓ |

## Performance

- **Boot time**: ~30 seconds
- **Security scan**: ~2 minutes
- **Memory usage**: 512MB - 2GB
- **Disk usage**: 2-3GB

## Troubleshooting

**License won't activate:**
```bash
aegis-cli status
# Check license key is correct
# Verify internet connection
```

**Security scanner not running:**
```bash
sudo systemctl status aegis-security-monitor
sudo systemctl restart aegis-security-monitor
```

**Too many threat alerts:**
```bash
sudo aegis-security --whitelist /path/to/app
# Add trusted applications
```

## Support

- **Email**: support@aegis-os.dev
- **Documentation**: /usr/share/doc/aegis-security/
- **License Portal**: https://license.aegis-os.dev

---

**Aegis OS Basic** - Secure, supported, and affordable.

License: $49/year | Build Time: 90-120 minutes | Support: Yes
