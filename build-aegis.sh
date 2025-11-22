#!/bin/bash
set -e

echo "🛡️ Aegis OS Build System"
echo "========================"
echo ""
echo "Choose which edition to build:"
echo ""
echo "1. Freemium    (FREE,   2.1GB, ~2 hours) - Base OS"
echo "2. Basic       ($49,    2.2GB, ~2 hours) - + Security"
echo "3. Gamer       ($99,    2.4GB, ~2 hours) - + Gaming"
echo "4. AI Dev      ($149,   2.5GB, ~2 hours) - + ML/AI"
echo "5. Server      ($199,   2.6GB, ~2 hours) - Enterprise"
echo "6. Workplace   ($79,    2.3GB, ~2 hours) - + Teams"
echo ""
read -p "Enter number (1-6): " choice

case $choice in
    1) TIER="freemium" ;;
    2) TIER="basic" ;;
    3) TIER="gamer" ;;
    4) TIER="ai-dev" ;;
    5) TIER="server" ;;
    6) TIER="workplace" ;;
    *) echo "❌ Invalid choice"; exit 1 ;;
esac

echo ""
echo "🚀 Building Aegis OS $TIER Edition..."
echo ""

# Check if we're in the right directory
if [ ! -d "aegis-os-$TIER" ]; then
    echo "❌ Error: aegis-os-$TIER directory not found"
    echo "Make sure you're in the root of the Aegis OS folder"
    exit 1
fi

# Navigate to tier directory and run build
cd "aegis-os-$TIER"

if [ ! -f "build.sh" ]; then
    echo "❌ Error: build.sh not found in aegis-os-$TIER"
    exit 1
fi

# Make build script executable and run it
chmod +x build.sh
./build.sh

echo ""
echo "✅ Build complete!"
echo "📁 ISO file: $(pwd)/output/aegis-os-$TIER.iso"
echo ""
echo "Next steps:"
echo "1. Download the ISO file to your computer"
echo "2. Use Balena Etcher to flash it to a USB drive (8GB+)"
echo "3. Boot from USB on your target system"
