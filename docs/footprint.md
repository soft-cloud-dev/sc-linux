# Understand image size

[Home](../README.md) · [Build](building.md) · [Verification](verification.md)

SC Linux records disk, installer and installed-package sizes after a successful build. The **uncompressed RAW file size is not the same as package size**.

## Read the measurements

Open [`03-inspect.ipynb`](../notebooks/03-inspect.ipynb), or read the raw report:

```sh
cat build/output/footprint.json
head -n 30 build/output/raw/sc-linux.packages-kib.tsv
cat build/output/raw/sc-linux.directories-bytes.tsv
du -h build/output/raw/sc-linux.raw build/output/sc-linux.raw.zst build/output/sc-linux.iso
```

| Measurement | Meaning |
| --- | --- |
| Uncompressed RAW bytes | Whole GPT image: partitions, filesystems and unused space |
| Compressed RAW bytes | zstd-compressed deployment payload |
| ISO bytes | Installer boot files plus compressed RAW |
| Package Installed-Size | Debian estimate in KiB, not actual filesystem blocks |
| Directory bytes | Direct measurement in mkosi's root filesystem before disk layout |

The [`footprint.ipynb`](../notebooks/footprint.ipynb) operation creates the report; the guided inspection notebook verifies artifact hashes and presents its key numbers.

## Existing space-saving choices

The two mkosi definitions disable recommended packages and optional documentation. The ESP is **384 MiB**; the root has a **2 GiB minimum** and `Minimize=guess`. Build finalization removes temporary caches without deleting essential FreeIPA, SSSD, Kerberos, or kernel components. The distributable RAW uses `zstd -T1 -19`.

These settings save space but are **not** proof that the resulting image is smaller or boots after each change.

## Compare a change properly

1. Record baseline `footprint.json` values.
2. Change one package, partition or compression parameter.
3. Rebuild with a new clean output directory.
4. Compare size and build-time results.
5. Run VM smoke tests, root-growth checks, and unsigned reproducibility comparison when relevant.

The existing smoke harness does **not** independently prove that ext4 expands on an 8 GiB target. Do not remove kernel modules, FreeIPA dependencies or packaged Python blindly.
