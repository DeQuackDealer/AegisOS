# Aegis OS ISO Builder

Build Aegis OS installation media directly on your computer. 100% offline operation after initial setup.

## Overview

The ISO Builder creates bootable Aegis OS ISO files that you can flash to USB using Balena Etcher.

### Two Versions

| Version | File | License Required |
|---------|------|------------------|
| **Freemium** | `AegisBuilderFreemium.exe` | No |
| **Licensed** | `AegisBuilderLicensed.exe` | Yes (paid editions) |

## User Flow

### Freemium Edition

1. **Download** `AegisBuilderFreemium.exe` (or run the .py script)
2. **Open** the application
3. **Click "Build ISO"** - building starts immediately
4. **Wait** for the ISO to be generated (~10-30 minutes)
5. **Open Balena Etcher** when prompted
6. **Flash** the ISO to a USB drive (8GB+ recommended)
7. **Boot** from USB to install Aegis OS

### Paid Editions (Basic, Gamer, AI Developer, etc.)

1. **Purchase** a license from the Aegis OS website
2. **Download** `AegisBuilderLicensed.exe`
3. **Open** the application
4. **Enter your license key** or load your license.json file
5. **Select** your edition (the one your license is valid for)
6. **Click "Build ISO"**
7. **Wait** for the ISO to be generated
8. **Flash** to USB with Balena Etcher

## Editions & Pricing

| Edition | Price | Description |
|---------|-------|-------------|
| Freemium | FREE | Basic desktop with essential tools |
| Basic | $69 | Full desktop with security and backup |
| Workplace | $49 | Business productivity suite |
| Gamer | $69 | Gaming-optimized with Steam/Lutris |
| AI Developer | $89 | ML/AI development tools |
| Gamer+AI | $129 | Ultimate gaming with AI enhancements |
| Server | $129 | Headless server with Docker |

## Building the Executables

### Requirements

- Python 3.11+
- PyInstaller
- cryptography library (for licensed version)

### Build Command

```bash
cd build-system/iso-builder
python build-executables.py
```

Output:
- `dist/AegisBuilderFreemium.exe` (~15 MB without resources)
- `dist/AegisBuilderLicensed.exe` (~20 MB without resources)

### Adding Resources

For the builders to work, you must populate the `resources/` folder:

```
resources/
├── base_system.tar.xz      # Pre-built Linux base (~2-3 GB)
├── kernel/
│   ├── vmlinuz             # Linux kernel
│   └── initrd.img          # Initial ramdisk
├── isolinux/
│   ├── isolinux.bin        # BIOS bootloader
│   ├── ldlinux.c32         # Required modules
│   ├── libutil.c32
│   ├── libcom32.c32
│   └── vesamenu.c32
└── overlays/
    ├── overlay_basic.tar.xz
    ├── overlay_gamer.tar.xz
    ├── overlay_ai.tar.xz
    └── ...
```

See `resources/README.txt` for detailed instructions on creating these files.

## License System

### How It Works

1. Customer purchases license on website
2. Website generates RSA-2048 signed license
3. Customer receives `license.json` file
4. Builder verifies signature offline
5. Valid license → build proceeds
6. Invalid license → build blocked with clear error

### License File Format

```json
{
  "edition": "gamer",
  "email": "customer@example.com",
  "key": "AEGIS-XXXX-XXXX-XXXX",
  "signature": "base64-encoded-rsa-signature",
  "expires": "2026-01-01T00:00:00Z"
}
```

### License Search Locations

The builder automatically searches:
- Current directory
- `~/.aegis/license.json`
- `~/Downloads/aegis-license.json`
- `~/Desktop/aegis-license.json`
- USB drives (root and aegis/ subfolder)

## Running Without Compiling

If you have Python installed, you can run the builders directly:

```bash
# Freemium
python aegis_builder_freemium.py

# Licensed
python aegis_builder_licensed.py
```

## Alternative Formats

### Windows HTA (Legacy)
`aegis-iso-builder.hta` - Double-click to run on Windows. Uses WSL2 for building.

### Linux Shell Script
`aegis-iso-builder.sh` - Native Linux ISO builder.

## Troubleshooting

### "Missing resources" Error
Ensure the `resources/` folder contains all required files. See `resources/README.txt`.

### "Invalid license" Error
- Check your license key is entered correctly
- Ensure your license hasn't expired
- Verify you're using the correct edition

### Build Fails
- Ensure you have 15GB+ free disk space
- On Windows, WSL2 may be required for some operations
- Check the build log for specific errors

## Support

- Website: https://aegis-os.com
- Support: support@aegis-os.com
