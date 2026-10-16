# Contributing to SC Linux

[Home](README.md) · [Architecture](docs/architecture.md) · [Verification](docs/verification.md)

## Choose the right file

| Change | Edit |
| --- | --- |
| Host-side validation, staging, packaging or VM tests | Named operation in `notebooks/*.ipynb` |
| Step-by-step teaching chapters | `book/*.ipynb` and `book/*.md` |
| Compact operational walkthrough | `notebooks/01-*` through `04-*` |
| Docker or mkosi orchestration | `scripts/*.sh`, `Dockerfile` |
| OS packages, boot settings or partition layout | `images/*/mkosi.conf` and `images/server/mkosi.repart/` |
| Files installed in the OS | `images/*/overlay/` |
| Shared validation and installed-command helpers | `lib/scos/core.py` |
| FreeIPA identity or build baseline | `config/identity.json` or `config/build.json` |
| Task guides | `docs/` |

Named operation notebooks are the canonical host-side Python sources. `scripts/notebook.sh` executes their cells directly in Make and CI. Keep build logic there; guided notebooks should call the underlying operations rather than duplicate them. Guest commands and Python regression tests remain ordinary files because they must work without Jupyter.

## Edit notebooks

Follow the [notebook guide](docs/notebooks.md) for setup, working copies and copying reviewed edits back to source. Use `make lab` for operational notebooks or `make book-lab` for teaching chapters.

Keep each notebook readable from top to bottom: goal, prerequisites, visible arguments, focused cells and checks. Put import-safe helpers before the final guarded command cell. Avoid hidden notebook state and unreviewed network access.

Do not commit generated outputs, credentials, private keys, keytabs, kernel traces or seed media. Clear code-cell outputs and execution counts before committing notebooks.

## Verify your changes

```sh
make check
```

This runs unit tests, notebook syntax and structure checks, local documentation-link checks, configuration validation, shell syntax checks and pinned-action checks.

| Change | Additional verification |
| --- | --- |
| Book content or configuration | Install `requirements-book.txt`, then run `make book` |
| Image inputs or build pipeline | On supported amd64 Linux, run `make builder`, `make images` and `make smoke` |
| Deterministic-build behavior | Run `make repro` |
| Provisioning or identity | Test the affected workflow in a real deployment |

Image builds require a clean, committed source tree. In your pull request, state what changed and which checks actually ran. Keep source-test results separate from build, boot and live-enrollment evidence.

## Security and license

The image builder uses privileged Docker. Import only independently verified public IPA CA certificates. Protect seed media and signing keys. See [Security](SECURITY.md).

A source repository is not automatically licensed for redistribution. The project owner must choose a license for original code; upstream dependencies retain their existing licenses.
