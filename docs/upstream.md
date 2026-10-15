# Upstream references

These references were carried forward from the supplied implementation. They describe
upstream interfaces; they are not evidence that this repository has built or booted
an image. Consult the version matching the pinned toolchain when changing it.

- mkosi 25.3 configuration and output formats: https://github.com/systemd/mkosi/blob/v25.3/mkosi/resources/man/mkosi.1.md
- Debian's pinned mkosi package and dependencies: https://packages.debian.org/trixie/mkosi
- mkosi apt sandbox source override behavior: https://github.com/systemd/mkosi/blob/v25.3/mkosi/installer/apt.py
- mkosi Debian repository behavior: https://github.com/systemd/mkosi/blob/v25.3/mkosi/distributions/debian.py
- FreeIPA native client options, including `-W`: https://manpages.debian.org/trixie/freeipa-client/ipa-client-install.1.en.html
- CA trust registration: https://manpages.debian.org/trixie/ca-certificates/update-ca-certificates.8.en.html
- Cloud-init NoCloud datasource: https://cloudinit.readthedocs.io/en/latest/reference/datasources/nocloud.html
- Debian cloud-init unit filenames: https://packages.debian.org/trixie/all/cloud-init/filelist
- systemd PCR semantics: https://systemd.io/TPM2_PCR_MEASUREMENTS/
- QEMU TPM interfaces: https://www.qemu.org/docs/master/specs/tpm.html
- Debian snapshot archive: https://snapshot.debian.org/
- GitHub immutable action references used here: https://github.com/actions/checkout/tree/11bd71901bbe5b1630ceea73d27597364c9af683 and https://github.com/actions/upload-artifact/tree/ea165f8d65b6e75b540449e92b4886f43607fa02
