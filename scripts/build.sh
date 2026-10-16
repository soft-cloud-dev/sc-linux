#!/usr/bin/env bash
# Run one build from committed source, with optional external EFI signing keys.
set -euo pipefail
cd "$(dirname "$0")/.."

fail() {
    printf '%s\n' "$*" >&2
    exit 1
}

bash scripts/notebook.sh notebooks/check.ipynb --require-trust
[[ -s build/builder.id ]] || fail 'Run make builder first.'
[[ -z $(git status --porcelain --untracked-files=normal) ]] ||
    fail 'Commit source and CA changes before building.'

source_directory=$PWD
output_directory=$(realpath -m "${1:-build/output}")
mkdir -p "$output_directory"
[[ -z $(ls -A "$output_directory") ]] ||
    fail "Output directory must be empty: $output_directory"

source_epoch=$(git show -s --format=%ct HEAD)
source_commit=$(git rev-parse HEAD)
builder_image=$(cat build/builder.id)
signing_arguments=()

if [[ -n ${SCOS_SIGNING_DIR:-} ]]; then
    signing_directory=$(realpath "$SCOS_SIGNING_DIR")
    [[ -s "$signing_directory/private.key" && -s "$signing_directory/certificate.pem" ]] ||
        fail 'Signing directory must contain private.key and certificate.pem.'
    signing_arguments+=(--mount "type=bind,src=$signing_directory,dst=/signing,readonly")
fi

docker run --rm --privileged --platform linux/amd64 \
    --mount "type=bind,src=$source_directory,dst=/src,readonly" \
    --mount "type=bind,src=$output_directory,dst=/out" \
    --env "SOURCE_DATE_EPOCH=$source_epoch" \
    --env "SOURCE_COMMIT=$source_commit" \
    "${signing_arguments[@]}" \
    "$builder_image" bash /src/scripts/build-inside.sh

cp build/builder.id build/builder-base.txt "$output_directory/"
