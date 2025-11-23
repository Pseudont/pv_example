# Provenance Validation Example with in-toto

This repository demonstrates a complete supply chain security implementation using:
- **Sigstore/Cosign**: For keyless container image signing and SLSA provenance attestation
- **in-toto**: For supply chain policy enforcement and verification

## Overview

The CI/CD pipeline builds a containerized Flask application, signs it with Sigstore, creates provenance attestations, and enforces a supply chain policy using in-toto.

## Supply Chain Steps

The in-toto layout enforces three critical steps:

1. **Checkout**: Verifies that source code files (app.py, Dockerfile, requirements.txt) are present
2. **Build**: Ensures the Docker build uses the checked-out source files and produces an image digest
3. **Sign**: Confirms the image was signed with Cosign and the signature was verified

Each step creates link metadata that records:
- **Materials**: Input artifacts consumed by the step
- **Products**: Output artifacts produced by the step

## Verification

The supply chain is verified at two levels:

### 1. Cosign Verification
```bash
# Verify image signature
cosign verify ghcr.io/pseudont/pv_example:master \
  --certificate-identity-regexp="https://github.com/Pseudont/.*" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com"

# Verify SLSA provenance attestation
cosign verify-attestation ghcr.io/pseudont/pv_example:master \
  --certificate-identity-regexp="https://github.com/Pseudont/.*" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  --type slsaprovenance
```

### 2. in-toto Verification
```bash
# Download link metadata from GitHub Actions artifacts
# Then run verification script
pip install in-toto
./verify-supply-chain.sh
```

The `in-toto-verify` tool checks that:
- All required steps were executed
- Each step used the correct input materials
- Each step produced the expected output products
- Steps were performed in the correct order

## Files

- `in-toto-layout.json`: Supply chain policy definition
- `verify-supply-chain.sh`: Automated verification script
- `.github/workflows/build-and-sign.yml`: CI/CD pipeline with in-toto integration
- `CLAUDE.md`: Developer documentation

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py

# Build Docker image
docker build -t pv_example .
docker run -p 8080:8080 pv_example
```

## How It Works

1. **GitHub Actions triggers** on push to master
2. **Code checkout** → in-toto records source files
3. **Docker build** → Multi-platform image built and pushed to ghcr.io
4. **in-toto records build** → Saves image digest as product
5. **Cosign signs image** → Keyless signing via OIDC
6. **Cosign attests provenance** → SLSA provenance attached to image
7. **Signature verification** → Cosign verifies the signature
8. **in-toto records sign step** → Verification result saved as product
9. **Supply chain verification** → `in-toto-verify` checks all steps complied with policy
10. **Artifacts uploaded** → Link metadata saved for offline verification

## Security Guarantees

- **Image integrity**: Cosign signature proves image hasn't been tampered with
- **Provenance**: SLSA attestation shows who built the image, from what source, and when
- **Supply chain compliance**: in-toto layout ensures the build followed required steps
- **Transparency**: All signatures and attestations are publicly verifiable via Rekor transparency log
