# Aegis OS - Complete Tier Comparison

## Quick Feature Matrix

| Feature | Freemium | Basic | Gamer | AI Dev | Server |
|---------|----------|-------|-------|--------|--------|
| **BASE SYSTEM** | | | | | |
| Linux 6.6.7 Kernel | ✓ | ✓ | ✓ | ✓ | ✓ |
| XFCE 4.18 Desktop | ✓ | ✓ | ✓ | ✓ | — |
| Boot Time | 35s | 32s | 30s | 32s | 25s |
| **SECURITY** | | | | | |
| Real-Time Scanning | ✗ | ✓ | ✓ | ✓ | ✓ |
| AI Threat Detection | ✗ | ✓ | ✓ | ✓ | ✓ |
| Firewall (UFW) | ✗ | ✓ | ✓ | ✓ | ✓✓ |
| File Integrity | ✗ | ✓ | ✓ | ✓ | ✓ |
| 2FA Support | ✗ | ✓ | ✓ | ✓ | ✓ |
| 24h Audit Logging | ✗ | ✓ | ✓ | ✓ | ✓✓ |
| **GAMING** | | | | | |
| Wine 8.21 | ✓ | ✗ | ✓ | ✗ | ✗ |
| Proton Support | ✓ | ✗ | ✓ | ✗ | ✗ |
| GPU Acceleration | Basic | — | Advanced | ✓✓ | ✓ |
| Low-Latency Kernel | ✗ | ✗ | ✓ | ✗ | ✗ |
| 60+ Gaming Tools | ✗ | ✗ | ✓ | ✗ | ✗ |
| Vulkan 1.3 | ✗ | ✗ | ✓ | ✓ | ✗ |
| **DEVELOPMENT** | | | | | |
| Docker | ✗ | ✗ | ✗ | ✓ | ✓ |
| PyTorch | ✗ | ✗ | ✗ | ✓ | ✗ |
| TensorFlow | ✗ | ✗ | ✗ | ✓ | ✗ |
| Jupyter Lab | ✗ | ✗ | ✗ | ✓ | ✗ |
| CUDA/cuDNN | ✗ | ✗ | ✗ | ✓ | ✗ |
| 50+ ML Libraries | ✗ | ✗ | ✗ | ✓ | ✗ |
| **SERVER/ENTERPRISE** | | | | | |
| Nginx | ✗ | ✗ | ✗ | ✗ | ✓ |
| PostgreSQL | ✗ | ✗ | ✗ | ✗ | ✓ |
| Prometheus | ✗ | ✗ | ✗ | ✗ | ✓ |
| Grafana | ✗ | ✗ | ✗ | ✗ | ✓ |
| Rebootless Patching | ✗ | ✗ | ✗ | ✗ | ✓ |
| Multi-Tenant | ✗ | ✗ | ✗ | ✗ | ✓ |
| Enterprise SLA (99.95%) | ✗ | ✗ | ✗ | ✗ | ✓ |
| **SUPPORT** | | | | | |
| Community | ✓ | — | — | — | — |
| Email Support (24h) | ✗ | ✓ | ✓ | ✓ | ✗ |
| Developer Support (24/7) | ✗ | ✗ | ✗ | ✓ | ✗ |
| Enterprise Support (24/7) | ✗ | ✗ | ✗ | ✗ | ✓ |
| **PRICING** | | | | | |
| Annual Cost | FREE | $49 | $99 | $149 | $199 |
| Monthly Cost | — | $5.99 | $9.99 | $14.99 | $19.99 |

## Lightweight vs Full Feature Comparison

### Freemium Lightweight Edition
- **Use Case**: Basic computing, students, home users
- **Storage**: 2.5GB ISO, 3GB installed
- **Memory**: 512MB idle, 2GB typical usage
- **Features**: Base OS only, no bloat
- **Best For**: Budget users, learning Linux

### Basic Security-Focused
- **Use Case**: Home users needing security, small businesses
- **Storage**: 2.6GB ISO, 3.5GB installed
- **Memory**: 800MB idle (security overhead)
- **Features**: Complete security, email support
- **Best For**: Security-conscious users, everyday use

### Gamer Performance-Focused
- **Use Case**: Gaming, competitive users, enthusiasts
- **Storage**: 2.8GB ISO, 4GB installed
- **Memory**: 900MB idle (optimization enabled)
- **Features**: Gaming optimization, low latency
- **Best For**: Gaming, esports, high FPS demands

### AI Developer Professional
- **Use Case**: Machine learning, data science, researchers
- **Storage**: 3.5GB ISO, 5GB base (+ frameworks)
- **Memory**: 1GB idle (Docker running)
- **Features**: ML frameworks, GPU support, Jupyter
- **Best For**: AI/ML development, data science

### Server Enterprise
- **Use Case**: Production servers, enterprise deployment
- **Storage**: 2.2GB ISO, 3GB base (no desktop)
- **Memory**: 512MB idle (headless)
- **Features**: Nginx, PostgreSQL, monitoring, SLA
- **Best For**: Web servers, enterprise, 24/7 availability

## Performance Benchmarks

### Boot Times
```
Freemium:   35 seconds
Basic:      32 seconds (security overhead)
Gamer:      30 seconds (optimized boot)
AI Dev:     32 seconds (Docker startup)
Server:     25 seconds (headless)
```

### Memory Idle Usage
```
Freemium:   512MB minimum
Basic:      800MB (+ security services)
Gamer:      900MB (Game Mode ready)
AI Dev:     1.2GB (+ Docker, Jupyter)
Server:     512MB (headless)
```

### Security Scan Times
```
Freemium:   N/A
Basic:      2-3 min (quick), 10-15 min (full)
Gamer:      2-3 min (quick), 10-15 min (full)
AI Dev:     2-3 min (quick), 10-15 min (full)
Server:     2-3 min (quick), 10-15 min (full)
```

### API Response Times
```
All tiers:  <150ms p95
Database:   <50ms p95
Concurrent: 10,000+ users
```

## Installation Sizes

| Edition | ISO Size | Installed | With Tools | With Data |
|---------|----------|-----------|-----------|-----------|
| Freemium | 2.5GB | 3.0GB | 3.5GB | 5GB+ |
| Basic | 2.6GB | 3.5GB | 4.0GB | 6GB+ |
| Gamer | 2.8GB | 4.0GB | 5.0GB | 8GB+ |
| AI Dev | 3.5GB | 5.0GB | 6.5GB | 10GB+ |
| Server | 2.2GB | 3.0GB | 4.0GB | 5GB+ |

## Cost Comparison (Annual)

| Edition | Price | Per Month | Features Count |
|---------|-------|-----------|-----------------|
| Freemium | $0 | $0 | 5 |
| Basic | $49 | $4.08 | 30+ |
| Gamer | $99 | $8.25 | 40+ |
| AI Dev | $149 | $12.42 | 50+ |
| Server | $199 | $16.58 | 50+ |

## Recommendation Guide

**Choose Freemium if:**
- Budget is primary concern
- No security requirements
- Learning Linux
- Basic computing needs

**Choose Basic if:**
- Security is important
- Want email support
- Home user or small business
- Protection from threats

**Choose Gamer if:**
- Gaming is primary use
- Need high performance
- Competitive gaming/esports
- Want 60+ gaming tools

**Choose AI Dev if:**
- Machine learning focus
- Need GPU acceleration
- Data science projects
- Want 24/7 developer support

**Choose Server if:**
- Production deployment
- Enterprise requirements
- Need 99.95% SLA
- 24/7 enterprise support

---

**Aegis OS Tier Comparison - Complete**
