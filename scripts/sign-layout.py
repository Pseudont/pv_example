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
    from securesystemslib import interface
except ImportError as e:
    print(f"Error: Required module not found: {e}", file=sys.stderr)
    print("Install with: pip install in-toto securesystemslib", file=sys.stderr)
    sys.exit(1)


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

    # Load the unsigned layout
    try:
        with open(layout_path, 'r') as f:
            layout_dict = json.load(f)
    except FileNotFoundError:
        print(f"Error: Layout file not found: {layout_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in layout file: {e}", file=sys.stderr)
        sys.exit(1)

    # Create a Metablock with the layout
    try:
        layout_obj = Layout.read(layout_dict)
        metablock = Metablock(signed=layout_obj)
    except Exception as e:
        print(f"Error: Failed to create layout object: {e}", file=sys.stderr)
        sys.exit(1)

    # Load and verify the private key
    try:
        key = interface.import_rsa_privatekey_from_file(str(key_path))
    except FileNotFoundError:
        print(f"Error: Private key not found: {key_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to load private key: {e}", file=sys.stderr)
        sys.exit(1)

    # Sign the layout
    try:
        metablock.sign(key)
    except Exception as e:
        print(f"Error: Failed to sign layout: {e}", file=sys.stderr)
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
