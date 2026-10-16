# Install and provision a machine

[Home](../README.md) · [Build](building.md) · [Identity](identity.md)

**Warning:** writing an OS image destroys data on the selected disk. Confirm the disk ID and keep installer media under operator control.

## 1. Create a host-specific seed

Each host needs its **own** NoCloud seed, containing a hostname and SSH public key. The default domain is `ipa.softcloud.dev`. The seed must not contain a FreeIPA password, OTP or private key.

```sh
bash scripts/notebook.sh notebooks/seed.ipynb node01.ipa.softcloud.dev ~/.ssh/id_ed25519.pub build/node01-seed.iso
```

Requires `xorriso` and `ssh-keygen`. The tool refuses to overwrite an existing seed. The `cidata` ISO creates a `scos` user with that public key and passwordless sudo at first boot. Protect it: replacing the public key changes who gets administrator access.

## 2. Install the OS

**Option A — installer ISO:** boot `build/output/sc-linux.iso` in **UEFI mode** and inspect available disks.

```sh
lsblk
scos-install /dev/disk/by-id/YOUR-DISK
```

The installer resolves and validates the selected **whole disk**. It checks payload hashes, prompts for a disk-specific `ERASE` confirmation, writes the disk and reads back the image. Installation is destructive, **not** a secure erase. Remove installer media when it finishes.

**Option B — direct RAW import:** decompress the image and import it with your hypervisor.

```sh
zstd -d build/output/sc-linux.raw.zst -o build/sc-linux.raw
```

Do not use the ISO as a RAW disk or run two active clones of the template on the same storage path.

## 3. First boot and SSH

Attach the host's seed as a **second read-only CD-ROM** before first boot. Networking uses DHCP for standard Ethernet interface names.

After boot, verify DNS resolution and time synchronization, then log in:

```sh
ssh scos@node01.ipa.softcloud.dev
```

After provisioning, remove the seed and keep it securely archived or destroy it. Do not reuse it for another machine.

## 4. Enroll in FreeIPA

Create a host enrollment OTP through your approved administrative process, then on the host run:

```sh
sudo scos-enroll node01.ipa.softcloud.dev
```

Enter the **one-time host OTP** at the native FreeIPA client prompt. Never place it in commands, environment variables, notebook outputs or seed media. See [Identity](identity.md) for post-enrollment checks.

## Platform boundaries

UEFI is required. The server starts with a **384 MiB ESP** and an ext4 root with a **2 GiB minimum**; the finished root size depends on the build. Partition/filesystem growth on larger targets must be tested separately. A TPM-less host may boot, but cannot furnish TPM measurement evidence.
