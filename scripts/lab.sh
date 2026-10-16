#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v jupyter >/dev/null 2>&1; then
    printf '%s\n' 'JupyterLab is not installed. Install it in .venv, then run make lab.' >&2
    exit 1
fi
mkdir -p build/notebooks
for source in notebooks/*.ipynb; do
    destination="build/notebooks/${source##*/}"
    if [[ ! -e "$destination" ]]; then
        cp "$source" "$destination"
    fi
done
mkdir -p build/notebooks/book
for source in book/*.ipynb; do
    destination="build/notebooks/book/${source##*/}"
    if [[ ! -e "$destination" ]]; then
        cp "$source" "$destination"
    fi
done
printf '%s\n' 'Opening working notebooks in build/notebooks/ (ignored by Git).' >&2
printf '%s\n' 'Jupyter Book chapters: book/01-environment.ipynb through book/08-provision.ipynb' >&2
exec jupyter lab --ServerApp.root_dir="$PWD/build/notebooks"
