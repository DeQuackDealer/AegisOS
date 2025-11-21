#!/bin/bash
# One-click Buildroot build for Aegis OS
# Run this on a Linux machine: bash QUICK_BUILD.sh

set -e

echo "🚀 AEGIS OS - BUILDROOT ISO BUILDER"
echo "===================================="
echo ""
echo "This will build a BOOTABLE ISO in 90-120 minutes"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."
command -v gcc &> /dev/null || { echo "❌ gcc not found. Run: sudo apt-get install build-essential"; exit 1; }
command -v wget &> /dev/null || { echo "❌ wget not found. Run: sudo apt-get install wget"; exit 1; }

AVAILABLE_RAM=$(free -g | awk 'NR==2 {print $2}')
if [ "$AVAILABLE_RAM" -lt 8 ]; then
    echo "⚠️  WARNING: Only ${AVAILABLE_RAM}GB RAM available (8GB+ recommended)"
fi

echo "✓ All prerequisites OK"
echo ""

# Navigate to script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📍 Working directory: $SCRIPT_DIR"
echo ""

# Make scripts executable
chmod +x build.sh post-build.sh

# Start build
echo "🛠️  Starting Buildroot compilation..."
echo "(This may take 1-2 hours - go grab coffee!)"
echo ""

./build.sh

echo ""
echo "✅ BUILD COMPLETE!"
echo ""
echo "📁 Your bootable ISO is here:"
echo "   $SCRIPT_DIR/output/aegis-os-freemium.iso"
echo ""
echo "🎮 Next steps:"
echo "   1. Test in VirtualBox"
echo "   2. Download Balena Etcher (balena.io/etcher)"
echo "   3. Flash to USB drive"
echo "   4. Boot any computer from USB"
echo ""
echo "Enjoy Aegis OS! 🚀"
