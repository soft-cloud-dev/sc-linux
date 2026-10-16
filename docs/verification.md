# What has been verified?

[Home](../README.md) · [Build](building.md) · [Security](../SECURITY.md)

There are **four distinct verification levels**. Passing one does not imply that later levels passed.

| Level | Command | What it proves |
| --- | --- | --- |
| 1 · Source | `make check` | Python tests, notebook syntax, mkosi configuration, CA validation where configured, shell syntax |
| 2 · Build | `make images` | mkosi produced both expected artifacts; does not prove they boot |
| 3 · VM acceptance | `make smoke` | Two RAW clones boot with unique IDs; ISO installation and installed boot reach expected markers |
| 4 · Live deployment | Operator procedure | Actual cloud-init, SSH, FreeIPA enrollment, HBAC/sudo and domain revocation policies |

For level 1 you can also open [`01-validate.ipynb`](../notebooks/01-validate.ipynb). Tests use temporary CA fixtures; these are **not** deployment CAs.

## Required trust preflight

```sh
bash scripts/notebook.sh notebooks/check.ipynb --require-trust
```

This fails if the required public IPA CA is absent or fails certificate and fingerprint validation. It cannot establish that an independent trust review took place: the operator must verify the fingerprint through a trusted channel before building. Never bypass the preflight with a placeholder certificate.

## After a successful build

Inspect `build/output/SHA256SUMS`, `artifacts.json` and `footprint.json`. Execute the [artifact inspection notebook](../notebooks/03-inspect.ipynb). Checksums detect local corruption; they do not authenticate an attacker-controlled image distribution channel.

Run `make smoke` and inspect `build/output/tests/` and `smoke.json`. Root growth on larger disks and Secure Boot enforcement are not included in the existing smoke checks.

`make repro` compares two independently built **unsigned** RAW and ISO artifacts byte-for-byte. It is a separate requirement, not an automatic consequence of passing smoke tests.

## Work not proven by source tests

Source checks do **not** establish successful Docker/mkosi image construction, VM boots, actual FreeIPA enrollment, Secure Boot enforcement, root integrity, remote attestation, or reproducible builds.

| GitHub Actions workflow | Trigger | Purpose |
| --- | --- | --- |
| **Validate** | Push, pull request or manual dispatch | Run `make check` |
| **Jupyter Book** | Push, pull request or manual dispatch | Render static HTML in strict mode without executing cells |
| **Build Linux** | Manual dispatch on `main` | Build images and run VM acceptance; optionally compare unsigned builds |

**Build Linux** uses privileged containers and requires the real CA and an operator trust review.

Report test outcomes for the exact commit and artifact. Do not label the project production-ready on source-test evidence alone.
