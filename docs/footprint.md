# Image footprint

[README](../README.md) · [Build](building.md) · [Verify](verification.md)

SC Linux builds an amd64 Debian 13 disk template and a UEFI installer ISO.
Both are made from the same server image. The ISO carries the compressed RAW
image, so reductions to the RAW's compressed payload usually affect the ISO
too. The uncompressed disk size is not the installed package size.

## Current size controls

| Control | Behavior |
| --- | --- |
| `WithRecommends=no` | Skip Debian recommended packages in both mkosi images |
| `WithDocs=no` | Do not install optional package docs/man pages; preserve copyright files |
| 384 MiB ESP | Fixed UEFI partition; must still fit the complete UKI |
| 2 GiB root minimum | `Minimize=guess` measures space required for the copied root |
| Root growth | `systemd-repart` partition resize followed by `scos-grow-root.service` for ext4 growth |
| Postinstall cleanup | Remove disposable apt lists/logs and Python bytecode, not SSSD runtime dependencies |
| `zstd -T1 -19` | Compress the distributable RAW; single-threaded for deterministic parameters |

The built root's exact size is data-dependent and can exceed 2 GiB.
FreeIPA, SSSD, Kerberos, kernel modules, and required guest firmware are not
arbitrarily removed. In particular, the kernel metapackage and native client
packages are preserved.

Do not run `zerofree` on a mounted ext4 filesystem, remove individual kernel
modules without boot tests, or delete packaged Python modules/tests blindly.
The reproducibility comparison must also pass after any filesystem-level
rewriting. The installer tests check SHA-256 over the entire RAW payload.

## Inspect a build

Build only from a clean commit, as described in [building](building.md), then
inspect the output files:

```sh
cat build/output/footprint.json
head -n 30 build/output/raw/sc-linux.packages-kib.tsv
cat build/output/raw/sc-linux.directories-bytes.tsv
du -h build/output/raw/sc-linux.raw build/output/sc-linux.raw.zst build/output/sc-linux.iso
```

`scripts/footprint.py` records uncompressed RAW bytes, compressed RAW bytes,
ISO bytes, installer UKI bytes, compression ratio, and 30 largest packages.
The guest package data comes from `dpkg-query` in the image finalization step.
`Installed-Size` is an estimated package allocation in KiB, not a filesystem
block count. The directory sizes are measured separately before the root
filesystem and partition allocation are included.

The separate `builder-packages.tsv` describes the Docker builder, not the
packages on the deployed machine.

## Acceptance requirements

1. Confirm the RAW and ISO are built successfully from the pinned snapshot.
2. Record the exact values in `footprint.json`; compare baseline and candidate.
3. Run `make smoke` to boot two RAW clones, install and boot from ISO, and
   assert that the installed root filesystem grew beyond 6 GiB on an 8 GiB disk.
4. Inspect root partition dimensions and verify a subsequent reboot stays
   healthy; the smoke harness checks filesystem capacity, not partition extents.
5. Run `make repro` for the exact unsigned candidate before declaring
   byte-level reproducibility.

The source tests verify smoke assertions but do not boot an OS. Image-build
acceptance and root growth remain unverified until the manual Build Linux
workflow is run on this branch. The ESP allocation change also requires
confirming room for the current and future UKI.

Compression level 19 is a tradeoff: it spends additional builder CPU time
to reduce distribution bytes. Benchmark this against the baseline `-10`.
Do not assume improvement without comparing actual artifact sizes and runtimes.
