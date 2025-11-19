
#!/bin/bash
set -e

# Aegis OS Freemium Build Script
# Compiles the complete Aegis OS Freemium edition using Buildroot

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"
OUTPUT_DIR="$SCRIPT_DIR/output"

echo "🚀 Starting Aegis OS Freemium Build Process..."

# Check if buildroot is available
if ! command -v make &> /dev/null; then
    echo "❌ Make is required but not installed"
    exit 1
fi

# Create build directories
mkdir -p "$BUILD_DIR"
mkdir -p "$OUTPUT_DIR"

# Download buildroot if not present
BUILDROOT_VERSION="2023.08"
BUILDROOT_DIR="$BUILD_DIR/buildroot-$BUILDROOT_VERSION"

if [ ! -d "$BUILDROOT_DIR" ]; then
    echo "📦 Downloading Buildroot $BUILDROOT_VERSION..."
    cd "$BUILD_DIR"
    wget -q "https://buildroot.org/downloads/buildroot-$BUILDROOT_VERSION.tar.gz"
    tar -xzf "buildroot-$BUILDROOT_VERSION.tar.gz"
    rm "buildroot-$BUILDROOT_VERSION.tar.gz"
fi

# Copy Aegis configuration to buildroot
echo "🔧 Configuring Buildroot for Aegis OS..."
cp "$SCRIPT_DIR/buildroot-config/.config" "$BUILDROOT_DIR/.config"

# Set up overlay path
cd "$BUILDROOT_DIR"
sed -i "s|aegis-os-freemium/overlay|$SCRIPT_DIR/overlay|g" .config
sed -i "s|aegis-os-freemium/post-build.sh|$SCRIPT_DIR/post-build.sh|g" .config

# Make post-build script executable
chmod +x "$SCRIPT_DIR/post-build.sh"

# Start the build process
echo "🛠️  Building Aegis OS Freemium (this may take 1-2 hours)..."
make olddefconfig
make -j$(nproc)

# Copy output files
echo "📤 Copying build artifacts..."
cp "$BUILDROOT_DIR/output/images/rootfs.ext4" "$OUTPUT_DIR/aegis-os-freemium.ext4"

if [ -f "$BUILDROOT_DIR/output/images/bzImage" ]; then
    cp "$BUILDROOT_DIR/output/images/bzImage" "$OUTPUT_DIR/aegis-kernel"
fi

if [ -f "$BUILDROOT_DIR/output/images/grub-eltorito.iso" ]; then
    cp "$BUILDROOT_DIR/output/images/grub-eltorito.iso" "$OUTPUT_DIR/aegis-os-freemium.iso"
fi

# Generate checksums
echo "🔐 Generating checksums..."
cd "$OUTPUT_DIR"
sha256sum * > checksums.txt

echo "✅ Aegis OS Freemium build completed successfully!"
echo "📁 Output files are in: $OUTPUT_DIR"
echo ""
echo "Files generated:"
ls -la "$OUTPUT_DIR"

echo ""
echo "🛡️  AEGIS OS FREEMIUM EDITION - GENESIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎮 Gaming Features:"
echo "   ✅ Proton and Wine pre-configured"
echo "   ✅ Gaming optimization tools"
echo "   ✅ Low-latency kernel settings"
echo ""
echo "🖥️  System Features:"
echo "   ✅ XFCE desktop environment"
echo "   ✅ Comprehensive system monitoring"
echo "   ✅ License management system"
echo "   ✅ Kernel module interface"
echo ""
echo "🔧 Advanced Features:"
echo "   ✅ Custom Aegis kernel module"
echo "   ✅ Professional system utilities"
echo "   ✅ Automated optimization services"
echo "   ✅ Aegis branding and wallpaper"
echo ""
echo "🌐 Community Support:"
echo "   ✅ Community forums access"
echo "   ✅ Documentation and guides"
echo "   ✅ No license required - completely free!"
echo ""
echo "💿 Installation:"
echo "   sudo dd if=$OUTPUT_DIR/aegis-os-freemium.iso of=/dev/sdX bs=4M status=progress"
echo ""
echo "🚀 Ready to upgrade to paid editions?"
echo "   Visit: https://aegis-os.com/editions"
echo "   Get: AI optimization, priority support, advanced features"
echo ""
echo "🛡️  Aegis OS - The Gold Standard for Gamers, AI Developers & Servers"
