#!/bin/bash
# Aegis OS ISO Build Script
# This script builds REAL, BOOTABLE ISOs using archiso
# Must be run on Arch Linux with archiso installed

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_DIR="$SCRIPT_DIR/archiso/profiles/releng"
WORK_DIR="$SCRIPT_DIR/work"
OUTPUT_DIR="$SCRIPT_DIR/output"
VERSION="${AEGIS_VERSION:-2.0.0}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${CYAN}[BUILD]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

show_usage() {
    echo "Aegis OS ISO Builder"
    echo ""
    echo "Usage: $0 [OPTIONS] [EDITION]"
    echo ""
    echo "Editions:"
    echo "  freemium              - Free edition (default)"
    echo "  basic                 - Basic edition (\$19)"
    echo "  gamer                 - Gamer edition (\$49)"
    echo "  gamer-passwordless    - Gamer edition (TESTING ONLY - no login security)"
    echo "  workplace             - Workplace edition"
    echo "  aidev                 - AI Developer edition"
    echo "  server                - Server edition"
    echo ""
    echo "Options:"
    echo "  -h, --help      Show this help"
    echo "  -c, --clean     Clean work directory before build"
    echo "  -v, --version   Set version (default: $VERSION)"
    echo "  -o, --output    Output directory (default: $OUTPUT_DIR)"
    echo ""
    echo "Requirements:"
    echo "  - Arch Linux or Arch-based system"
    echo "  - archiso package installed"
    echo "  - Root privileges"
    echo ""
    echo "Example:"
    echo "  sudo $0 gamer"
    echo "  sudo $0 --clean --version 2.1.0 basic"
}

check_requirements() {
    log "Checking requirements..."
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        error "This script must be run as root"
        echo "Try: sudo $0 $*"
        exit 1
    fi
    
    # Check if archiso is installed
    if ! command -v mkarchiso &> /dev/null; then
        error "archiso is not installed"
        echo "Install with: sudo pacman -S archiso"
        exit 1
    fi
    
    # Check if we're on Arch Linux
    if [ ! -f /etc/arch-release ]; then
        warn "Not running on Arch Linux - build may fail"
    fi
    
    success "Requirements check passed"
}

prepare_edition() {
    local edition="$1"
    log "Preparing $edition edition..."
    
    # Create edition-specific profile
    local edition_profile="$WORK_DIR/profile-$edition"
    rm -rf "$edition_profile"
    cp -r "$PROFILE_DIR" "$edition_profile"
    
    # Apply edition-specific packages
    local pkg_file="$SCRIPT_DIR/archiso/packages/${edition}.txt"
    if [ -f "$pkg_file" ]; then
        cat "$pkg_file" >> "$edition_profile/packages.x86_64"
        log "Added packages from $pkg_file"
    fi
    
    # Apply edition-specific overlay
    local overlay_dir="$SCRIPT_DIR/overlays/$edition"
    if [ -d "$overlay_dir" ]; then
        cp -r "$overlay_dir"/* "$edition_profile/airootfs/" 2>/dev/null || true
        log "Applied overlay from $overlay_dir"
    fi
    
    # Apply common overlay
    local common_overlay="$SCRIPT_DIR/overlays/common"
    if [ -d "$common_overlay" ]; then
        cp -r "$common_overlay"/* "$edition_profile/airootfs/" 2>/dev/null || true
        log "Applied common overlay"
    fi
    
    # Set edition in os-release
    sed -i "s/NAME=\"Aegis OS\"/NAME=\"Aegis OS ${edition^}\"/" "$edition_profile/airootfs/etc/os-release"
    echo "VARIANT=\"${edition}\"" >> "$edition_profile/airootfs/etc/os-release"
    echo "VARIANT_ID=\"${edition}\"" >> "$edition_profile/airootfs/etc/os-release"
    
    # Update profiledef.sh with edition name
    sed -i "s/iso_name=\"aegis-os\"/iso_name=\"aegis-${edition}\"/" "$edition_profile/profiledef.sh"
    
    # Set executable permissions on all scripts
    chmod +x "$edition_profile/airootfs/usr/local/bin/"* 2>/dev/null || true
    
    echo "$edition_profile"
}

build_iso() {
    local edition="$1"
    local edition_profile
    
    edition_profile=$(prepare_edition "$edition")
    
    log "Building $edition ISO with mkarchiso..."
    log "Profile: $edition_profile"
    log "Work directory: $WORK_DIR/$edition"
    log "Output directory: $OUTPUT_DIR"
    
    mkdir -p "$OUTPUT_DIR"
    mkdir -p "$WORK_DIR/$edition"
    
    # Build the ISO using mkarchiso
    export AEGIS_VERSION="$VERSION"
    
    mkarchiso -v \
        -w "$WORK_DIR/$edition" \
        -o "$OUTPUT_DIR" \
        "$edition_profile"
    
    # Find the generated ISO
    local iso_file
    iso_file=$(ls -t "$OUTPUT_DIR"/aegis-${edition}-*.iso 2>/dev/null | head -1)
    
    if [ -z "$iso_file" ]; then
        error "ISO file not found after build"
        exit 1
    fi
    
    # Rename to standard format
    local final_name="aegis-${edition}-${VERSION}.iso"
    mv "$iso_file" "$OUTPUT_DIR/$final_name"
    
    # Generate checksums
    log "Generating checksums..."
    cd "$OUTPUT_DIR"
    sha256sum "$final_name" > "${final_name}.sha256"
    sha512sum "$final_name" > "${final_name}.sha512"
    md5sum "$final_name" > "${final_name}.md5"
    
    # Create manifest
    cat > "${final_name%.iso}.json" <<EOF
{
    "name": "Aegis OS ${edition^}",
    "edition": "$edition",
    "version": "$VERSION",
    "filename": "$final_name",
    "size": $(stat -c%s "$final_name"),
    "sha256": "$(cat ${final_name}.sha256 | cut -d' ' -f1)",
    "sha512": "$(cat ${final_name}.sha512 | cut -d' ' -f1)",
    "md5": "$(cat ${final_name}.md5 | cut -d' ' -f1)",
    "build_date": "$(date -Iseconds)",
    "arch": "x86_64"
}
EOF
    
    success "Built: $OUTPUT_DIR/$final_name"
    success "Size: $(du -h "$final_name" | cut -f1)"
    success "SHA256: $(cat ${final_name}.sha256 | cut -d' ' -f1)"
}

clean_work() {
    log "Cleaning work directory..."
    rm -rf "$WORK_DIR"
    success "Work directory cleaned"
}

# Parse arguments
EDITION="freemium"
CLEAN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -c|--clean)
            CLEAN=true
            shift
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        freemium|basic|gamer|gamer-passwordless|workplace|aidev|server|gamer-ai)
            EDITION="$1"
            shift
            ;;
        *)
            error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║       Aegis OS ISO Build System            ║${NC}"
echo -e "${CYAN}║       Building REAL Bootable ISOs          ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════╝${NC}"
echo ""

check_requirements

if [ "$CLEAN" = true ]; then
    clean_work
fi

log "Building edition: $EDITION"
log "Version: $VERSION"
log "Output: $OUTPUT_DIR"
echo ""

build_iso "$EDITION"

echo ""
success "Build complete!"
echo ""
echo "ISO location: $OUTPUT_DIR/aegis-${EDITION}-${VERSION}.iso"
echo ""
echo "To test in VirtualBox/QEMU:"
echo "  - Create new VM with 4GB+ RAM"
echo "  - Enable EFI in VM settings"
echo "  - Boot from the generated ISO"
echo ""
