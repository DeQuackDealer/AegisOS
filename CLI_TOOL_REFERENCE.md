# Aegis OS CLI Tool Reference

## Installation

```bash
# Automatic (included with OS)
aegis-cli --version

# Manual
pip install aegis-os-cli
```

## License Commands

### Activate License
```bash
aegis-cli activate --key AEGIS-BASIC-2024-XXXXX
```

Response:
```
✓ License activated
Tier: Basic
Expires: 2025-12-31
Features: security, ai_detection, firewall
```

### Check License Status
```bash
aegis-cli status
```

Response:
```
License Status
├─ Tier: Basic ($49/year)
├─ Status: Active
├─ Expires: 2025-12-31 (in 40 days)
├─ Hardware ID: UUID-XXXX-XXXX
└─ Support: Email support
```

### List Active Licenses
```bash
aegis-cli licenses list
```

### Deactivate License
```bash
aegis-cli deactivate
```

## Security Commands

### Run Security Scan
```bash
# Quick scan (2-3 minutes)
aegis-cli security scan

# Full scan (10-15 minutes)
aegis-cli security scan --full

# Specific areas
aegis-cli security scan --firewall
aegis-cli security scan --files
aegis-cli security scan --processes
```

Response:
```
Security Scan Results
├─ Firewall: OK (23 rules active)
├─ File Integrity: OK (1,245 files verified)
├─ Processes: 1 suspicious process found
├─ Network: OK (no intrusions detected)
├─ Threat Level: MEDIUM
└─ Scan Time: 2m 34s
```

### Generate Security Report
```bash
aegis-cli security report

# Export formats
aegis-cli security report --format pdf
aegis-cli security report --format json
aegis-cli security report --format csv
```

### Whitelist Trusted Application
```bash
aegis-cli security whitelist /path/to/app --reason "Development"
```

### View Threat Log
```bash
aegis-cli security threats

# Filter by severity
aegis-cli security threats --severity critical
aegis-cli security threats --severity high
```

## System Information

### Display System Info
```bash
aegis-cli info
```

Response:
```
Aegis OS System Information
├─ Edition: Basic ($49/year)
├─ Version: 1.0.0
├─ Kernel: Linux 6.6.7
├─ Desktop: XFCE 4.18
├─ Uptime: 45 days 12 hours
├─ CPU: 8 cores @ 3.2 GHz
├─ RAM: 16 GB installed
├─ Storage: 500 GB SSD
├─ Graphics: GPU acceleration enabled
└─ Build Date: 2025-11-21
```

### Show Hardware Details
```bash
aegis-cli hardware
```

### Check System Health
```bash
aegis-cli health
```

Response:
```
System Health Check
├─ CPU Usage: 32%
├─ Memory Usage: 58%
├─ Disk Usage: 45%
├─ Temperature: 55°C (Normal)
├─ Filesystem: OK
└─ All Systems: Healthy ✓
```

## User & Account Commands

### User Profile
```bash
aegis-cli user profile
```

### Enable Two-Factor Authentication
```bash
aegis-cli user 2fa enable
```

Response:
```
Two-Factor Authentication Setup
Scan this QR code in your authenticator app:
[QR CODE]
Backup Codes:
- XXXX-XXXX-XXXX
- XXXX-XXXX-XXXX
```

### Disable Two-Factor Authentication
```bash
aegis-cli user 2fa disable
```

### Change Password
```bash
aegis-cli user password change
```

## Update Commands

### Check for Updates
```bash
aegis-cli update check
```

Response:
```
Update Check
├─ Current Version: 1.0.0
├─ Latest Version: 1.0.1
├─ Update Available: Yes
├─ Release Date: 2025-11-25
└─ Size: 245 MB
```

### Install Updates
```bash
# Auto-install
aegis-cli update install

# Dry-run first
aegis-cli update install --dry-run

# Schedule for later
aegis-cli update schedule --time "2:00 AM"
```

### View Update History
```bash
aegis-cli update history
```

## Backup Commands

### Schedule Backup
```bash
# Daily backup
aegis-cli backup schedule --frequency daily

# Weekly backup
aegis-cli backup schedule --frequency weekly

# Custom schedule
aegis-cli backup schedule --frequency custom --cron "0 2 * * *"
```

### List Backups
```bash
aegis-cli backup list
```

### Create Manual Backup
```bash
aegis-cli backup create
```

### Restore from Backup
```bash
aegis-cli backup restore --id backup-id
```

## Network Commands

### Show Network Status
```bash
aegis-cli network status
```

### Configure Firewall
```bash
# Enable firewall
aegis-cli firewall enable

# Disable firewall
aegis-cli firewall disable

# Show rules
aegis-cli firewall rules

# Add rule
aegis-cli firewall add --port 8080 --protocol tcp --action allow
```

## Performance Commands

### Display Performance Stats
```bash
aegis-cli performance stats
```

### Optimize System
```bash
aegis-cli optimize
```

### Clear Cache
```bash
aegis-cli cache clear
```

### Monitor Real-time
```bash
aegis-cli monitor
```

## Developer Commands

### Initialize Project
```bash
aegis-cli init --project myapp
```

### Run Build
```bash
aegis-cli build
```

### Run Tests
```bash
aegis-cli test
```

### Deploy Application
```bash
aegis-cli deploy
```

## Service Management

### Manage Services
```bash
# Start service
aegis-cli service start <service-name>

# Stop service
aegis-cli service stop <service-name>

# Restart service
aegis-cli service restart <service-name>

# List services
aegis-cli service list

# Enable autostart
aegis-cli service enable <service-name>
```

## System Commands

### Shutdown
```bash
aegis-cli shutdown
```

### Reboot
```bash
aegis-cli reboot
```

### Put to Sleep
```bash
aegis-cli sleep
```

### Lock Screen
```bash
aegis-cli lock
```

## Configuration Commands

### Set Configuration
```bash
aegis-cli config set key value

# Examples
aegis-cli config set theme dark
aegis-cli config set language en_US
aegis-cli config set notifications enabled
```

### Get Configuration
```bash
aegis-cli config get key

# Get all
aegis-cli config get all
```

### Reset Configuration
```bash
aegis-cli config reset
```

## Help & Documentation

### Show Help
```bash
# General help
aegis-cli help

# Command-specific help
aegis-cli help <command>

# Examples
aegis-cli help security
aegis-cli help update
```

### Show Version
```bash
aegis-cli --version
```

### Show License Info
```bash
aegis-cli license info
```

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Invalid argument
- `3` - Command not found
- `4` - Permission denied
- `5` - License invalid/expired
- `127` - Command not found

## Examples

### Complete Security Setup
```bash
# Activate license
aegis-cli activate --key AEGIS-BASIC-2024-XXXXX

# Enable 2FA
aegis-cli user 2fa enable

# Configure firewall
aegis-cli firewall enable
aegis-cli firewall add --port 22 --protocol tcp --action allow

# Run security scan
aegis-cli security scan --full

# Schedule daily backups
aegis-cli backup schedule --frequency daily
```

### System Maintenance
```bash
# Check health
aegis-cli health

# Check for updates
aegis-cli update check

# Optimize system
aegis-cli optimize

# Clear cache
aegis-cli cache clear

# View logs
aegis-cli logs tail
```

---

**Aegis OS CLI v1.0 - Complete Reference**
