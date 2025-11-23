#!/bin/bash
set -euo pipefail

# in-toto Supply Chain Verification Script
# This script verifies that the container build process followed the defined supply chain policy

echo "=== in-toto Supply Chain Verification ==="

# Check if in-toto is installed
if ! command -v in-toto-verify &> /dev/null; then
    echo "Error: in-toto-verify not found. Install with: pip install in-toto"
    exit 1
fi

# Check if layout file exists
if [ ! -f "in-toto-layout.json" ]; then
    echo "Error: in-toto-layout.json not found"
    exit 1
fi

# Check if link metadata files exist
LINKS_DIR="."
REQUIRED_LINKS=("checkout" "build" "sign")

for step in "${REQUIRED_LINKS[@]}"; do
    if ! ls ${LINKS_DIR}/${step}.*.link 2>/dev/null; then
        echo "Warning: No link metadata found for step: ${step}"
    fi
done

# Run in-toto verification
echo "Verifying supply chain layout..."
in-toto-verify \
    --layout in-toto-layout.json \
    --layout-keys "" \
    --link-dir ${LINKS_DIR}

if [ $? -eq 0 ]; then
    echo "✓ Supply chain verification PASSED"
    echo "All steps were executed according to policy:"
    echo "  1. Code checkout"
    echo "  2. Docker image build"
    echo "  3. Cosign signature verification"
    exit 0
else
    echo "✗ Supply chain verification FAILED"
    echo "The build process did not follow the defined policy"
    exit 1
fi
