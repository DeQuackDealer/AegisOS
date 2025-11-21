# Build BOOTABLE Aegis OS ISO (Buildroot)

This guide will create a real, bootable Aegis OS ISO in 90-120 minutes.

## Prerequisites
- **Linux machine** (Ubuntu 20.04+ or Debian recommended)
- **8GB+ RAM** (16GB better)
- **20GB free disk space**
- **Internet connection**

## Step 1: Install Build Tools

```bash
sudo apt-get update
sudo apt-get install -y build-essential wget cpio unzip rsync bc libncurses5-dev
```

## Step 2: Get the Build Files

Download the `aegis-os-freemium/` folder from this repo or copy these files:
- `build.sh` - Build automation script
- `post-build.sh` - Post-build setup
- `buildroot-config/.config` - Buildroot configuration (593 settings)
- `overlay/` - Custom files and utilities

## Step 3: Run the Build

```bash
cd aegis-os-freemium
chmod +x build.sh post-build.sh
./build.sh
```

**This will:**
1. Download Buildroot 2023.08 (~200MB)
2. Apply Aegis OS configuration
3. Compile Linux 6.6.7 + XFCE 4.18 + Wine + Proton (~90-120 min)
4. Generate 4 output files

## Step 4: Find Your Bootable ISO

After build completes, look in `aegis-os-freemium/output/`:

```
✓ aegis-os-freemium.iso    ← BOOTABLE ISO! Use this!
✓ aegis-os-freemium.ext4   ← Filesystem only
✓ aegis-kernel             ← Linux kernel
✓ checksums.txt            ← Verification
```

## Step 5: Test in VirtualBox

```bash
# On your Linux machine:
virtualbox &

# Create new VM:
# - Name: Aegis OS
# - Type: Linux / Other Linux 64-bit
# - Memory: 4GB+
# - CPU cores: 2+
# - Storage: Point to aegis-os-freemium.iso
# - Click Start
```

**It should boot and auto-login as user `aegis`** ✓

## Step 6: Create Bootable USB (with Balena Etcher)

Once you've tested and verified in VirtualBox:

```bash
# On Windows/Mac/Linux:
1. Download Balena Etcher: https://balena.io/etcher
2. Open Etcher
3. Select: aegis-os-freemium.iso
4. Select: Your USB drive (8GB+)
5. Click Flash
6. Wait for "Flash complete!"
7. Plug USB into any computer and boot
```

## Troubleshooting

**Build fails with "command not found":**
- Run: `sudo apt-get install build-essential wget cpio unzip rsync bc libncurses5-dev`

**Build times out or crashes:**
- Make sure you have 16GB+ RAM
- Close other applications
- Try again (downloads are cached after first run)

**ISO won't boot in VirtualBox:**
- Check boot order (CD should be first)
- Try with 4GB+ RAM
- Enable 3D acceleration in VM settings

**Need help?**
- Check the build.sh script comments
- Buildroot docs: https://buildroot.org/
- Linux 6.6.7 docs: https://kernel.org

---

**Expected build output:**
```
✅ Linux 6.6.7 kernel compiled
✅ XFCE 4.18 desktop ready
✅ Wine 8.21 + Proton installed
✅ Gaming optimized
✅ Buildroot-generated ISO created
```

**The ISO is ~2.5GB and fully bootable.** Ready for VirtualBox and USB!
