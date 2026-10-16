# Verification

[README](../README.md) · [Build](building.md) · [Security](../SECURITY.md)

## Source validation

The readability rewrite was checked on 2026-10-16. `make check` passes **23 tests**
and the source/shell checks. The supplied archive's 18 tests remain covered.
An independent reviewer reproduced the passing suite and found no blocking
regressions in the rewrite. Local documentation links and anchors, both workflow
YAML files, Python formatting, and all three guest command help entrypoints were
also checked.

| Check | What it establishes |
| --- | --- |
| Identity and enrollment tests | Explicit realm, hostname rules, safe native-client arguments, IPA configuration checks |
| CA tests | Correct fingerprint, public CA requirement, rejection of leaf certificates and private keys |
| Artifact tests | Missing/empty artifacts and size/hash mismatches are rejected |
| Installer tests | Unsafe disk descriptions are rejected; readback checks the exact payload prefix |
| Seed tests | Bootstrap configuration includes a public key and no enrollment password |
| Staging test | Both relocated overlays receive the shared package, executable commands, metadata, and appropriate server trust/configuration |
| CLI tests | Host tools import without executing their commands; public `--help` works without build inputs |
| Smoke-harness tests | Required inputs, evidence markers, machine-ID format, and diagnostic-only authorization state |
| Source checks | Configuration, both overlays, pinned action references, Python syntax, and shell syntax |

These are source-level tests. Installer readback tests use memory streams, not a
physical disk. Staging tests create a temporary CA fixture, not the deployment CA.
No test private key is committed.

## Deliberately blocked preflight

```sh
python3 scripts/check.py --require-trust
```

This must fail in the initial checkout because the real IPA CA and fingerprint
have not been supplied. That failure is expected; creating a placeholder CA would
hide the missing deployment trust.

## Image acceptance

A size-optimized build additionally requires inspection of `footprint.json`,
the size-ranked guest package list, and confirmation that the root filesystem
can grow on the 8 GiB installer target. The updated smoke harness requires
more than 6 GiB of root filesystem capacity after installation, in addition
to successful boot and unique machine identity. It does not verify the GPT
partition extents directly, and still requires a full image build to pass.


On a supported build host, `make smoke` is designed to:

1. Boot two disposable RAW clones and collect guest boot evidence.
2. Require different initialized machine IDs.
3. Boot the installer ISO with a blank virtual disk and run installation.
4. Boot that disk without the ISO, require a third machine ID and a
   root filesystem capacity exceeding 6 GiB.
5. Write logs and a success record only after the required markers are observed.

Use `make repro` for an independent byte comparison of two unsigned builds.
A successful smoke run does not imply a successful reproducibility comparison.

## Not qualified by this rewrite

The authoring environment has no Docker or QEMU, and the supplied repository has
no real IPA CA. The following were not executed here:

- Builder creation, package resolution, or mkosi image construction.
- RAW/ISO VM boot, disk installation, or installed-system boot.
- Double-build byte reproducibility.
- Real NoCloud provisioning, live FreeIPA enrollment, HBAC, or sudo policy.
- Secure Boot enforcement, physical TPM checks, or remote attestation.

Do not describe the generated OS as boot-tested or production-ready until the
corresponding integration checks have run. GitHub's **Validate** workflow covers
source checks; **Build Linux** is a separate manual workflow requiring the real CA.
