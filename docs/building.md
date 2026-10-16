# Build your first image

[Home](../README.md) · [Install](installing.md) · [Verification](verification.md)

This guide builds **two files from one server definition**: a compressed RAW disk for a hypervisor, and an ISO that installs the same disk image.

## Before you start

Use an **amd64 Linux host**, not Docker Desktop. Install Docker, Git, Make, Python 3.11+ and OpenSSL. Reserve at least **40 GiB** disk space. You need a verified **public** FreeIPA CA. The build uses privileged Docker and requires a clean, committed Git checkout.

The exact Debian snapshot and mkosi package are declared in [`config/build.json`](../config/build.json). Identity is in [`config/identity.json`](../config/identity.json).

## 1. Verify the FreeIPA CA

Obtain the CA certificate and confirm its **DER SHA-256 fingerprint through an independent trusted channel**. Replace the example values below.

```sh
bash scripts/notebook.sh notebooks/trust.ipynb /secure/path/ipa-ca.crt --sha256 VERIFIED_DER_SHA256
make check
git add trust/ipa-ca.crt trust/ipa-ca.sha256
git commit -m "Configure public IPA CA"
```

Do not commit private keys or an invented trust anchor. For more context see [Identity](identity.md).

## 2. Validate and create the builder

```sh
make check
make builder
```

`make check` verifies notebooks, unit tests, configuration and shell syntax without building an image. `make builder` creates a local Docker toolchain from the reviewed snapshot. It records its ID in `build/builder.id`.

## 3. Produce the images

```sh
make images
```

The build stages the server files, makes a bootable RAW disk, compresses it with zstd, hashes it, builds the installer UKI and wraps that in a UEFI ISO. The output directory must be **empty**. By default it is `build/output/`.

For a second build, provide a different destination:

```sh
bash scripts/build.sh build/run-02
```

For a cell-by-cell build in JupyterLab, activate your JupyterLab virtual environment and run `make lab`. Open `02-build.ipynb` from `build/notebooks/`. Working copies are Git-ignored so saved notebook outputs cannot violate the clean-tree build requirement.

## 4. Inspect and boot-test

```sh
make smoke
```

The disposable VM tests boot two RAW clones, run the ISO installer against a blank virtual disk, and boot the result. Logs and `smoke.json` are written under `build/output/tests/`.

Open [`03-inspect.ipynb`](../notebooks/03-inspect.ipynb) for hashes and size measurements or [`04-smoke.ipynb`](../notebooks/04-smoke.ipynb) to examine the VM test results.

| Output | Meaning |
| --- | --- |
| `sc-linux.raw.zst` | Compressed RAW disk image |
| `sc-linux.iso` | UEFI installer containing the compressed disk |
| `raw/sc-linux.raw` | Uncompressed disk used for VM tests |
| `artifacts.json` / `SHA256SUMS` | Byte sizes and SHA-256 |
| `footprint.json` | Disk/ISO/package size report |
| `payload.json` | Hashes embedded in the installer |
| `tests/` | VM logs and smoke result |

## Optional: EFI signing and reproducibility

The CI build is unsigned. To sign locally, store `private.key` and `certificate.pem` in a protected directory **outside the repository** and use:

```sh
SCOS_SIGNING_DIR=/secure/efi-signing make images
```

Firmware trust must be configured separately. A signed UKI does **not** authenticate the writable ext4 root.

For byte-for-byte comparison of two independently built **unsigned** images, use `make repro` with clean output directories. This is not proof of a fully hermetic build, and it does not replace testing.

## Important limitations

The project pins an apt snapshot, so security updates are not automatic. Changes to the snapshot, package list, kernel or mkosi version need new builds and verification. A successful `make check` is **not** proof that the RAW boots, the installer works, or FreeIPA enrollment succeeds.

## Troubleshooting

- **Git working tree is dirty:** commit source edits, and use `make lab` to run ignored notebook copies instead of tracked files.
- **CA verification fails:** check the certificate fingerprint through an independent trusted channel; do not use a placeholder CA for build outputs.
- **Output already exists:** specify a fresh directory under `build/`, or move earlier outputs elsewhere.
- **Docker or VM boot fails:** use supported amd64 Linux and check Docker privileges. QEMU falls back to software emulation when KVM is unavailable.
