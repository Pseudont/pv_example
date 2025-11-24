# Provenance Validation Example with in-toto

This repository demonstrates a complete supply chain security implementation using:
- **Sigstore/Cosign**: For keyless container image signing and SLSA provenance attestation
- **PortSwigger Dastardly**: For DAST (Dynamic Application Security Testing)
- **in-toto**: For supply chain policy enforcement and verification

## ⚠️ Security Warning

**This application contains intentional security vulnerabilities for DAST testing purposes.**

The Flask application includes vulnerabilities such as:
- Cross-Site Scripting (XSS)
- SQL Injection patterns
- Open Redirect
- Information Disclosure
- Missing Security Headers
- Debug mode enabled

**DO NOT deploy this to production or expose it to the public internet.** This is strictly for CI/CD security pipeline demonstration purposes.

## Overview

The CI/CD pipeline builds a containerized Flask application, performs DAST scanning with Dastardly to detect vulnerabilities, signs it with Sigstore, creates provenance attestations, and enforces a supply chain policy using in-toto.

## Supply Chain Steps

The in-toto layout enforces four critical steps:

1. **Checkout**: Verifies that source code files (app.py, Dockerfile, requirements.txt) are present
2. **Build**: Ensures the Docker build uses the checked-out source files and produces an image digest
3. **DAST Scan**: Confirms security testing was performed with Dastardly before signing
4. **Sign**: Confirms the image was signed with Cosign and the signature was verified

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

The in-toto layout must be signed to ensure its integrity. The workflow automatically generates ephemeral keys during CI/CD runs.

For local verification:
```bash
# Download link metadata and public key from GitHub Actions artifacts
# Install in-toto
pip install in-toto

# Run verification script (requires layout-owner-key.pub)
./verify-supply-chain.sh
```

The `in-toto-verify` tool checks that:
- The layout signature is valid (using layout-owner-key.pub)
- All required steps were executed
- Each step used the correct input materials
- Each step produced the expected output products
- Steps were performed in the correct order

#### Optional: Pre-generate Keys for Production

For production deployments, generate and sign the layout beforehand:
```bash
# Install dependencies
pip install in-toto cryptography

# Generate keys and sign layout
./setup-intoto-keys.sh

# This creates:
# - layout-owner-key (private - DO NOT COMMIT)
# - layout-owner-key.pub (public - commit this)
# - Signed in-toto-layout.json
```

## Files

- `in-toto-layout.json`: Supply chain policy definition
- `verify-supply-chain.sh`: Automated verification script
- `setup-intoto-keys.sh`: Script to generate keys and sign the layout
- `.github/workflows/build-and-sign.yml`: CI/CD pipeline with in-toto integration
- `CLAUDE.md`: Developer documentation
- `.gitignore`: Prevents committing private keys

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py

# Build Docker image
docker build -t pv_example .
docker run -p 8080:8080 pv_example

# Run with DAST scanning
./run-local-dast.sh
# Report will be saved to ./dastardly-output/dastardly-report.xml
```

## How It Works

1. **GitHub Actions triggers** on push to master
2. **Code checkout** → in-toto records source files
3. **Docker build** → Multi-platform image built and pushed to ghcr.io
4. **in-toto records build** → Saves image digest as product
5. **DAST scanning** → Dastardly scans running container for vulnerabilities
6. **in-toto records DAST scan** → Saves scan results as product
7. **Cosign signs image** → Keyless signing via OIDC (only after security testing)
8. **Cosign attests provenance** → SLSA provenance attached to image
9. **Signature verification** → Cosign verifies the signature
10. **in-toto records sign step** → Verification result saved as product
11. **Supply chain verification** → `in-toto-verify` checks all steps complied with policy
12. **Artifacts uploaded** → Link metadata and DAST reports saved for offline verification

## Security Guarantees

- **Vulnerability Detection**: Dastardly DAST scanning identifies security flaws before signing
- **Image integrity**: Cosign signature proves image hasn't been tampered with
- **Provenance**: SLSA attestation shows who built the image, from what source, and when
- **Supply chain compliance**: in-toto layout ensures the build followed required steps including security testing
- **Transparency**: All signatures and attestations are publicly verifiable via Rekor transparency log
- **Security as a gate**: Images are only signed after passing DAST scans
