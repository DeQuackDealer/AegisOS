
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
chroot $TARGET_DIR systemctl enable NetworkManager

# Set executable permissions
chmod +x $TARGET_DIR/usr/local/bin/*
chmod +x $TARGET_DIR/etc/init.d/*

echo "Aegis OS Freemium build complete!"
