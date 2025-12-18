#!/bin/bash
# Aegis OS Gamer Branch - Build Script
# Builds premium gaming features
#
# WARNING: This is raw source. Build requires:
# - Arch Linux or Arch-based system
# - Basic branch built first
# - Python 3.10+
# - Root privileges for system service installation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build"
OUTPUT_DIR="${SCRIPT_DIR}/output"

VERSION="1.0.0"
BUILD_DATE=$(date +%Y-%m-%d)
EDITION="gamer"

echo "========================================"
echo "  Aegis OS Gamer Branch Build System"
echo "  Version: ${VERSION}"
echo "  Date: ${BUILD_DATE}"
echo "========================================"
echo ""
echo "  PREMIUM FEATURES BUILD"
echo "  License: \$49 lifetime / \$10 annual"
echo ""

# Check requirements
check_requirements() {
    echo "[1/6] Checking build requirements..."
    
    if [ ! -f /etc/arch-release ]; then
        echo "ERROR: Build requires Arch Linux"
        exit 1
    fi
    
    # Check for basic branch
    BASIC_PKG="../basic/output/aegis-basic-${VERSION}.tar.gz"
    if [ ! -f "${BASIC_PKG}" ]; then
        echo "ERROR: Basic branch must be built first"
        echo "Run: cd ../basic && ./build.sh"
        exit 1
    fi
    
    for cmd in python3 pacman makepkg; do
        if ! command -v "$cmd" &> /dev/null; then
            echo "ERROR: Missing required command: $cmd"
            exit 1
        fi
    done
    
    echo "  Requirements: OK"
}

# Extract basic branch
extract_basic() {
    echo "[2/6] Extracting basic branch..."
    
    mkdir -p "${BUILD_DIR}"
    tar -xzf "../basic/output/aegis-basic-${VERSION}.tar.gz" -C "${BUILD_DIR}"
    
    echo "  Basic branch extracted: OK"
}

# Process gamer sources
process_sources() {
    echo "[3/6] Processing gamer source files..."
    
    mkdir -p "${BUILD_DIR}/gamer-src"
    
    # Replace build markers in Python files
    for pyfile in "${SCRIPT_DIR}/src/"*.py; do
        if [ -f "$pyfile" ]; then
            filename=$(basename "$pyfile")
            echo "  Processing: $filename"
            
            sed -e "s/%%VERSION%%/${VERSION}/g" \
                -e "s/%%BUILD_DATE%%/${BUILD_DATE}/g" \
                -e "s/%%EDITION%%/${EDITION}/g" \
                "$pyfile" > "${BUILD_DIR}/gamer-src/${filename}"
        fi
    done
    
    echo "  Gamer sources processed: OK"
}

# Compile Python
compile_python() {
    echo "[4/6] Compiling Python sources..."
    
    mkdir -p "${BUILD_DIR}/gamer-compiled"
    
    python3 -m compileall "${BUILD_DIR}/gamer-src" -b
    find "${BUILD_DIR}/gamer-src" -name "*.pyc" -exec mv {} "${BUILD_DIR}/gamer-compiled/" \;
    
    echo "  Compilation: OK"
}

# Package for distribution
package() {
    echo "[5/6] Creating distribution package..."
    
    mkdir -p "${OUTPUT_DIR}"
    
    PACKAGE_NAME="aegis-gamer-${VERSION}.tar.gz"
    tar -czf "${OUTPUT_DIR}/${PACKAGE_NAME}" \
        -C "${BUILD_DIR}" \
        src compiled gamer-src gamer-compiled \
        -C "${SCRIPT_DIR}" \
        configs services
    
    echo "  Package created: ${OUTPUT_DIR}/${PACKAGE_NAME}"
}

# Generate checksums
generate_checksums() {
    echo "[6/6] Generating checksums..."
    
    cd "${OUTPUT_DIR}"
    sha256sum *.tar.gz > SHA256SUMS
    
    echo "  Checksums: OK"
}

# Main build sequence
main() {
    check_requirements
    extract_basic
    process_sources
    compile_python
    package
    generate_checksums
    
    echo ""
    echo "========================================"
    echo "  GAMER BUILD COMPLETE"
    echo "========================================"
    echo ""
    echo "Output: ${OUTPUT_DIR}"
    echo ""
    echo "Premium features included:"
    echo "  - Dual GPU Rendering"
    echo "  - StreamForge Capture Stack"
    echo "  - 8 Gaming System Services"
    echo "  - Latency FastPath"
    echo "  - VRAM Balancer"
    echo "  - NetBoost Network Optimizer"
    echo "  - Shader Pre-Cache Engine"
    echo "  - Audio Zero-Latency"
    echo "  - Thermal Guard"
    echo ""
    echo "License required: \$49 lifetime / \$10 annual"
}

# Run
main "$@"
