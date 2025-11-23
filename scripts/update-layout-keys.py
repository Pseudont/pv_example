#!/usr/bin/env python3
"""
Update an in-toto layout with public key information.

This script reads a public key and updates the layout's keys dictionary
and step pubkeys to reference it.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

try:
    from cryptography.hazmat.primitives.serialization import load_pem_public_key
    from cryptography.hazmat.backends import default_backend
except ImportError as e:
    print(f"Error: Required module not found: {e}", file=sys.stderr)
    print("Install with: pip install cryptography", file=sys.stderr)
    sys.exit(1)


def update_layout_keys(layout_path: Path, public_key_path: Path) -> None:
    """
    Update layout with public key metadata.

    Args:
        layout_path: Path to the layout JSON file
        public_key_path: Path to the public key PEM file
    """
    # Load the public key
    try:
        pem_data = public_key_path.read_bytes()
        pub_key_obj = load_pem_public_key(pem_data, backend=default_backend())
        pem_str = pem_data.decode('utf-8')
    except FileNotFoundError:
        print(f"Error: Public key not found: {public_key_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to load public key: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate keyid (sha256 hash of public key)
    keyid = hashlib.sha256(pem_data).hexdigest()

    # Create public key dict in securesystemslib format (v1.0+ format)
    # The key dict must include the keyid field
    pub_key = {
        'keyid': keyid,
        'keytype': 'rsa',
        'scheme': 'rsassa-pss-sha256',
        'keyval': {'public': pem_str}
    }

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
