#!/bin/bash
#
# Aegis OS ISO Builder
# Builds a complete Aegis OS ISO on your computer
# Then use Balena Etcher to flash it to USB
#

set -e

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="/tmp/aegis-build-$$"
OUTPUT_DIR="${HOME}/Downloads"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Edition configs
declare -A EDITION_NAMES=(
    ["freemium"]="Freemium"
    ["basic"]="Basic"
    ["workplace"]="Workplace"
    ["gamer"]="Gamer"
    ["ai"]="AI Developer"
    ["gamer-ai"]="Gamer+AI"
    ["server"]="Server"
)

declare -A EDITION_PRICES=(
    ["freemium"]="FREE"
    ["basic"]="$69"
    ["workplace"]="$49"
    ["gamer"]="$69"
    ["ai"]="$89"
    ["gamer-ai"]="$129"
    ["server"]="$129"
)

print_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║           AEGIS OS ISO BUILDER v${VERSION}                    ║"
    echo "║     Build your custom Aegis OS installation media          ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "\n${BLUE}[STEP $1]${NC} $2"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

check_requirements() {
    print_step "1/6" "Checking requirements..."
    
    local missing=0
    
    # Check if running as root or sudo available
    if [ "$EUID" -ne 0 ]; then
        if ! command -v sudo &> /dev/null; then
            print_error "This script requires sudo or root access"
            exit 1
        fi
        SUDO="sudo"
    else
        SUDO=""
    fi
    
    # Check required tools
    for cmd in debootstrap mksquashfs xorriso; do
        if command -v $cmd &> /dev/null; then
            print_success "$cmd found"
        else
            print_warning "$cmd not found - will install"
            missing=1
        fi
    done
    
    # Check disk space (need at least 15GB)
    local free_space=$(df /tmp --output=avail -B1G 2>/dev/null | tail -1 | tr -d ' ')
    if [ "$free_space" -lt 15 ]; then
        print_error "Need at least 15GB free space in /tmp (have ${free_space}GB)"
        exit 1
    fi
    print_success "Disk space: ${free_space}GB available"
    
    return $missing
}

install_build_tools() {
    print_step "2/6" "Installing build tools..."
    
    if command -v apt-get &> /dev/null; then
        $SUDO apt-get update -qq
        $SUDO apt-get install -y -qq debootstrap squashfs-tools xorriso isolinux syslinux-common wget curl
    elif command -v dnf &> /dev/null; then
        $SUDO dnf install -y debootstrap squashfs-tools xorriso syslinux wget curl
    elif command -v pacman &> /dev/null; then
        $SUDO pacman -S --noconfirm debootstrap squashfs-tools libisoburn syslinux wget curl
    else
        print_error "Unsupported package manager. Please install: debootstrap, squashfs-tools, xorriso, isolinux"
        exit 1
    fi
    
    print_success "Build tools installed"
}

select_edition() {
    echo -e "\n${CYAN}Select Aegis OS Edition:${NC}\n"
    
    local i=1
    local editions=("freemium" "basic" "workplace" "gamer" "ai" "gamer-ai" "server")
    
    for ed in "${editions[@]}"; do
        printf "  %d) %-15s %s\n" $i "${EDITION_NAMES[$ed]}" "${EDITION_PRICES[$ed]}"
        ((i++))
    done
    
    echo ""
    read -p "Enter choice [1-7]: " choice
    
    case $choice in
        1) EDITION="freemium" ;;
        2) EDITION="basic" ;;
        3) EDITION="workplace" ;;
        4) EDITION="gamer" ;;
        5) EDITION="ai" ;;
        6) EDITION="gamer-ai" ;;
        7) EDITION="server" ;;
        *) print_error "Invalid choice"; exit 1 ;;
    esac
    
    print_success "Selected: ${EDITION_NAMES[$EDITION]} (${EDITION_PRICES[$EDITION]})"
}

