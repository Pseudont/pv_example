#!/usr/bin/env python3
"""
Sign an in-toto layout file with a private key.

This script converts an unsigned layout JSON to a signed Metablock format
that can be verified with in-toto-verify.
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from in_toto.models.layout import Layout
    from in_toto.models.metadata import Metablock
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    from securesystemslib.signer import CryptoSigner
except ImportError as e:
    print(f"Error: Required module not found: {e}", file=sys.stderr)
    print("Install with: pip install in-toto cryptography securesystemslib", file=sys.stderr)
    sys.exit(1)


def load_private_key_signer(key_path: Path):
    """
    Load a private key and return a CryptoSigner for the new in-toto API.

    Returns:
        CryptoSigner object for use with Metablock.create_signature()
    """
    # Read and load the PEM private key
    with open(key_path, 'rb') as f:
        pem_data = f.read()

    private_key = load_pem_private_key(pem_data, password=None, backend=default_backend())

    # Create a CryptoSigner (used by in-toto 1.0+)
    return CryptoSigner(private_key)


def sign_layout(layout_path: Path, key_path: Path, output_path: Path = None) -> None:
    """
    Sign an in-toto layout file.

    Args:
        layout_path: Path to the unsigned layout JSON file
        key_path: Path to the private key file
        output_path: Path to write signed layout (defaults to layout_path)
    """
    if output_path is None:
        output_path = layout_path

    # Load the layout
    try:
        with open(layout_path, 'r') as f:
            layout_dict = json.load(f)
    except FileNotFoundError:
        print(f"Error: Layout file not found: {layout_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in layout file: {e}", file=sys.stderr)
        sys.exit(1)

    # Check if this is already a signed metablock or an unsigned layout
    try:
        if 'signed' in layout_dict and 'signatures' in layout_dict:
            # Already a signed metablock, just add another signature
            metablock = Metablock.read(layout_dict)
        else:
            # Unsigned layout - create a Layout object and populate from dict
            # We avoid using Layout.read() to bypass key validation
            from in_toto.models.layout import Step, Inspection

            # Parse steps
            steps = []
            for step_dict in layout_dict.get('steps', []):
                step = Step(**step_dict)
                steps.append(step)

            # Parse inspections
            inspections = []
            for inspect_dict in layout_dict.get('inspect', []):
                inspection = Inspection(**inspect_dict)
                inspections.append(inspection)

            # Create Layout with parsed objects
            layout_obj = Layout(
                steps=steps,
                inspect=inspections,
                keys=layout_dict.get('keys', {}),
                expires=layout_dict.get('expires', '2030-12-31T23:59:59Z')
            )
            # Set _type field if present
            if '_type' in layout_dict:
                layout_obj._type = layout_dict['_type']

            metablock = Metablock(signed=layout_obj)
    except Exception as e:
        print(f"Error: Failed to create layout object: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Load the private key as a signer
    try:
        signer = load_private_key_signer(key_path)
    except FileNotFoundError:
        print(f"Error: Private key not found: {key_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to load private key: {e}", file=sys.stderr)
        sys.exit(1)

    # Sign the layout using the new API
    try:
        metablock.create_signature(signer)
    except Exception as e:
        print(f"Error: Failed to sign layout: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Write the signed layout
    try:
        metablock.dump(str(output_path))
    except Exception as e:
        print(f"Error: Failed to write signed layout: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✓ Layout signed successfully: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Sign an in-toto layout file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sign layout in place
  %(prog)s -l in-toto-layout.json -k layout-owner-key

  # Sign layout to a different file
  %(prog)s -l in-toto-layout.json -k layout-owner-key -o signed-layout.json
        """
    )
    parser.add_argument(
        '-l', '--layout',
        type=Path,
        required=True,
        help='Path to the unsigned layout JSON file'
    )
    parser.add_argument(
        '-k', '--key',
        type=Path,
        required=True,
        help='Path to the private key file'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Path to write signed layout (defaults to input file)'
    )

    args = parser.parse_args()
    sign_layout(args.layout, args.key, args.output)


if __name__ == '__main__':
    main()
