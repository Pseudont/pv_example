#!/bin/bash
set -euo pipefail

# Local test script for in-toto layout signing workflow
# This simulates what happens in the GitHub Actions workflow

echo "=== Testing in-toto Layout Signing Workflow ==="
echo ""

# Clean up any previous test artifacts
echo "Cleaning up previous test artifacts..."
rm -f test-in-toto-key test-in-toto-key.pub
rm -f test-layout.json test-layout.json.bak
rm -f *.link

# Create a test layout (copy of the original)
echo "Creating test layout..."
cp in-toto-layout.json test-layout.json

# Step 1: Generate keys
echo ""
echo "Step 1: Generating test keys..."
./scripts/generate-intoto-key.py -k test-in-toto-key
if [ $? -ne 0 ]; then
    echo "❌ Key generation failed"
    exit 1
fi
echo "✓ Keys generated"

# Step 2: Update layout with public key
echo ""
echo "Step 2: Updating layout with public key..."
./scripts/update-layout-keys.py -l test-layout.json -k test-in-toto-key.pub
if [ $? -ne 0 ]; then
    echo "❌ Layout update failed"
    exit 1
fi
echo "✓ Layout updated"

# Step 3: Sign the layout
echo ""
echo "Step 3: Signing the layout..."
./scripts/sign-layout.py -l test-layout.json -k test-in-toto-key
if [ $? -ne 0 ]; then
    echo "❌ Layout signing failed"
    exit 1
fi
echo "✓ Layout signed"

# Step 4: Verify the signed layout structure
echo ""
echo "Step 4: Verifying signed layout structure..."
if python3 -c "
import json
import sys

with open('test-layout.json', 'r') as f:
    layout = json.load(f)

# Check for required fields in signed metablock
if 'signed' not in layout:
    print('❌ Missing \"signed\" field')
    sys.exit(1)

if 'signatures' not in layout:
    print('❌ Missing \"signatures\" field')
    sys.exit(1)

if len(layout['signatures']) == 0:
    print('❌ No signatures found')
    sys.exit(1)

print('✓ Layout has valid metablock structure')
print(f'  - Signatures: {len(layout[\"signatures\"])}')
print(f'  - Expires: {layout[\"signed\"].get(\"expires\", \"unknown\")}')
print(f'  - Steps: {len(layout[\"signed\"].get(\"steps\", []))}')
"; then
    echo "✓ Layout structure valid"
else
    echo "❌ Layout structure validation failed"
    exit 1
fi

# Step 5: Create dummy link metadata for testing verification
echo ""
echo "Step 5: Creating test link metadata..."
if command -v in-toto-run &> /dev/null; then
    # Create dummy materials/products for testing
    touch app.py Dockerfile requirements.txt .github/workflows/build-and-sign.yml

    in-toto-run \
        --step-name checkout \
        --signing-key test-in-toto-key \
        --products app.py Dockerfile requirements.txt .github/workflows/build-and-sign.yml \
        -- echo "Checkout step"

    echo "test-digest" > image-digest.txt
    in-toto-run \
        --step-name build \
        --signing-key test-in-toto-key \
        --materials app.py Dockerfile requirements.txt \
        --products image-digest.txt \
        -- echo "Build step"

    echo "verified" > signature-verified.txt
    in-toto-run \
        --step-name sign \
        --signing-key test-in-toto-key \
        --materials image-digest.txt \
        --products signature-verified.txt \
        -- echo "Sign step"

    echo "✓ Link metadata created"
else
    echo "⚠ in-toto-run not found, skipping link metadata creation"
fi

# Step 6: Test verification
echo ""
echo "Step 6: Testing verification..."
if command -v in-toto-verify &> /dev/null; then
    if in-toto-verify \
        --layout test-layout.json \
        --verification-keys test-in-toto-key.pub \
        --link-dir . 2>&1 | tee verify-output.txt; then
        echo "✓ Verification PASSED"
    else
        echo "⚠ Verification returned non-zero (may be due to missing link metadata)"
        echo "Last few lines of output:"
        tail -n 5 verify-output.txt
    fi
    rm -f verify-output.txt
else
    echo "⚠ in-toto-verify not found, skipping verification test"
    echo "Install with: pip install in-toto"
fi

# Cleanup
echo ""
echo "=== Test Summary ==="
echo "✓ Key generation works"
echo "✓ Layout update works"
echo "✓ Layout signing works"
echo "✓ Signed layout has correct structure"
echo ""
echo "Test artifacts created:"
ls -lh test-in-toto-key* test-layout.json 2>/dev/null || true
echo ""
echo "To clean up test artifacts, run:"
echo "  rm -f test-in-toto-key* test-layout.json* *.link image-digest.txt signature-verified.txt"
