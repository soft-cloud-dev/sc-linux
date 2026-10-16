# SC Linux

A small **Debian 13 (Trixie) amd64** server image, built with **mkosi 25.3-7**. One build produces a compressed bootable disk image and an installer ISO. FreeIPA enrollment happens **after** each host is provisioned.

**Status:** development. Source checks, image construction, VM boot and real FreeIPA enrollment are separate acceptance stages. Do not assume a successful source check means an image was tested.

## Get started

1. Clone the repository and run source checks.
2. Independently verify the fingerprint of the checked-in public FreeIPA CA, or replace it with your own reviewed CA.
3. Commit any configuration or trust changes.
4. Build the images and run the disposable VM tests.

```sh
git clone https://github.com/soft-cloud-dev/sc-linux.git
cd sc-linux
make check
```

The build requires an **amd64 Linux** machine with Docker, Git, Make, OpenSSL and at least **40 GiB free**. It uses privileged containers. Follow [the build guide](docs/building.md) before running it.

## Learn and operate through notebooks

Open [`notebooks/`](notebooks) in JupyterLab, starting Jupyter from the repository root:

| Start here | What you will do |
| --- | --- |
| [01 · Validate](notebooks/01-validate.ipynb) | Check configuration and run tests |
| [02 · Build](notebooks/02-build.ipynb) | Review inputs and generate RAW + ISO |
| [03 · Inspect](notebooks/03-inspect.ipynb) | Verify hashes, compare sizes |
| [04 · Smoke-test](notebooks/04-smoke.ipynb) | Boot test VMs and review evidence |

The **actual host-side operations** also live in notebooks: [check](notebooks/check.ipynb), [trust](notebooks/trust.ipynb), [prepare](notebooks/prepare.ipynb), [make-iso](notebooks/make-iso.ipynb), [artifacts](notebooks/artifacts.ipynb), [footprint](notebooks/footprint.ipynb), [seed](notebooks/seed.ipynb), and [smoke](notebooks/smoke.ipynb).

You **do not need Jupyter installed to use CI or the Makefile**. Execute any operation with the minimal, Python-standard-library runner:

```sh
bash scripts/notebook.sh notebooks/check.ipynb
make check
```

The notebook is the executable source. The runner evaluates its Python cells in order; it does not execute Markdown or install dependencies. JupyterLab is an optional interface, not part of the deployed OS.

## Open notebooks interactively

JupyterLab is needed only when you want to **explore cells interactively**. Install it in a local development environment, not in the built OS:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install jupyterlab
make lab
```

Run `make lab`, then open `01-validate.ipynb`. This creates **working copies** of the notebooks in ignored `build/notebooks/`, so Jupyter autosave and execution outputs cannot dirty the committed source or block image builds. Repeated launches preserve these copies. To contribute changes, deliberately copy the edited notebook back into `notebooks/`, clear its cell outputs, and commit it. CI and command-line builds continue to use the committed notebooks through `make` and `scripts/notebook.sh`.

## Build and test

After configuring verified CA trust and committing your changes:

```sh
make builder
make images
make smoke
```

Expected outputs in `build/output/`: `sc-linux.raw.zst`, `sc-linux.iso`, `SHA256SUMS`, `artifacts.json`, `footprint.json`, package manifests, and VM logs after smoke testing.

For a step-by-step explanation see [Build](docs/building.md), [Install](docs/installing.md), [Identity](docs/identity.md), [Architecture](docs/architecture.md), [Footprint](docs/footprint.md), and [Verification](docs/verification.md).

**Scope:** UEFI, systemd, cloud-init NoCloud, SSH and native FreeIPA client. Signing is optional. The repository does **not** implement authenticated root, remote attestation, automatic updates, Kubernetes orchestration, or a FreeBSD image. Read [Security](SECURITY.md) before deploying.
