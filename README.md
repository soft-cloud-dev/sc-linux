# SC Linux

Build a small Debian-based SCOS server image with a native FreeIPA client.

**Debian 13 · amd64 · systemd · UEFI · mkosi 25.3-7**

SC Linux produces a bootable disk image and an installer ISO from the same
server definition. Each deployed host receives its own identity, SSH keys,
and FreeIPA enrollment credentials.

> **Development status:** source tests pass. Image builds, VM boots, and live
> FreeIPA enrollment still need validation. A verified public IPA CA is required
> before an image can be built. See [verification](docs/verification.md).

## Start here

| Task | Guide |
| --- | --- |
| Build the RAW image and installer ISO | [Building](docs/building.md) |
| Install a machine and configure SSH access | [Installation](docs/installing.md) |
| Configure trust and enroll in FreeIPA | [Identity](docs/identity.md) |
| Understand the image layout and build flow | [Architecture](docs/architecture.md) |
| Run checks and understand their limits | [Verification](docs/verification.md) |
| Change the code or configuration | [Contributing](CONTRIBUTING.md) |

## Check the source

Source checks need Python 3.11+, OpenSSL, Bash, and Make. They do not need Docker,
an IPA server, or a CA certificate.

```sh
git clone https://github.com/soft-cloud-dev/sc-linux.git
cd sc-linux
make check
```

To build images, follow [the build guide](docs/building.md): configure the real
CA, commit the source, then run `make builder`, `make images`, and `make smoke`
on an amd64 Linux host with Docker. Run `make help` to list commands.

## Outputs

All final outputs go to `build/output/` by default.

| File | Purpose |
| --- | --- |
| `sc-linux.raw.zst` | Compressed GPT disk image for direct deployment |
| `sc-linux.iso` | UEFI installer containing the same disk image |
| `SHA256SUMS`, `artifacts.json` | Artifact checksums and sizes |
| Manifests and metadata | Package versions, source commit, and builder identity |
| `tests/` | Boot logs and results after a smoke-test run |

## Scope

The server uses a writable ext4 root and DHCP networking. Provisioning uses
per-host NoCloud media; enrollment uses the standard FreeIPA client's interactive
one-time-password prompt. TPM measurements are diagnostic evidence.

Secure Boot signing is optional. Remote attestation, an authenticated root,
automatic updates, Kubernetes, and FreeBSD are outside this repository's scope.
Read [the security boundaries](SECURITY.md) before deploying or distributing images.
