#!/usr/bin/env python3
"""
Generate RSA key pair for in-toto layout signing.

Creates a private/public key pair in PEM format compatible with in-toto.
"""

import argparse
import sys
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
except ImportError as e:
    print(f"Error: Required module not found: {e}", file=sys.stderr)
    print("Install with: pip install cryptography", file=sys.stderr)
    sys.exit(1)


def generate_key_pair(private_key_path: Path, public_key_path: Path, key_size: int = 2048) -> None:
    """
    Generate an RSA key pair for in-toto signing.

    Args:
        private_key_path: Path to write the private key
        public_key_path: Path to write the public key
        key_size: RSA key size in bits (default: 2048)
    """
    # Check if keys already exist
    if private_key_path.exists() or public_key_path.exists():
        print("Error: Key files already exist. Remove them first or use different paths.", file=sys.stderr)
        if private_key_path.exists():
            print(f"  - {private_key_path}", file=sys.stderr)
        if public_key_path.exists():
            print(f"  - {public_key_path}", file=sys.stderr)
        sys.exit(1)

    # Generate RSA key pair
    print(f"Generating {key_size}-bit RSA key pair...")
    try:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
    except Exception as e:
        print(f"Error: Failed to generate key: {e}", file=sys.stderr)
        sys.exit(1)

    # Serialize private key
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Serialize public key
    public_key = private_key.public_key()
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Write keys to files
    try:
        private_key_path.write_bytes(pem_private)
        private_key_path.chmod(0o600)  # Restrict permissions
        print(f"✓ Private key: {private_key_path} (mode 0600)")

        public_key_path.write_bytes(pem_public)
        public_key_path.chmod(0o644)
        print(f"✓ Public key:  {public_key_path}")
    except Exception as e:
        print(f"Error: Failed to write key files: {e}", file=sys.stderr)
        # Cleanup on failure
        private_key_path.unlink(missing_ok=True)
        public_key_path.unlink(missing_ok=True)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate RSA key pair for in-toto layout signing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate default key pair
  %(prog)s -k layout-owner-key

  # Generate 4096-bit key pair
  %(prog)s -k layout-owner-key -s 4096
        """
    )
    parser.add_argument(
        '-k', '--key',
        type=Path,
        required=True,
        help='Base name for key files (will create <key> and <key>.pub)'
    )
    parser.add_argument(
        '-s', '--size',
        type=int,
        default=2048,
        choices=[2048, 3072, 4096],
        help='RSA key size in bits (default: 2048)'
    )

    args = parser.parse_args()

    private_key_path = args.key
    public_key_path = args.key.with_suffix('.pub')

    generate_key_pair(private_key_path, public_key_path, args.size)

    print("\nWARNING: Keep the private key secure and never commit it to version control!")
    print(f"         Add '{private_key_path.name}' to .gitignore")


if __name__ == '__main__':
    main()
