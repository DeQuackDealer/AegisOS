#!/bin/bash
# Aegis OS USB Creator Script

if [ $# -eq 0 ]; then
    echo "Usage: $0 /dev/sdX"
    echo "Warning: This will erase all data on the target device!"
    exit 1
fi

DEVICE=$1
ISO_FILE="aegis-os-freemium.iso"

echo "🛡️  Aegis OS USB Creator"
echo "========================"
echo "Target device: $DEVICE"
echo "ISO file: $ISO_FILE"
echo ""
echo "⚠️  This will ERASE all data on $DEVICE"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo "🔥 Creating bootable USB..."
sudo dd if="$ISO_FILE" of="$DEVICE" bs=4M status=progress oflag=sync

echo "✅ Bootable USB created successfully!"
echo "🚀 Your Aegis OS USB is ready to boot!"
