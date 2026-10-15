# Install and provision a host

[README](../README.md) · [Build](building.md) · [Enroll](identity.md)

## Prepare one seed per machine

Choose an inventory-assigned hostname below the configured IPA domain and a
public SSH key. The default domain is `ipa.softcloud.dev`; the IPA server's own
hostname cannot be used for a client.

The seed helper requires `xorriso` and `ssh-keygen`. Install them on the machine
running the helper, or use the builder container.

```sh
python3 scripts/seed.py node01.ipa.softcloud.dev ~/.ssh/id_ed25519.pub build/node01-seed.iso
```

The helper refuses to overwrite an existing seed. It writes NoCloud user-data
and a unique instance ID to an ISO labelled `cidata`.

On the installed system's first boot, attach this seed as a second read-only
CD-ROM. It creates user `scos` with the supplied public key and passwordless sudo.
Root login and SSH password authentication are disabled. There is no shared
recovery password.

Protect the seed's integrity: replacing its public key grants administrator
access. Remove it after initialization and do not reuse it for another host.
Do not provide untrusted cloud-init user-data.

## Choose a deployment path

### Installer ISO

1. Boot `sc-linux.iso` in UEFI mode with the destination disk attached.
2. Inspect the available disks with `lsblk`.
3. Select the whole disk explicitly. Replace the example device below.

```sh
lsblk
scos-install /dev/disk/by-id/YOUR-DISK
```

The installer checks both the compressed and uncompressed payload before writing.
It requires the exact confirmation `ERASE /dev/RESOLVED-DEVICE` shown in its prompt.
It rejects a mounted, mapped, read-only, undersized, or non-disk target, and verifies
the image bytes read back from the disk after writing.

**Installation destroys existing data on the selected disk. It is not a secure erase.**
After completion, remove the installer ISO, attach the per-host seed, and reboot
from the installed disk. The installer provides a root console; keep the media
under operator control.

### Direct RAW deployment

Decompress the disk image, then import it using your hypervisor's disk-image
import operation:

```sh
zstd -d build/output/sc-linux.raw.zst -o build/sc-linux.raw
```

Attach the seed before the first boot. Do not attach multiple copies of this
template as boot disks to one VM: disk and partition UUIDs identify the template,
not the provisioned host.

## First login

Matching Ethernet interfaces (`en*` and `eth*`) use DHCP. The resolver must reach
the IPA domain and the system clock must synchronize before enrollment.

```sh
ssh scos@node01.ipa.softcloud.dev
sudo scos-enroll node01.ipa.softcloud.dev
```

Follow the [enrollment guide](identity.md#enroll-a-provisioned-host) for OTP handling
and post-enrollment checks. Successful SSH access depends on the seed, networking,
and name resolution; local source tests do not establish that those work in your lab.

## Disk and boot limits

- UEFI only; legacy BIOS is not supported.
- The server uses a writable ext4 root of approximately 4 GiB plus a 512 MiB ESP.
- Installing onto a larger disk relocates the backup GPT header but does not grow
  the root partition or filesystem. Expansion is a separate administrative task.
- A TPM-less server can boot; it does not report successful TPM evidence collection.
