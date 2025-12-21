
#!/bin/bash
set -e

TARGET_DIR=$1

echo "Setting up Aegis OS Gamer Edition..."

# Create aegis user in passwd (using 'x' placeholder pointing to shadow)
echo "aegis:x:1000:1000:Aegis User:/home/aegis:/bin/bash" >> $TARGET_DIR/etc/passwd
echo "aegis:x:1000:" >> $TARGET_DIR/etc/group

# Create shadow entry with disabled/empty password for passwordless login
# Using '!' as password field means account has no password and password login is disabled
# The user can still login via auto-login getty without any password prompt
echo "aegis:!:19722:0:99999:7:::" >> $TARGET_DIR/etc/shadow

# Set proper permissions on shadow file
chmod 640 $TARGET_DIR/etc/shadow

# Create gshadow entry
echo "aegis:!::" >> $TARGET_DIR/etc/gshadow

mkdir -p $TARGET_DIR/home/aegis
chroot $TARGET_DIR chown -R 1000:1000 /home/aegis

# Set up passwordless sudo for aegis user
mkdir -p $TARGET_DIR/etc/sudoers.d
echo "aegis ALL=(ALL) NOPASSWD: ALL" > $TARGET_DIR/etc/sudoers.d/aegis
chmod 440 $TARGET_DIR/etc/sudoers.d/aegis

# Set up auto-login for XFCE via getty (no password required)
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
if [ -d "$TARGET_DIR/lib/modules" ]; then
    # Copy kernel module source - get absolute path from environment if available
    KERNEL_MOD_SRC="${KERNEL_MODULE_SOURCE:-.}"
    if [ -d "$KERNEL_MOD_SRC/kernel-module" ]; then
        mkdir -p $TARGET_DIR/usr/src/aegis-lkm
        cp -r $KERNEL_MOD_SRC/kernel-module/* $TARGET_DIR/usr/src/aegis-lkm/ 2>/dev/null || true
        
        # Build kernel module
        if [ -f "$TARGET_DIR/usr/src/aegis-lkm/Makefile" ]; then
            cd $TARGET_DIR/usr/src/aegis-lkm
            make KERNEL_SOURCE=$TARGET_DIR/lib/modules/*/build 2>/dev/null || echo "⚠️  Kernel module build skipped (using stub)"
            
            # Install kernel module if built successfully
            if [ -f "aegis_lkm.ko" ]; then
                mkdir -p $TARGET_DIR/lib/modules/*/extra
                cp aegis_lkm.ko $TARGET_DIR/lib/modules/*/extra/
                mkdir -p $TARGET_DIR/etc/modules-load.d
                echo "aegis_lkm" >> $TARGET_DIR/etc/modules-load.d/aegis.conf
                echo "✅ Kernel module installed"
            fi
        fi
    fi
fi

# Generate wallpaper (optional, not critical for boot)
if command -v python3 >/dev/null 2>&1; then
    if [ -f "$TARGET_DIR/usr/share/pixmaps/aegis-wallpaper-generator.py" ]; then
        chroot $TARGET_DIR python3 /usr/share/pixmaps/aegis-wallpaper-generator.py 2>/dev/null || echo "⚠️  Wallpaper generation skipped"
    fi
fi

# Create default directories
mkdir -p $TARGET_DIR/var/lib/aegis
mkdir -p $TARGET_DIR/var/log
mkdir -p $TARGET_DIR/etc/aegis

# Set up Aegis branding
echo "AEGIS_OS_VERSION=1.0.0-gamer" >> $TARGET_DIR/etc/os-release
echo "AEGIS_OS_CODENAME=Genesis" >> $TARGET_DIR/etc/os-release
echo "AEGIS_OS_EDITION=Gamer" >> $TARGET_DIR/etc/os-release

# Create issue file with Aegis branding
cat > $TARGET_DIR/etc/issue << 'EOF'

    ▄▀█ █▀▀ █▀▀ █ █▀   █▀█ █▀
    █▀█ ██▄ █▄█ █ ▄█   █▄█ ▄█
    
Aegis OS Gamer Edition - Genesis
The Gold Standard for Gaming

Login: aegis (no password required)
Web: https://aegis-os.com

EOF

echo "Aegis OS Gamer Edition build complete!"
