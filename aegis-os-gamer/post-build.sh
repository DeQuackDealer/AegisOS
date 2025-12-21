
#!/bin/bash
set -e

TARGET_DIR=$1
PASSWORD_MODE=${2:-"passwordless"}  # "passwordless" or "password" (default: passwordless)

if [ "$PASSWORD_MODE" = "passwordless" ]; then
    echo "Setting up Aegis OS Gamer Edition (Passwordless)..."
    EDITION_SUFFIX="-passwordless"
else
    echo "Setting up Aegis OS Gamer Edition (Password Protected)..."
    EDITION_SUFFIX=""
fi

# Create aegis user in passwd (using 'x' placeholder pointing to shadow)
echo "aegis:x:1000:1000:Aegis User:/home/aegis:/bin/bash" >> $TARGET_DIR/etc/passwd
echo "aegis:x:1000:" >> $TARGET_DIR/etc/group

# Create shadow entry based on password mode
if [ "$PASSWORD_MODE" = "passwordless" ]; then
    # Empty password field allows login without password (with autologin)
    echo "aegis::19722:0:99999:7:::" >> $TARGET_DIR/etc/shadow
    echo "aegis:!::" >> $TARGET_DIR/etc/gshadow
    
    # Add autologin group for display managers
    echo "autologin:x:969:aegis" >> $TARGET_DIR/etc/group
    echo "autologin:!::aegis" >> $TARGET_DIR/etc/gshadow
else
    # Password-protected mode: set default password "aegis" (users should change it)
    # Generate SHA-512 hash with random salt at build time for security
    if command -v openssl >/dev/null 2>&1; then
        DEFAULT_PASS_HASH=$(openssl passwd -6 "aegis")
    elif command -v mkpasswd >/dev/null 2>&1; then
        DEFAULT_PASS_HASH=$(mkpasswd -m sha-512 "aegis")
    else
        # Fallback: use chpasswd in chroot to set password
        echo "aegis:aegis" | chroot $TARGET_DIR chpasswd
        DEFAULT_PASS_HASH=""
    fi
    if [ -n "$DEFAULT_PASS_HASH" ]; then
        echo "aegis:${DEFAULT_PASS_HASH}:19722:0:99999:7:::" >> $TARGET_DIR/etc/shadow
    fi
    echo "aegis:!::" >> $TARGET_DIR/etc/gshadow
fi

# Set proper permissions on shadow file
chmod 640 $TARGET_DIR/etc/shadow

mkdir -p $TARGET_DIR/home/aegis
chroot $TARGET_DIR chown -R 1000:1000 /home/aegis

# Set up sudo configuration based on password mode
mkdir -p $TARGET_DIR/etc/sudoers.d
if [ "$PASSWORD_MODE" = "passwordless" ]; then
    echo "aegis ALL=(ALL) NOPASSWD: ALL" > $TARGET_DIR/etc/sudoers.d/aegis
else
    echo "# Aegis user requires password for sudo (secure mode)" > $TARGET_DIR/etc/sudoers.d/aegis
    echo "aegis ALL=(ALL) ALL" >> $TARGET_DIR/etc/sudoers.d/aegis
fi
chmod 440 $TARGET_DIR/etc/sudoers.d/aegis

# Set up auto-login for XFCE via getty (only for passwordless mode)
mkdir -p $TARGET_DIR/etc/systemd/system/getty@tty1.service.d
if [ "$PASSWORD_MODE" = "passwordless" ]; then
    cat > $TARGET_DIR/etc/systemd/system/getty@tty1.service.d/override.conf << 'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin aegis --noclear %I $TERM
EOF
else
    # Standard login prompt for password-protected mode
    cat > $TARGET_DIR/etc/systemd/system/getty@tty1.service.d/override.conf << 'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --noclear %I $TERM
EOF
fi

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

# Set up Aegis branding based on password mode
if [ "$PASSWORD_MODE" = "passwordless" ]; then
    echo "AEGIS_OS_VERSION=1.0.0-gamer-passwordless" >> $TARGET_DIR/etc/os-release
    echo "AEGIS_OS_CODENAME=Genesis" >> $TARGET_DIR/etc/os-release
    echo "AEGIS_OS_EDITION=Gamer-Passwordless" >> $TARGET_DIR/etc/os-release
    
    # Create issue file for passwordless edition
    cat > $TARGET_DIR/etc/issue << 'EOF'

    ▄▀█ █▀▀ █▀▀ █ █▀   █▀█ █▀
    █▀█ ██▄ █▄█ █ ▄█   █▄█ ▄█
    
Aegis OS Gamer Edition (Passwordless) - Genesis
The Gold Standard for Gaming

Login: aegis (no password required)
Web: https://aegis-os.com

EOF
    echo "Aegis OS Gamer Edition (Passwordless) build complete!"
else
    echo "AEGIS_OS_VERSION=1.0.0-gamer" >> $TARGET_DIR/etc/os-release
    echo "AEGIS_OS_CODENAME=Genesis" >> $TARGET_DIR/etc/os-release
    echo "AEGIS_OS_EDITION=Gamer" >> $TARGET_DIR/etc/os-release
    
    # Create issue file for password-protected edition
    cat > $TARGET_DIR/etc/issue << 'EOF'

    ▄▀█ █▀▀ █▀▀ █ █▀   █▀█ █▀
    █▀█ ██▄ █▄█ █ ▄█   █▄█ ▄█
    
Aegis OS Gamer Edition - Genesis
The Gold Standard for Gaming

Login: aegis / Password: aegis
(Please change your password after first login)
Web: https://aegis-os.com

EOF
    echo "Aegis OS Gamer Edition build complete!"
fi
