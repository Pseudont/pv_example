# Verify latest image
IMAGE="ghcr.io/pseudont/pv_example:master"
cosign verify ${IMAGE} \
  --certificate-identity-regexp="https://github.com/Pseudont/.*" \
  --certificate-oidc-issuer=https://token.actions.githubusercontent.com

# Show provenance
cosign verify-attestation ${IMAGE} \
  --certificate-identity-regexp="https://github.com/Pseudont/.*" \
  --certificate-oidc-issuer=https://token.actions.githubusercontent.com \
  --type slsaprovenance | jq -r '.payload' | base64 -d | jq .predicate.builder
