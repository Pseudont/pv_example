#!/usr/bin/env python3
"""
Update an in-toto layout with public key information.

This script reads a public key and updates the layout's keys dictionary
and step pubkeys to reference it.
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
    from cryptography.hazmat.backends import default_backend
    from securesystemslib.signer import CryptoSigner
except ImportError as e:
    print(f"Error: Required module not found: {e}", file=sys.stderr)
    print("Install with: pip install cryptography securesystemslib", file=sys.stderr)
    sys.exit(1)


def update_layout_keys(layout_path: Path, public_key_path: Path) -> None:
    """
    Update layout with public key metadata.

    Args:
        layout_path: Path to the layout JSON file
        public_key_path: Path to the public key PEM file
    """
    # We need the private key to create a CryptoSigner to get the correct keyid
    # The public key path should be <name>.pub, so private key is <name>
    private_key_path = public_key_path.with_suffix('')

    try:
        # Load private key to create CryptoSigner (needed for correct keyid)
        with open(private_key_path, 'rb') as f:
            private_pem = f.read()
        private_key = load_pem_private_key(private_pem, password=None, backend=default_backend())

        # Create CryptoSigner to get the keyid that in-toto will use
        signer = CryptoSigner(private_key)

        # Get the public key dict from the signer
        pub_key_dict = signer.public_key.to_dict()
        keyid = signer.public_key.keyid

        # Add keyid to the dict (it's not included in to_dict())
        pub_key = {
            'keyid': keyid,
            **pub_key_dict
        }

    except FileNotFoundError as e:
        print(f"Error: Key file not found: {e}", file=sys.stderr)
        print(f"Note: This script needs both {private_key_path.name} and {public_key_path.name}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to load key: {e}", file=sys.stderr)
        sys.exit(1)

    # Load the layout
    try:
        with open(layout_path, 'r') as f:
            layout = json.load(f)
    except FileNotFoundError:
        print(f"Error: Layout file not found: {layout_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in layout file: {e}", file=sys.stderr)
        sys.exit(1)

    # Update layout with key information
    # The keys dict maps keyid -> key_dict (which also contains keyid)
    layout['keys'] = {keyid: pub_key}
    for step in layout.get('steps', []):
        step['pubkeys'] = [keyid]

    # Write updated layout
    try:
        with open(layout_path, 'w') as f:
            json.dump(layout, f, indent=2)
    except Exception as e:
        print(f"Error: Failed to write layout: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✓ Layout updated with public key")
    print(f"  Key ID: {keyid[:16]}...")


def main():
    parser = argparse.ArgumentParser(
        description="Update in-toto layout with public key information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -l in-toto-layout.json -k layout-owner-key.pub
        """
    )
    parser.add_argument(
        '-l', '--layout',
        type=Path,
        required=True,
        help='Path to the layout JSON file'
    )
    parser.add_argument(
        '-k', '--key',
        type=Path,
        required=True,
        help='Path to the public key PEM file'
    )

    args = parser.parse_args()
    update_layout_keys(args.layout, args.key)


if __name__ == '__main__':
    main()
