#!/bin/bash
set -euo pipefail

# in-toto Layout Key Generation and Signing Script
# This script generates RSA keys and signs the in-toto layout

echo "=== in-toto Layout Setup ==="

# Check if in-toto is installed
if ! command -v in-toto-sign &> /dev/null; then
    echo "Installing in-toto..."
    python3 -m pip install --user in-toto || pip install --user in-toto || pip3 install --user in-toto
fi

# Generate layout owner keys if they don't exist
if [ ! -f "layout-owner-key" ] || [ ! -f "layout-owner-key.pub" ]; then
    echo "Generating layout owner keys..."
    python3 << 'EOF'
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import json
import hashlib

# Generate RSA key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Serialize private key in PEM format
pem_private = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Serialize public key
public_key = private_key.public_key()
pem_public = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Write keys to files (in-toto format expects no .pem extension for signing)
with open('layout-owner-key', 'wb') as f:
    f.write(pem_private)

with open('layout-owner-key.pub', 'wb') as f:
    f.write(pem_public)

print('✓ Keys generated successfully')
EOF

    chmod 600 layout-owner-key
    chmod 644 layout-owner-key.pub
else
    echo "✓ Layout owner keys already exist"
fi

# Sign the layout
if [ -f "in-toto-layout.json" ]; then
    echo "Signing in-toto layout..."

    # Create backup of original layout
    cp in-toto-layout.json in-toto-layout.json.bak

    # Sign the layout using in-toto-sign
    in-toto-sign -f in-toto-layout.json -k layout-owner-key

    echo "✓ Layout signed successfully"
    echo ""
    echo "Files created:"
    echo "  - layout-owner-key (private key - keep secure!)"
    echo "  - layout-owner-key.pub (public key - use for verification)"
    echo "  - in-toto-layout.json (signed layout)"
    echo ""
    echo "IMPORTANT: Add layout-owner-key to .gitignore (private key should NOT be committed)"
    echo "           The public key (layout-owner-key.pub) can be committed for verification"
else
    echo "Error: in-toto-layout.json not found"
    exit 1
fi
