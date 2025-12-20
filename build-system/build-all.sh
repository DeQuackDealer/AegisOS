#!/bin/bash
# Build all Aegis OS editions

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="${AEGIS_VERSION:-2.0.0}"

EDITIONS=("freemium" "basic" "gamer")

echo "Building all Aegis OS editions..."
echo "Version: $VERSION"
echo ""

for edition in "${EDITIONS[@]}"; do
    echo "=========================================="
    echo "Building: $edition"
    echo "=========================================="
    "$SCRIPT_DIR/build.sh" --version "$VERSION" "$edition"
    echo ""
done

echo "All editions built successfully!"
ls -lh "$SCRIPT_DIR/output/"*.iso
