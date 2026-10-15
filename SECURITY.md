# Security boundaries

SC Linux is a development image factory. Its source tests do not qualify it for
production deployment.

## Build and distribution

- Review source before running privileged containers. No Docker socket is mounted
  inside the builder, but privileged mode does not isolate hostile source safely.
- Independently verify IPA CA fingerprints. A certificate obtained through an
  unauthenticated channel is not sufficient evidence for a new trust anchor.
- Images are unsigned by default. Checksums, package manifests, and GitHub artifact
  IDs are not release signatures, an SBOM, or a build-provenance attestation.
- Snapshot repositories freeze security updates. Review the snapshot and rebuild
  and redeploy deliberately; no automatic update or recovery mechanism is provided.

## Provisioning and enrollment

- Protect seed integrity: its SSH key creates a passwordless-sudo administrator.
- Keep installer media under operator control; it provides a root console.
- Issue one OTP for each approved host. Admission is the operator's responsibility;
  the repository has no attestation broker or automatic authorization service.
- An interactive prompt avoids credentials in arguments and shell history. It does
  not protect them from root or a compromised enrollment process.
- Unique keytabs and host keys persist on deployed machines. They must never be
  embedded in the reusable image.

## Boot trust

UKI signing and TPM diagnostics do not authenticate the writable root. Smoke tests
check boot evidence collection and installation, not hardware endorsement keys,
remote attestation policy, or Secure Boot enforcement.

See [verification](docs/verification.md) for what has and has not been exercised.

## Reporting and redistribution

Do not put secrets or sensitive exploitation details in public issues. Before
public distribution, the owner should configure a private vulnerability-reporting
channel and select a license for this repository's original code. This repository
does not currently designate a private reporting contact or grant a license for
its original code. Upstream packages retain their own licenses and notices.
