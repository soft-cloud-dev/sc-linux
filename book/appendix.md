# Reference: where the actual code lives

| Area | Authoritative file |
| --- | --- |
| Source checks | [check notebook](../notebooks/check.ipynb) |
| Trust input validation | [trust notebook](../notebooks/trust.ipynb) |
| Host filesystem and apt snapshot staging | [prepare notebook](../notebooks/prepare.ipynb) |
| mkosi disk and installer recipes | [server configuration](../images/server/mkosi.conf), [installer configuration](../images/installer/mkosi.conf) |
| Container orchestration | [build-inside.sh](../scripts/build-inside.sh) |
| Installer ISO assembly | [make-iso notebook](../notebooks/make-iso.ipynb) |
| Artifact SHA-256 manifests | [artifacts notebook](../notebooks/artifacts.ipynb) |
| Disk usage report | [footprint notebook](../notebooks/footprint.ipynb) |
| QEMU smoke tests | [smoke notebook](../notebooks/smoke.ipynb) |
| NoCloud ISO | [seed notebook](../notebooks/seed.ipynb) |

A kernel and userspace inside the deployed image must work independently of Jupyter. Guest runtime scripts and `lib/scos/core.py` therefore remain normal executables.

## Book maintenance

The chapters are teaching and operator interfaces. Avoid duplicating ISO assembly, cryptographic validation, or disk writes in educational cells: instead, call the tested underlying command and inspect its outputs. Never commit executed notebook outputs, secret material, TPM logs, seed media or enrollment passwords.

Build documentation with `jupyter book build --html` (no execution). Live execution is opt-in in your local JupyterLab environment. For implementation detail and limits consult [architecture](../docs/architecture.md), [verification](../docs/verification.md) and [security](../SECURITY.md).
