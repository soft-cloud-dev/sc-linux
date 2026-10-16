#!/usr/bin/env bash
# Use the same toolchain for construction and disposable VM acceptance tests.
set -euo pipefail
cd "$(dirname "$0")/.."

output_directory=$(realpath "${1:-build/output}")
builder_image=$(cat build/builder.id)

docker run --rm --privileged --platform linux/amd64 \
    --mount "type=bind,src=$PWD,dst=/src,readonly" \
    --mount "type=bind,src=$output_directory,dst=/out" \
    "$builder_image" bash scripts/notebook.sh notebooks/smoke.ipynb /out
