# in-toto Utility Scripts

This directory contains utility scripts for managing in-toto layouts and keys.

## Scripts

### `generate-intoto-key.py`

Generates an RSA key pair for signing in-toto layouts.

```bash
# Generate default 2048-bit key
./generate-intoto-key.py -k layout-owner-key

# Generate 4096-bit key for production
./generate-intoto-key.py -k layout-owner-key -s 4096
```

**Outputs:**
- `<keyname>` - Private key (PEM format, mode 0600)
- `<keyname>.pub` - Public key (PEM format, mode 0644)

### `update-layout-keys.py`

Updates an in-toto layout file with public key metadata.

```bash
./update-layout-keys.py -l in-toto-layout.json -k layout-owner-key.pub
```

This script:
- Calculates the key ID (SHA256 hash of public key)
- Adds the public key to the layout's `keys` dictionary
- Updates all steps to reference the key ID in their `pubkeys` field

### `sign-layout.py`

Signs an in-toto layout file with a private key.

```bash
# Sign layout in place
./sign-layout.py -l in-toto-layout.json -k layout-owner-key

# Sign to a different output file
./sign-layout.py -l in-toto-layout.json -k layout-owner-key -o signed-layout.json
```

This script:
- Loads the unsigned layout JSON
- Creates an in-toto Metablock with signatures
- Signs it using the provided private key
- Writes the signed layout back to the file

## Typical Workflow

```bash
# 1. Generate keys
./scripts/generate-intoto-key.py -k layout-owner-key

# 2. Update layout with public key
./scripts/update-layout-keys.py -l in-toto-layout.json -k layout-owner-key.pub

# 3. Sign the layout
./scripts/sign-layout.py -l in-toto-layout.json -k layout-owner-key

# 4. Verify (in CI or locally)
in-toto-verify --layout in-toto-layout.json --layout-keys layout-owner-key.pub
```

Or simply use the convenience script:
```bash
./setup-intoto-keys.sh
```

## Requirements

```bash
pip install in-toto cryptography securesystemslib
```

## Security Notes

- **Private keys** (`layout-owner-key`) must NEVER be committed to version control
- **Public keys** (`layout-owner-key.pub`) should be committed for verification
- The scripts use proper file permissions (0600 for private keys)
- All scripts include error handling and validation
