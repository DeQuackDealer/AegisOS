#!/bin/bash
# Aegis OS Basic Branch - Build Script
# Builds the core foundation (Freemium base)
#
# WARNING: This is raw source. Build requires:
# - Arch Linux or Arch-based system
# - archiso package
# - Python 3.10+
# - Root privileges

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build"
OUTPUT_DIR="${SCRIPT_DIR}/output"

VERSION="1.0.0"
BUILD_DATE=$(date +%Y-%m-%d)
EDITION="basic"

echo "========================================"
echo "  Aegis OS Basic Branch Build System"
echo "  Version: ${VERSION}"
echo "  Date: ${BUILD_DATE}"
echo "========================================"
echo ""

# Check requirements
check_requirements() {
    echo "[1/5] Checking build requirements..."
    
    if [ ! -f /etc/arch-release ]; then
        echo "ERROR: Build requires Arch Linux"
        exit 1
    fi
    
    for cmd in python3 pacman makepkg; do
        if ! command -v "$cmd" &> /dev/null; then
            echo "ERROR: Missing required command: $cmd"
            exit 1
        fi
    done
    
    if [ "$EUID" -ne 0 ]; then
        echo "WARNING: Some build steps require root privileges"
    fi
    
    echo "  Requirements: OK"
}

# Process source files
process_sources() {
    echo "[2/5] Processing source files..."
    
    mkdir -p "${BUILD_DIR}/src"
    
    # Replace build markers in Python files
    for pyfile in "${SCRIPT_DIR}/src/"*.py; do
        if [ -f "$pyfile" ]; then
            filename=$(basename "$pyfile")
            echo "  Processing: $filename"
            
            sed -e "s/%%VERSION%%/${VERSION}/g" \
                -e "s/%%BUILD_DATE%%/${BUILD_DATE}/g" \
                -e "s/%%EDITION%%/${EDITION}/g" \
                "$pyfile" > "${BUILD_DIR}/src/${filename}"
        fi
    done
    
    echo "  Sources processed: OK"
}

# Compile Python to bytecode
compile_python() {
    echo "[3/5] Compiling Python sources..."
    
    # Create compiled directory
    mkdir -p "${BUILD_DIR}/compiled"
    
    # Compile to .pyc
    python3 -m compileall "${BUILD_DIR}/src" -b
    
    # Move compiled files
    find "${BUILD_DIR}/src" -name "*.pyc" -exec mv {} "${BUILD_DIR}/compiled/" \;
    
    echo "  Compilation: OK"
}

# Package for distribution
package() {
    echo "[4/5] Creating distribution package..."
    
    mkdir -p "${OUTPUT_DIR}"
    
    # Create tarball
    PACKAGE_NAME="aegis-basic-${VERSION}.tar.gz"
    tar -czf "${OUTPUT_DIR}/${PACKAGE_NAME}" \
        -C "${BUILD_DIR}" \
        src compiled \
        -C "${SCRIPT_DIR}" \
        configs services
    
    echo "  Package created: ${OUTPUT_DIR}/${PACKAGE_NAME}"
}

# Generate checksums
generate_checksums() {
    echo "[5/5] Generating checksums..."
    
    cd "${OUTPUT_DIR}"
    sha256sum *.tar.gz > SHA256SUMS
    
    echo "  Checksums: OK"
}

# Main build sequence
main() {
    check_requirements
    process_sources
    compile_python
    package
    generate_checksums
    
    echo ""
    echo "========================================"
    echo "  BUILD COMPLETE"
    echo "========================================"
    echo ""
    echo "Output: ${OUTPUT_DIR}"
    echo ""
    echo "To build ISO, use the archiso build system"
    echo "See: https://github.com/DeQuackDealer/AegisOS"
}

# Run
main "$@"
