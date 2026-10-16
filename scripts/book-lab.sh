#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v jupyter >/dev/null 2>&1; then
    printf '%s\n' 'JupyterLab is missing. Install it in your local development environment.' >&2
    exit 1
fi

mkdir -p build/book-notebooks
for source in book/*.ipynb; do
    target="build/book-notebooks/${source##*/}"
    if [[ ! -e "$target" ]]; then
        cp "$source" "$target"
    fi
done

printf '%s\n' 'Opening ignored Jupyter Book working copies under build/book-notebooks.' >&2
printf '%s\n' 'To contribute edits, copy notebooks back into book/ and clear their outputs.' >&2
exec jupyter lab --ServerApp.root_dir="$PWD/build/book-notebooks"
