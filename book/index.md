# Build SC Linux, one action at a time

SC Linux builds a Debian 13 (`amd64`) UEFI server disk and an installer ISO using `mkosi`. This book explains each decision, runs one bounded action at a time, and checks the result before moving on.

**What you will produce:** `sc-linux.raw.zst` (deployable compressed disk) and `sc-linux.iso` (UEFI installer), plus size reports, hashes and disposable VM boot evidence.

## How to use this book

Follow the nine chapters in the left navigation. Each executable chapter has the same flow: **Goal → Prerequisites → Action → Check → Next**. Execute the code cells **locally in JupyterLab**, not on a public website. Use `make book-lab` for ignored working copies, so notebook autosaves cannot dirty the committed source. Notebook actions may access Docker, build privileged images or modify local outputs.

The book is a **guided operator interface** to the tested build pipeline, not a second implementation. Generate documentation with `jupyter book build --html` **without `--execute`**. The existing `make` and `notebooks/*.ipynb` commands remain the canonical automation and CI implementation.

## Safety and reproducibility

- **Do not** run untrusted code using privileged Docker.
- The build requires a trusted public FreeIPA CA; verify its DER SHA-256 fingerprint via an independent channel.
- Source checks, completed image builds, VM boot tests and live FreeIPA enrollment are separate milestones.
- Individual cells print what they are about to do. The imaging and installer stages are destructive to their own output directories, and disk installation is destructive to the selected target.

## Starting point

Clone the repository, follow [Environment](01-environment.ipynb), then complete the remaining chapters in order. The book uses the existing build pipeline rather than redefining lower-level image assembly logic.
