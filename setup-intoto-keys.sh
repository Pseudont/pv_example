#!/bin/bash
set -euo pipefail

# in-toto Layout Key Generation and Signing Script
# This script generates RSA keys and signs the in-toto layout

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== in-toto Layout Setup ==="

# Check if required Python packages are installed
if ! python3 -c "import in_toto, cryptography" 2>/dev/null; then
    echo "Installing required packages..."
    python3 -m pip install --user in-toto cryptography securesystemslib || \
    pip install --user in-toto cryptography securesystemslib || \
    pip3 install --user in-toto cryptography securesystemslib
fi

# Generate layout owner keys if they don't exist
if [ ! -f "layout-owner-key" ] || [ ! -f "layout-owner-key.pub" ]; then
    echo "Generating layout owner keys..."
    "${SCRIPT_DIR}/scripts/generate-intoto-key.py" -k layout-owner-key
    echo ""
else
    echo "✓ Layout owner keys already exist"
fi

# Update layout with public key and sign it
if [ -f "in-toto-layout.json" ]; then
    # Create backup of original layout
    if [ ! -f "in-toto-layout.json.bak" ]; then
        cp in-toto-layout.json in-toto-layout.json.bak
        echo "✓ Created backup: in-toto-layout.json.bak"
    fi

    echo "Updating layout with public key..."
    "${SCRIPT_DIR}/scripts/update-layout-keys.py" \
        -l in-toto-layout.json \
        -k layout-owner-key.pub

    echo "Signing in-toto layout..."
    "${SCRIPT_DIR}/scripts/sign-layout.py" \
        -l in-toto-layout.json \
        -k layout-owner-key

    echo ""
    echo "Setup complete! Files:"
    echo "  ✓ layout-owner-key (private key - keep secure!)"
    echo "  ✓ layout-owner-key.pub (public key - use for verification)"
    echo "  ✓ in-toto-layout.json (signed layout)"
    echo ""
    echo "IMPORTANT:"
    echo "  - NEVER commit 'layout-owner-key' to version control"
    echo "  - Commit 'layout-owner-key.pub' and signed 'in-toto-layout.json'"
else
    echo "Error: in-toto-layout.json not found"
    exit 1
fi
