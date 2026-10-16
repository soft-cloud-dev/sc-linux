#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v jupyter >/dev/null 2>&1; then
    printf '%s\n' 'JupyterLab is required. Install it in a local virtual environment.' >&2
    exit 1
fi

mkdir -p build/book-notebooks
for source in book/*.ipynb book/*.md; do
    destination="build/book-notebooks/${source##*/}"
    if [[ ! -e "$destination" ]]; then
        cp "$source" "$destination"
    fi
done

printf '%s\n' 'Editing ignored working copies in build/book-notebooks/' >&2
exec jupyter lab --ServerApp.root_dir="$PWD/build/book-notebooks"
