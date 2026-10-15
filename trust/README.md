# Public IPA CA

This directory is intentionally missing a CA certificate until the operator
supplies and independently verifies the real trust anchor.

Follow [identity and trust](../docs/identity.md) and use `scripts/trust.py` to create:

| File | Content |
| --- | --- |
| `ipa-ca.crt` | Exactly one public PEM CA certificate |
| `ipa-ca.sha256` | Independently verified SHA-256 of its DER encoding |

Commit both public files after review. Never commit a private key. Image builds
refuse to proceed while either file is absent or invalid.
