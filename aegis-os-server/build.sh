#!/bin/bash
set -e

# Aegis OS Server Build Script
# $199/year - Enterprise features, rebootless patching, security

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"
OUTPUT_DIR="$SCRIPT_DIR/output"

echo "🚀 Starting Aegis OS Server Build Process..."

mkdir -p "$BUILD_DIR"
mkdir -p "$OUTPUT_DIR"

BUILDROOT_VERSION="2023.08"
BUILDROOT_DIR="$BUILD_DIR/buildroot-$BUILDROOT_VERSION"

if [ ! -d "$BUILDROOT_DIR" ]; then
    echo "📦 Downloading Buildroot $BUILDROOT_VERSION..."
    cd "$BUILD_DIR"
    wget -q "https://buildroot.org/downloads/buildroot-$BUILDROOT_VERSION.tar.gz"
    tar -xzf "buildroot-$BUILDROOT_VERSION.tar.gz"
    rm "buildroot-$BUILDROOT_VERSION.tar.gz"
fi

echo "🔧 Configuring Buildroot for Aegis OS Server..."
cp "$SCRIPT_DIR/buildroot-config/.config" "$BUILDROOT_DIR/.config"

cd "$BUILDROOT_DIR"
sed -i "s|aegis-os-server/overlay|$SCRIPT_DIR/overlay|g" .config
sed -i "s|aegis-os-server/post-build.sh|$SCRIPT_DIR/post-build.sh|g" .config

chmod +x "$SCRIPT_DIR/post-build.sh"

# Security features (PAID TIER)
echo "🔒 Adding enterprise security & monitoring..."
echo "BR2_PACKAGE_OPENSSL=y" >> "$BUILDROOT_DIR/.config"
echo "BR2_PACKAGE_UFW=y" >> "$BUILDROOT_DIR/.config"
echo "BR2_PACKAGE_FAIL2BAN=y" >> "$BUILDROOT_DIR/.config"

# Enterprise packages
echo "📊 Adding enterprise & monitoring tools..."
echo "BR2_PACKAGE_NGINX=y" >> "$BUILDROOT_DIR/.config"
echo "BR2_PACKAGE_POSTGRESQL=y" >> "$BUILDROOT_DIR/.config"
echo "BR2_PACKAGE_DOCKER=y" >> "$BUILDROOT_DIR/.config"
echo "BR2_PACKAGE_PROMETHEUS=y" >> "$BUILDROOT_DIR/.config"
echo "BR2_PACKAGE_GRAFANA=y" >> "$BUILDROOT_DIR/.config"
echo "BR2_PACKAGE_LOGSTASH=y" >> "$BUILDROOT_DIR/.config"

# Rebootless patching support
echo "BR2_PACKAGE_KPATCH=y" >> "$BUILDROOT_DIR/.config"
echo "BR2_PACKAGE_LIVEPATCH=y" >> "$BUILDROOT_DIR/.config"

echo "🛠️  Building Aegis OS Server (1-2 hours)..."
cd "$BUILDROOT_DIR"
make olddefconfig
make -j$(nproc)

echo "📤 Copying build artifacts..."
cp "$BUILDROOT_DIR/output/images/rootfs.ext4" "$OUTPUT_DIR/aegis-os-server.ext4"
[ -f "$BUILDROOT_DIR/output/images/bzImage" ] && cp "$BUILDROOT_DIR/output/images/bzImage" "$OUTPUT_DIR/aegis-kernel-server"
[ -f "$BUILDROOT_DIR/output/images/grub-eltorito.iso" ] && cp "$BUILDROOT_DIR/output/images/grub-eltorito.iso" "$OUTPUT_DIR/aegis-os-server.iso"

echo "🔐 Generating checksums..."
cd "$OUTPUT_DIR"
sha256sum * > checksums.txt

echo "✅ Aegis OS Server build completed!"
echo "📁 Output: $OUTPUT_DIR"
echo ""
echo "🏢 Features:"
echo "  ✓ Nginx + PostgreSQL"
echo "  ✓ Docker ready"
echo "  ✓ Prometheus + Grafana"
echo "  ✓ Rebootless patching"
echo "  ✓ Enterprise security & monitoring"
