#!/bin/bash
set -e

# Aegis OS Gamer Build Script
# Compiles the complete Aegis OS Gamer edition using Buildroot

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"
OUTPUT_DIR="$SCRIPT_DIR/output"

echo "🚀 Starting Aegis OS Gamer Build Process..."

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
echo "🔧 Configuring Buildroot for Aegis OS Gamer..."
cp "$SCRIPT_DIR/buildroot-config/.config" "$BUILDROOT_DIR/.config"

# Set up overlay path
cd "$BUILDROOT_DIR"
sed -i "s|aegis-os-gamer/overlay|$SCRIPT_DIR/overlay|g" .config
sed -i "s|aegis-os-gamer/post-build.sh|$SCRIPT_DIR/post-build.sh|g" .config

# Make post-build script executable
chmod +x "$SCRIPT_DIR/post-build.sh"

# Add security features (PAID TIER)
echo "🔒 Adding security & AI threat detection..."
echo "BR2_PACKAGE_OPENSSL=y" >> "$BUILDROOT_DIR/.config"
echo "BR2_PACKAGE_UFW=y" >> "$BUILDROOT_DIR/.config"

# Add gaming-specific optimizations
echo "🎮 Applying Gamer Edition optimizations..."
echo "BR2_PACKAGE_STEAM=y" >> "$BUILDROOT_DIR/.config"
echo "BR2_PACKAGE_PROTONGE=y" >> "$BUILDROOT_DIR/.config"
echo "BR2_KERNEL_CONFIG_FRAGMENT=\"$SCRIPT_DIR/gaming-kernel.config\"" >> "$BUILDROOT_DIR/.config"

# Start the build process
echo "🛠️  Building Aegis OS Gamer (this may take 1-2 hours)..."
cd "$BUILDROOT_DIR"
make olddefconfig
make -j$(nproc)

# Copy output files
echo "📤 Copying build artifacts..."
cp "$BUILDROOT_DIR/output/images/rootfs.ext4" "$OUTPUT_DIR/aegis-os-gamer.ext4"

if [ -f "$BUILDROOT_DIR/output/images/bzImage" ]; then
    cp "$BUILDROOT_DIR/output/images/bzImage" "$OUTPUT_DIR/aegis-kernel-gamer"
fi

if [ -f "$BUILDROOT_DIR/output/images/grub-eltorito.iso" ]; then
    cp "$BUILDROOT_DIR/output/images/grub-eltorito.iso" "$OUTPUT_DIR/aegis-os-gamer.iso"
fi

# Generate checksums
echo "🔐 Generating checksums..."
cd "$OUTPUT_DIR"
sha256sum * > checksums.txt

echo "✅ Aegis OS Gamer build completed successfully!"
echo "📁 Output files are in: $OUTPUT_DIR"
echo ""
echo "🎮 Features included:"
echo "  ✓ Low-latency gaming kernel"
echo "  ✓ AI game optimizer"
echo "  ✓ Proton/Wine enhanced"
echo "  ✓ Steam pre-configured"
echo "  ✓ GPU acceleration ready"
echo "  ✓ 60+ gaming utilities"
