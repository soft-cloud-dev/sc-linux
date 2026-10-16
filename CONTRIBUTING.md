# Contributing to SC Linux

[Home](README.md) · [Architecture](docs/architecture.md) · [Verification](docs/verification.md)

## Choose the right file

| Change | Edit |
| --- | --- |
| A build or verification operation | `notebooks/<operation>.ipynb` |
| Guided OS-building chapters | `book/*.ipynb` and `book/*.md` |
| Compact operational notebooks | `notebooks/01-*` to `04-*` |
| Docker or mkosi orchestration | `scripts/*.sh`, `Dockerfile` |
| OS packages, boot settings or partition layout | `images/*/mkosi.conf` and `mkosi.repart/` |
| Files installed in the OS | `images/*/overlay/` |
| Runtime checks used by installed commands | `lib/scos/core.py` |
| FreeIPA domain or build baseline | `config/identity.json` or `config/build.json` |

The notebooks are the **canonical host-side Python sources**, not copies of `scripts/*.py`. The runner in `scripts/notebook.sh` executes them without Jupyter, so the exact notebook cells are used in CI.

Run canonical operational notebooks with `make lab`; run Jupyter Book chapters with `make book-lab` (ignored working copies). Render the book with `make book-html` without notebook execution.

Run interactive operational notebooks with `make lab`. It creates working copies in ignored `build/notebooks/` so execution counters and saved outputs never dirty the committed source. To contribute, copy reviewed edits back into `notebooks/`, clear cell outputs, and commit the canonical version.

Keep each notebook easy to read from top to bottom: goal, prerequisites, visible arguments, focused cells, and checks. Put import-safe helpers before the final guarded command cell. Do not commit generated outputs, secrets, private keys, kernel traces, or host credentials. Avoid hidden notebook state and unreviewed network access.

## Test before opening a PR

```sh
make check
```

This runs the Python unit tests, checks all notebook code-cell syntax, validates configuration and shell scripts, and verifies pinned action references. For image changes, also run `make builder`, `make images` and `make smoke` on supported amd64 Linux. Use `make repro` for deterministic-build work.

**Important:** some Python files remain deliberately: installed guest commands depend on `lib/scos/core.py`, and Python regression tests remain under `tests/`. The deployed image must never require Jupyter.

## Security and license

The image builder uses privileged Docker. Import only independently verified public IPA CA certificates. Protect seed media and signing keys. See [SECURITY.md](SECURITY.md).

A source repository is not automatically licensed for redistribution. The project owner must choose a license for original code; upstream dependencies retain their existing licenses.
