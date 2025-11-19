
# Aegis OS Freemium Edition

The completely free, community-driven edition of Aegis OS with gaming-ready features and system optimization tools.

## Features

### Core System
- **Linux Foundation**: Built on a stable, secure Linux kernel
- **XFCE Desktop**: Lightweight desktop environment optimized for performance  
- **Gaming Ready**: Proton and Wine pre-configured for Windows game compatibility
- **System Monitoring**: Built-in performance monitoring and optimization
- **Community Support**: Access to forums and community documentation

### Gaming Optimization
- CPU governor optimization for performance
- Memory tuning for reduced latency
- Automatic Proton configuration for Steam
- Wine setup with essential libraries
- Gaming-focused system tweaks

### Included Applications
- Aegis System Monitor - Real-time system monitoring
- Aegis Gaming Optimizer - Performance optimization
- Aegis Welcome App - First-time setup and information
- Standard Linux utilities and tools

## Building from Source

### Requirements
- Linux build system with make, gcc, wget
- At least 8GB free disk space
- 4GB+ RAM (8GB recommended)
- Internet connection for downloading packages

### Build Process

1. **Clone or download** this repository
2. **Navigate** to the aegis-os-freemium directory  
3. **Run the build script**:
   ```bash
   chmod +x build.sh
   ./build.sh
   ```
4. **Wait** for the build to complete (1-2 hours depending on hardware)
5. **Find output** in the `output/` directory

### Output Files
- `aegis-os-freemium.iso` - Bootable ISO image
- `aegis-os-freemium.ext4` - Root filesystem image  
- `aegis-kernel` - Linux kernel
- `checksums.txt` - SHA256 checksums

## Installation

### Creating Bootable Media
```bash
# For USB drive (replace /dev/sdX with your USB device)
sudo dd if=output/aegis-os-freemium.iso of=/dev/sdX bs=4M status=progress
```

### System Requirements
- **CPU**: x86_64 processor
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 8GB minimum, 20GB recommended
- **Graphics**: Any graphics card with Linux drivers

## Usage

### First Boot
1. Boot from USB/CD
2. Automatic login to the `aegis` user account
3. XFCE desktop environment starts automatically
4. Welcome application provides setup options

### Gaming Setup
- Run "Aegis Gaming Optimizer" from the applications menu
- Steam games will use Proton automatically
- Windows applications can be run through Wine

### System Monitoring
The system monitor runs automatically and provides:
- Real-time performance statistics
- Resource usage alerts
- Log file management
- System health monitoring

## Configuration Files

### System Monitoring
- Configuration: `/etc/aegis/monitor-config.json`
- Statistics: `/var/lib/aegis/system-stats.json`
- Logs: `/var/log/aegis-system.log`

### Gaming Optimization  
- Configuration: `/etc/aegis/gaming-config.json`
- Logs: `/var/log/aegis-gaming.log`

## Limitations (Freemium Edition)

- **No priority security updates** - Updates come from community releases
- **No AI-powered optimizations** - Basic optimization algorithms only
- **Community support only** - No official technical support
- **No kernel-level enhancements** - Standard Linux kernel without Aegis modifications

## Upgrading to Paid Editions

Ready for more features? Check out our paid editions:

- **Basic Edition ($49/year)**: Priority security updates, email support, license validation
- **Gamer Edition ($99/year)**: AI-powered gaming optimization, advanced graphics tuning
- **AI Developer Edition ($149/year)**: CUDA/OpenCL optimization, development tools
- **Server Edition ($199/year)**: Enterprise features, multi-tenancy, advanced monitoring

Visit [https://aegis-os.com](https://aegis-os.com) to compare editions and upgrade.

## Community

- **Forums**: [https://community.aegis-os.com](https://community.aegis-os.com)
- **Documentation**: [https://docs.aegis-os.com](https://docs.aegis-os.com)
- **Bug Reports**: [https://github.com/aegis-os/community-issues](https://github.com/aegis-os/community-issues)

## License

Aegis OS Freemium Edition is released under the GPLv3 license. See LICENSE file for details.

Individual components may have different licenses - check specific package documentation.

---

**Aegis OS** - The gold standard for gamers, AI developers, and servers.
