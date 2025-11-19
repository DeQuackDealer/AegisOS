
#!/bin/bash
set -e

TARGET_DIR=$1

echo "Setting up Aegis OS Freemium..."

# Create aegis user
echo "aegis:x:1000:1000:Aegis User:/home/aegis:/bin/bash" >> $TARGET_DIR/etc/passwd
echo "aegis:x:1000:" >> $TARGET_DIR/etc/group
mkdir -p $TARGET_DIR/home/aegis
chroot $TARGET_DIR chown -R 1000:1000 /home/aegis

# Set up auto-login for XFCE
mkdir -p $TARGET_DIR/etc/systemd/system/getty@tty1.service.d
cat > $TARGET_DIR/etc/systemd/system/getty@tty1.service.d/override.conf << 'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin aegis --noclear %I $TERM
EOF

# Enable services
chroot $TARGET_DIR systemctl enable aegis-system-monitor
chroot $TARGET_DIR systemctl enable aegis-gaming-optimizer
chroot $TARGET_DIR systemctl enable aegis-license-manager
chroot $TARGET_DIR systemctl enable aegis-kernel-interface
chroot $TARGET_DIR systemctl enable NetworkManager

# Set executable permissions
chmod +x $TARGET_DIR/usr/local/bin/*
chmod +x $TARGET_DIR/etc/init.d/*
chmod +x $TARGET_DIR/usr/share/pixmaps/aegis-wallpaper-generator.py

# Run VM optimization if in VM
chroot $TARGET_DIR /usr/local/bin/aegis-vm-optimizer

# Initialize desktop effects and wallpaper engine
chroot $TARGET_DIR /usr/local/bin/aegis-desktop-effects
chroot $TARGET_DIR /usr/local/bin/aegis-taskbar-manager
chroot $TARGET_DIR /usr/local/bin/aegis-wallpaper-engine

# Build and install kernel module
echo "Building Aegis OS kernel module..."
cd $TARGET_DIR/lib/modules/*/build
if [ -d "$PWD" ]; then
    # Copy kernel module source
    mkdir -p $TARGET_DIR/usr/src/aegis-lkm
    cp -r $(dirname $0)/kernel-module/* $TARGET_DIR/usr/src/aegis-lkm/
    
    # Build kernel module
    cd $TARGET_DIR/usr/src/aegis-lkm
    make KERNEL_SOURCE=$TARGET_DIR/lib/modules/*/build || echo "Kernel module build failed (will use stub)"
    
    # Install kernel module if built successfully
    if [ -f "aegis_lkm.ko" ]; then
        mkdir -p $TARGET_DIR/lib/modules/*/extra
        cp aegis_lkm.ko $TARGET_DIR/lib/modules/*/extra/
        echo "aegis_lkm" >> $TARGET_DIR/etc/modules-load.d/aegis.conf
        echo "✅ Kernel module installed"
    fi
fi

# Generate wallpaper
if command -v python3 >/dev/null 2>&1; then
    chroot $TARGET_DIR /usr/share/pixmaps/aegis-wallpaper-generator.py || echo "Wallpaper generation failed"
fi

# Create default directories
mkdir -p $TARGET_DIR/var/lib/aegis
mkdir -p $TARGET_DIR/var/log
mkdir -p $TARGET_DIR/etc/aegis

# Set up Aegis branding
echo "AEGIS_OS_VERSION=1.0.0-freemium" >> $TARGET_DIR/etc/os-release
echo "AEGIS_OS_CODENAME=Genesis" >> $TARGET_DIR/etc/os-release
echo "AEGIS_OS_EDITION=Freemium" >> $TARGET_DIR/etc/os-release

# Create issue file with Aegis branding
cat > $TARGET_DIR/etc/issue << 'EOF'

    ▄▀█ █▀▀ █▀▀ █ █▀   █▀█ █▀
    █▀█ ██▄ █▄█ █ ▄█   █▄█ ▄█
    
Aegis OS Freemium Edition - Genesis
The Gold Standard for Gaming

Login: aegis (no password required)
Web: https://aegis-os.com

EOF

echo "Aegis OS Freemium build complete!"