download_base_system() {
    print_step "3/6" "Downloading Ubuntu base system..."
    echo "This will take 10-30 minutes depending on your internet speed."
    
    mkdir -p "$BUILD_DIR"
    cd "$BUILD_DIR"
    
    # Use debootstrap to get Ubuntu base
    $SUDO debootstrap --arch=amd64 --variant=minbase jammy rootfs http://archive.ubuntu.com/ubuntu/
    
    print_success "Base system downloaded"
}

customize_system() {
    print_step "4/6" "Customizing for ${EDITION_NAMES[$EDITION]} edition..."
    
    local ROOTFS="$BUILD_DIR/rootfs"
    
    # Mount necessary filesystems
    $SUDO mount --bind /dev "$ROOTFS/dev"
    $SUDO mount --bind /dev/pts "$ROOTFS/dev/pts"
    $SUDO mount -t proc proc "$ROOTFS/proc"
    $SUDO mount -t sysfs sysfs "$ROOTFS/sys"
    
    # Copy resolv.conf for network access
    $SUDO cp /etc/resolv.conf "$ROOTFS/etc/resolv.conf"
    
    # Base packages for all editions
    $SUDO chroot "$ROOTFS" apt-get update
    $SUDO chroot "$ROOTFS" apt-get install -y \
        linux-image-generic linux-headers-generic \
        xfce4 xfce4-goodies lightdm \
        firefox thunar-archive-plugin file-roller \
        network-manager network-manager-gnome \
        pulseaudio pavucontrol \
        sudo nano wget curl
    
    # Edition-specific packages
    case $EDITION in
        "freemium")
            print_success "Freemium: Base desktop installed"
            ;;
        "basic")
            $SUDO chroot "$ROOTFS" apt-get install -y \
                libreoffice gimp vlc timeshift clamav gufw
            print_success "Basic: Office, security, backup tools installed"
            ;;
        "workplace")
            $SUDO chroot "$ROOTFS" apt-get install -y \
                libreoffice thunderbird remmina filezilla \
                evolution evolution-ews
            print_success "Workplace: Business tools installed"
            ;;
        "gamer")
            $SUDO chroot "$ROOTFS" apt-get install -y \
                steam-installer lutris gamemode mangohud \
                wine winetricks vulkan-tools mesa-vulkan-drivers
            print_success "Gamer: Gaming tools installed"
            ;;
        "ai")
            $SUDO chroot "$ROOTFS" apt-get install -y \
                python3 python3-pip python3-venv \
                jupyter-notebook code \
                nvidia-driver-535 nvidia-cuda-toolkit
            print_success "AI Developer: ML tools installed"
            ;;
        "gamer-ai")
            $SUDO chroot "$ROOTFS" apt-get install -y \
                steam-installer lutris gamemode mangohud \
                python3 python3-pip nvidia-driver-535
            print_success "Gamer+AI: Gaming and AI tools installed"
            ;;
        "server")
            $SUDO chroot "$ROOTFS" apt-get install -y \
                openssh-server docker.io nginx postgresql \
                fail2ban ufw htop
            print_success "Server: Server packages installed"
            ;;
    esac
    
    # Create Aegis branding
    $SUDO mkdir -p "$ROOTFS/etc/aegis"
    echo "$EDITION" | $SUDO tee "$ROOTFS/etc/aegis/edition" > /dev/null
    echo "$VERSION" | $SUDO tee "$ROOTFS/etc/aegis/version" > /dev/null
    
    # Cleanup
    $SUDO chroot "$ROOTFS" apt-get clean
    $SUDO umount "$ROOTFS/sys" "$ROOTFS/proc" "$ROOTFS/dev/pts" "$ROOTFS/dev" || true
    
    print_success "System customization complete"
}

