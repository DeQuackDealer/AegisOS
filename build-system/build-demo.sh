#!/bin/bash
#
# Aegis OS Demo Build Script
# Creates a demo ISO structure (not actually bootable)
# For demonstration and documentation purposes
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
EDITION=${1:-freemium}
BUILD_DIR="./work/$EDITION"
OUTPUT_DIR="./output"
ISO_FILE="$OUTPUT_DIR/aegis-$EDITION-demo.iso"

# Banner
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}       AEGIS OS BUILD SYSTEM (DEMO)        ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check edition
case $EDITION in
    freemium|basic|gamer|ai|server)
        echo -e "${GREEN}✓${NC} Building edition: ${YELLOW}$EDITION${NC}"
        ;;
    *)
        echo -e "${RED}✗${NC} Invalid edition: $EDITION"
        echo "Usage: $0 [freemium|basic|gamer|ai|server]"
        exit 1
        ;;
esac

# Create directories
echo -e "\n${BLUE}[1/5]${NC} Creating build directories..."
mkdir -p $BUILD_DIR/{iso,chroot,squashfs}
mkdir -p $OUTPUT_DIR
mkdir -p logs

# Simulate base system creation
echo -e "${BLUE}[2/5]${NC} Creating base system..."
sleep 1
cat > $BUILD_DIR/chroot/aegis-release << EOF
Aegis OS $EDITION Edition
Version: 1.0.0
Build Date: $(date)
EOF
echo -e "${GREEN}✓${NC} Base system created"

# Simulate package installation
echo -e "${BLUE}[3/5]${NC} Installing packages..."
case $EDITION in
    freemium)
        echo "  → Installing XFCE desktop environment"
        echo "  → Installing basic applications"
        PACKAGES=50
        SIZE="1.5 GB"
        ;;
    basic)
        echo "  → Installing XFCE desktop environment"
        echo "  → Installing 500+ professional applications"
        echo "  → Installing development tools"
        PACKAGES=500
        SIZE="3.5 GB"
        ;;
    gamer)
        echo "  → Installing gaming platforms (Steam, Lutris)"
        echo "  → Installing Wine/Proton compatibility"
        echo "  → Installing 52+ gaming tools"
        PACKAGES=550
        SIZE="4.5 GB"
        ;;
    ai)
        echo "  → Installing ML frameworks (TensorFlow, PyTorch)"
        echo "  → Installing CUDA toolkit"
        echo "  → Installing Jupyter notebooks"
        PACKAGES=600
        SIZE="6.0 GB"
        ;;
    server)
        echo "  → Installing server stack (Nginx, PostgreSQL)"
        echo "  → Installing Kubernetes/Docker"
        echo "  → Installing monitoring tools"
        PACKAGES=300
        SIZE="3.0 GB"
        ;;
esac
sleep 2
echo -e "${GREEN}✓${NC} Installed $PACKAGES packages"

# Simulate filesystem compression
echo -e "${BLUE}[4/5]${NC} Creating compressed filesystem..."
touch $BUILD_DIR/squashfs/filesystem.squashfs
echo -e "${GREEN}✓${NC} Filesystem compressed"

# Create demo ISO structure
echo -e "${BLUE}[5/5]${NC} Generating ISO image..."
mkdir -p $BUILD_DIR/iso/{boot,isolinux,casper,EFI/boot}

# Create boot configuration
cat > $BUILD_DIR/iso/isolinux/isolinux.cfg << EOF
DEFAULT aegis
PROMPT 0
TIMEOUT 50

LABEL aegis
  MENU LABEL Aegis OS $EDITION
  KERNEL /casper/vmlinuz
  APPEND initrd=/casper/initrd.gz boot=casper quiet splash ---
EOF

# Create README in ISO
cat > $BUILD_DIR/iso/README.txt << EOF
=========================================
      AEGIS OS $EDITION EDITION
=========================================

This is a demo ISO structure for Aegis OS.

Edition: $EDITION
Size: $SIZE
Packages: $PACKAGES

For actual bootable ISOs, please visit:
https://aegis-os.com/downloads

Installation Guide:
https://aegis-os.com/install-guide

=========================================
EOF

# Create demo ISO file (just a marker file)
touch $ISO_FILE
echo "DEMO ISO - $EDITION Edition - Size: $SIZE" > $ISO_FILE

# Create build log
LOG_FILE="logs/build-$EDITION-$(date +%Y%m%d-%H%M%S).log"
cat > $LOG_FILE << EOF
Aegis OS Build Log
==================
Edition: $EDITION
Date: $(date)
Status: SUCCESS
Size: $SIZE
Packages: $PACKAGES
Output: $ISO_FILE
==================
EOF

# Success message
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}         BUILD COMPLETED SUCCESSFULLY!      ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "Edition:  ${YELLOW}$EDITION${NC}"
echo -e "Size:     ${YELLOW}$SIZE${NC}"
echo -e "Packages: ${YELLOW}$PACKAGES${NC}"
echo -e "ISO:      ${YELLOW}$ISO_FILE${NC}"
echo -e "Log:      ${YELLOW}$LOG_FILE${NC}"
echo ""
echo -e "${BLUE}Note:${NC} This is a demo build for documentation."
echo -e "      For actual bootable ISOs, a full build"
echo -e "      environment with proper tools is required."
echo ""