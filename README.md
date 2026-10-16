# SC Linux

A Debian 13 (`amd64`) server image built with mkosi. One build produces a compressed UEFI disk image and an installer ISO. Hosts are provisioned with cloud-init and enrolled in FreeIPA after installation.

**Development status:** source checks, image builds, VM boot tests and live FreeIPA enrollment are separate verification stages. See [verification](docs/verification.md) for what each stage proves.

## Start here

Clone the repository and validate the source. These checks need Python 3.11+, Git, Make, Bash and OpenSSL; they do not need Docker or Jupyter.

```sh
git clone https://github.com/soft-cloud-dev/sc-linux.git
cd sc-linux
make check
```

To build images, use an **amd64 Linux host** with Docker and at least **40 GiB free**. Follow the [build guide](docs/building.md) to review configuration, independently verify the public FreeIPA CA and commit your changes before building. Builds use privileged containers.

```sh
make builder
make images
make smoke
```

The main outputs are `build/output/sc-linux.raw.zst` and `build/output/sc-linux.iso`, accompanied by checksums, size reports and VM logs. See the [output reference](docs/building.md#4-inspect-and-boot-test).

## Choose a workflow

| Goal | Start here |
| --- | --- |
| Build from the command line | [Build guide](docs/building.md) |
| Learn the build step by step | [Nine-chapter Jupyter Book](book/index.md) |
| Run or edit notebooks locally | [Notebook guide](docs/notebooks.md) |
| Install a machine and configure SSH | [Installation guide](docs/installing.md) |
| Configure CA trust and enroll a host | [FreeIPA identity](docs/identity.md) |
| Understand or change the implementation | [Architecture](docs/architecture.md) · [Contributing](CONTRIBUTING.md) |

Jupyter is optional. Make and CI execute the canonical operation notebooks through a Python-standard-library runner. The installed OS does not include Jupyter.

## Commands

| Command | Purpose |
| --- | --- |
| `make` | Show available commands |
| `make check` | Run unit tests and source checks |
| `make builder` | Create the Docker build toolchain |
| `make images` | Build the RAW disk and installer ISO |
| `make smoke` | Boot RAW clones, install the ISO and boot the result |
| `make repro` | Compare two fresh unsigned builds byte for byte |
| `make lab` / `make book-lab` | Open operational notebooks / book chapters |
| `make book` | Render the book in strict mode without executing cells |

## Scope

The image includes systemd, cloud-init NoCloud, SSH and a native FreeIPA client. EFI signing is optional. Authenticated root, remote attestation, automatic updates, Kubernetes orchestration and FreeBSD images are not implemented.

Read [Security](SECURITY.md) before deployment. The [documentation index](docs/README.md) also covers image size, upstream references and historical changes.
