# Build images

[README](../README.md) · [Install](installing.md) · [Verify](verification.md)

## Requirements

Use an amd64 Linux host with Docker, Git, Make, Python 3.11+, and OpenSSL.
Reserve at least 40 GiB of disk space; two-build comparisons require more.
The builder needs privileged containers and working mount namespaces.
Docker Desktop is not qualified. VM tests use KVM when accessible and TCG otherwise.

The selected toolchain and package snapshot are in [config/build.json](../config/build.json).
The image identity is in [config/identity.json](../config/identity.json).

## 1. Configure trust

Obtain the real public IPA CA certificate and independently verify its SHA-256
certificate fingerprint through a trusted administrator. The helper expects a
hash of the certificate's DER bytes, not a hash of the PEM file.

Replace both example arguments before running this block:

```sh
python3 scripts/trust.py /secure/path/ipa-ca.crt --sha256 YOUR_VERIFIED_CERTIFICATE_SHA256
make check
git add trust/ipa-ca.crt trust/ipa-ca.sha256
git commit -m "Configure verified IPA CA trust"
```

Only the public certificate and its fingerprint belong in Git. See
[identity and trust](identity.md) for the exact configuration and enrollment model.

## 2. Build and test

Run from a clean checkout with all source changes committed:

```sh
make builder
make images
make smoke
```

`make builder` resolves the base container tag to a digest, builds the toolchain,
and records its image ID. `make images` uses that builder to create the server
RAW, compress it, embed its digest in the installer, and assemble the ISO.
`make smoke` boots disposable clones and exercises ISO installation.

The output directory must be empty. Keep earlier builds and select a new output
location when needed:

```sh
bash scripts/build.sh build/run-02
bash scripts/smoke.sh build/run-02
```

Custom output paths should remain under ignored `build/` or outside the checkout.
Otherwise the next build will detect uncommitted artifacts and refuse to run.

## 3. Inspect outputs

| Path under `build/output/` | Contents |
| --- | --- |
| `sc-linux.raw.zst` | Compressed server image |
| `sc-linux.iso` | Installer UKI and compressed server payload |
| `raw/sc-linux.raw` | Uncompressed template used by smoke tests |
| `raw/`, `installer/` | mkosi output, including package manifests |
| `raw/sc-linux.packages-kib.tsv` | Guest packages sorted by dpkg Installed-Size (KiB) |
| `raw/sc-linux.directories-bytes.tsv` | Major guest directory sizes in bytes |
| `footprint.json` | RAW/ISO sizes, compression savings, and top packages |
| `SHA256SUMS`, `artifacts.json` | Final artifact hashes and sizes |
| `payload.json` | Expected compressed and uncompressed payload hashes |
| `build-config.json` | Build configuration |
| `builder.id`, `builder-base.txt`, `builder-packages.tsv` | Builder provenance |
| `source-commit.txt`, `source-date-epoch.txt` | Source revision and timestamp |
| `tests/` | Smoke logs and `smoke.json` after a successful run |

Run `make images` before inspecting guest sizes. See the [footprint guide](footprint.md)
for measurements, limits, and optimization acceptance criteria.

Checksums detect corruption. They do not authenticate a download when an attacker
can replace both the images and their checksum file.

## Optional: sign the EFI images

Provide `private.key` and `certificate.pem` in a protected directory outside the
repository. The builder mounts it read-only and disables automatic firmware key
enrollment.

```sh
SCOS_SIGNING_DIR=/secure/efi-signing make images
```

Provision the matching trust in the target firmware separately. A signed UKI
does not authenticate the writable root filesystem. The default CI build is unsigned.

## Repeat a reviewed build

To reuse a previously reviewed base container digest:

```sh
SCOS_BASE_IMAGE=debian@sha256:YOUR_REVIEWED_DIGEST make builder
```

Keep or export the resulting local builder image. `make repro` uses the same
builder and clean source commit for two independent unsigned builds:

```sh
make repro
```

It compares the complete RAW and ISO bytes and fails on any difference. Its
`build/repro-a/` and `build/repro-b/` output directories must be empty before the
run. Unset `SCOS_SIGNING_DIR` first. Fixed timestamps and partition seeds support
repeatability; a successful comparison is still required to demonstrate it.

The base tag and host kernel are not fully pinned by the repository. This is
not a hermetic-build claim.

## GitHub Actions

- **Validate** runs source tests on pushes, pull requests, and manual dispatch.
- **Build Linux** runs only by manual dispatch on `main`. Commit the real CA first.
- The build workflow runs source checks, image construction, and VM smoke tests.
  Its optional reproducibility input adds two unsigned builds.
- Images upload only after required checks pass. Failed boot logs are preserved
  when available. No release is created automatically.

Actions are pinned to commit SHAs and repository permissions are read-only.
The privileged builder never runs on a pull-request trigger. Review the source
before dispatching it.

## Update the snapshot

Both build-time and deployed apt repositories remain on the selected Debian
snapshot, including security and updates suites. Archive signatures remain
required; expiry checking is disabled for the intentionally historical snapshot.

There are no automatic security updates. Advance the snapshot deliberately,
rebuild, run the checks, and redeploy. In-place kernel upgrades are not qualified:
the project does not yet provide a UKI update/signing workflow or A/B recovery.