create_iso() {
    print_step "5/6" "Creating ISO image..."
    
    local ISO_DIR="$BUILD_DIR/iso"
    local ISO_NAME="aegis-${EDITION}.iso"
    
    mkdir -p "$ISO_DIR"/{casper,isolinux,install}
    
    # Create squashfs
    echo "Creating compressed filesystem (this takes a while)..."
    $SUDO mksquashfs "$BUILD_DIR/rootfs" "$ISO_DIR/casper/filesystem.squashfs" \
        -comp xz -Xbcj x86
    
    print_success "Filesystem compressed"
    
    # Copy kernel and initrd
    $SUDO cp "$BUILD_DIR/rootfs/boot/vmlinuz-"* "$ISO_DIR/casper/vmlinuz"
    $SUDO cp "$BUILD_DIR/rootfs/boot/initrd.img-"* "$ISO_DIR/casper/initrd"
    
    # Create isolinux config
    cat > "$ISO_DIR/isolinux/isolinux.cfg" << 'EOF'
DEFAULT live
LABEL live
    menu label ^Start Aegis OS
    kernel /casper/vmlinuz
    append initrd=/casper/initrd boot=casper quiet splash ---
LABEL install
    menu label ^Install Aegis OS
    kernel /casper/vmlinuz
    append initrd=/casper/initrd boot=casper only-ubiquity quiet splash ---
EOF
    
    # Copy isolinux files
    cp /usr/lib/ISOLINUX/isolinux.bin "$ISO_DIR/isolinux/" 2>/dev/null || \
    cp /usr/share/syslinux/isolinux.bin "$ISO_DIR/isolinux/"
    cp /usr/lib/syslinux/modules/bios/*.c32 "$ISO_DIR/isolinux/" 2>/dev/null || \
    cp /usr/share/syslinux/*.c32 "$ISO_DIR/isolinux/" 2>/dev/null || true
    
    # Create ISO
    echo "Building ISO..."
    xorriso -as mkisofs \
        -iso-level 3 \
        -full-iso9660-filenames \
        -volid "AEGIS_OS_${EDITION^^}" \
        -eltorito-boot isolinux/isolinux.bin \
        -eltorito-catalog isolinux/boot.cat \
        -no-emul-boot -boot-load-size 4 -boot-info-table \
        -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin \
        -output "$OUTPUT_DIR/$ISO_NAME" \
        "$ISO_DIR"
    
    print_success "ISO created: $OUTPUT_DIR/$ISO_NAME"
}

cleanup() {
    print_step "6/6" "Cleaning up..."
    
    $SUDO rm -rf "$BUILD_DIR"
    
    print_success "Temporary files removed"
}

show_completion() {
    local ISO_PATH="$OUTPUT_DIR/aegis-${EDITION}.iso"
    local ISO_SIZE=$(du -h "$ISO_PATH" 2>/dev/null | cut -f1)
    
    echo -e "\n${GREEN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║              ISO BUILD COMPLETE!                           ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo "Edition:  ${EDITION_NAMES[$EDITION]}"
    echo "Size:     $ISO_SIZE"
    echo "Location: $ISO_PATH"
    echo ""
    echo -e "${CYAN}Next Steps:${NC}"
    echo "1. Open Balena Etcher (https://balena.io/etcher)"
    echo "2. Select: $ISO_PATH"
    echo "3. Select your USB drive (8GB+ recommended)"
    echo "4. Click 'Flash!'"
    echo "5. Boot from USB to install Aegis OS"
    echo ""
    
    # Try to open Balena Etcher or download page
    if command -v balenaEtcher &> /dev/null; then
        read -p "Open Balena Etcher now? [Y/n]: " open_etcher
        if [ "$open_etcher" != "n" ] && [ "$open_etcher" != "N" ]; then
            balenaEtcher "$ISO_PATH" &
        fi
    else
        echo -e "${YELLOW}Tip: Install Balena Etcher from https://balena.io/etcher${NC}"
    fi
}

# Main
main() {
    print_banner
    
    # Check/install requirements
    if ! check_requirements; then
        install_build_tools
    fi
    
    # Select edition
    select_edition
    
    # Confirm
    echo ""
    read -p "Build ${EDITION_NAMES[$EDITION]} ISO to $OUTPUT_DIR? [Y/n]: " confirm
    if [ "$confirm" = "n" ] || [ "$confirm" = "N" ]; then
        echo "Cancelled."
        exit 0
    fi
    
    # Build
    download_base_system
    customize_system
    create_iso
    cleanup
    
    show_completion
}

# Run
main "$@"
