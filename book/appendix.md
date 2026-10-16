# Reference: where the actual code lives

| Area | Authoritative file |
| --- | --- |
| Source checks | [check notebook](https://github.com/soft-cloud-dev/sc-linux/blob/main/notebooks/check.ipynb) |
| Trust input validation | [trust notebook](https://github.com/soft-cloud-dev/sc-linux/blob/main/notebooks/trust.ipynb) |
| Host filesystem and apt snapshot staging | [prepare notebook](https://github.com/soft-cloud-dev/sc-linux/blob/main/notebooks/prepare.ipynb) |
| mkosi disk and installer recipes | [server configuration](https://github.com/soft-cloud-dev/sc-linux/blob/main/images/server/mkosi.conf), [installer configuration](https://github.com/soft-cloud-dev/sc-linux/blob/main/images/installer/mkosi.conf) |
| Container orchestration | [build-inside.sh](https://github.com/soft-cloud-dev/sc-linux/blob/main/scripts/build-inside.sh) |
| Installer ISO assembly | [make-iso notebook](https://github.com/soft-cloud-dev/sc-linux/blob/main/notebooks/make-iso.ipynb) |
| Artifact SHA-256 manifests | [artifacts notebook](https://github.com/soft-cloud-dev/sc-linux/blob/main/notebooks/artifacts.ipynb) |
| Disk usage report | [footprint notebook](https://github.com/soft-cloud-dev/sc-linux/blob/main/notebooks/footprint.ipynb) |
| QEMU smoke tests | [smoke notebook](https://github.com/soft-cloud-dev/sc-linux/blob/main/notebooks/smoke.ipynb) |
| NoCloud ISO | [seed notebook](https://github.com/soft-cloud-dev/sc-linux/blob/main/notebooks/seed.ipynb) |

A kernel and userspace inside the deployed image must work independently of Jupyter. Guest runtime scripts and `lib/scos/core.py` therefore remain normal executables.

## Book maintenance

The chapters are teaching and operator interfaces. Avoid duplicating ISO assembly, cryptographic validation, or disk writes in educational cells: instead, call the tested underlying command and inspect its outputs. Never commit executed notebook outputs, secret material, TPM logs, seed media or enrollment passwords.

Build documentation with `jupyter book build --html` (no execution). Live execution is opt-in in your local JupyterLab environment. For implementation detail and limits consult [architecture](https://github.com/soft-cloud-dev/sc-linux/blob/main/docs/architecture.md), [verification](https://github.com/soft-cloud-dev/sc-linux/blob/main/docs/verification.md) and [security](https://github.com/soft-cloud-dev/sc-linux/blob/main/SECURITY.md).
