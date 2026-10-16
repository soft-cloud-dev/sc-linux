# Work with notebooks

[Home](../README.md) · [Build](building.md) · [Contributing](../CONTRIBUTING.md)

SC Linux has three notebook entry points. They share the same build pipeline.

| Notebook set | Purpose | Open with |
| --- | --- | --- |
| [`book/`](../book/index.md) | Nine chapters explaining the build one action at a time | `make book-lab` |
| [`notebooks/01-*` through `04-*`](../notebooks/01-validate.ipynb) | A compact validate → build → inspect → smoke-test workflow | `make lab` |
| Named operation notebooks in [`notebooks/`](../notebooks) | Canonical implementation used by Make and CI | `make lab` or the command-line runner |

## Use the command line

Jupyter is not required for Make or CI. The standard-library runner executes an operation's Python cells in order, without executing Markdown or installing dependencies:

```sh
bash scripts/notebook.sh notebooks/check.ipynb
```

| Operation | Responsibility |
| --- | --- |
| [check](../notebooks/check.ipynb) | Validate source and configuration |
| [trust](../notebooks/trust.ipynb) | Import a reviewed public FreeIPA CA |
| [prepare](../notebooks/prepare.ipynb) | Stage image inputs and the apt snapshot configuration |
| [make-iso](../notebooks/make-iso.ipynb) | Assemble the UEFI installer ISO |
| [artifacts](../notebooks/artifacts.ipynb) | Generate artifact hashes and metadata |
| [footprint](../notebooks/footprint.ipynb) | Report disk, ISO and package sizes |
| [seed](../notebooks/seed.ipynb) | Create a host-specific NoCloud seed |
| [smoke](../notebooks/smoke.ipynb) | Run disposable QEMU acceptance tests |

Use the [build](building.md), [installation](installing.md) and [identity](identity.md) guides for operation arguments and prerequisites. The runner accepts notebooks under `notebooks/`; book chapters run interactively in JupyterLab.

## Set up JupyterLab

Run these commands from the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install jupyterlab
make lab
```

Start with [01 · Validate](../notebooks/01-validate.ipynb), then [02 · Build](../notebooks/02-build.ipynb), [03 · Inspect](../notebooks/03-inspect.ipynb) and [04 · Smoke-test](../notebooks/04-smoke.ipynb).

For the longer teaching sequence, run `make book-lab` from the same activated environment and start with `01-environment.ipynb`. Image-building cells still require the host prerequisites in the [build guide](building.md).

## Working copies and contributions

The launchers copy source notebooks into ignored directories before opening JupyterLab:

| Command | Working directory | Canonical source |
| --- | --- | --- |
| `make lab` | `build/notebooks/` | `notebooks/` |
| `make book-lab` | `build/book-notebooks/` | `book/` |

Repeated launches preserve existing working copies. **They do not refresh those copies after a Git pull.** To load an updated source notebook, first save any local edits, then remove only its working copy and rerun the launcher.

To contribute an edit, deliberately copy the reviewed file back to its canonical directory. Clear code-cell outputs and execution counts before committing. Make and CI use canonical notebooks, so edits left only under `build/` do not change the image pipeline.

Keep credentials, private keys and enrollment passwords out of notebook cells and outputs. Jupyter belongs on the development host, not in the installed OS.

## Render the book

With the virtual environment activated, install the pinned documentation dependency and build static HTML:

```sh
python -m pip install -r requirements-book.txt
make book
```

`make book` uses strict mode. `make book-html` renders without strict mode. Both render without executing notebook cells. Do not add `--execute`: the chapters include local commands and privileged image-building operations.
