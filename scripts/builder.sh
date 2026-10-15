#!/usr/bin/env bash
# Resolve the base image once and record the exact local builder identity.
set -euo pipefail
cd "$(dirname "$0")/.."

command -v docker >/dev/null
mkdir -p build
snapshot=$(python3 -c 'import json; print(json.load(open("config/build.json"))["snapshot"])')
mkosi_version=$(python3 -c 'import json; print(json.load(open("config/build.json"))["mkosi_package"])')
base_image=${SCOS_BASE_IMAGE:-debian:trixie-slim}

docker pull --platform linux/amd64 "$base_image"
base_digest=$(docker image inspect "$base_image" --format '{{index .RepoDigests 0}}')
[[ "$base_digest" == *@sha256:* ]]

docker build --platform linux/amd64 \
    --build-arg "BASE_IMAGE=$base_digest" \
    --build-arg "SNAPSHOT=$snapshot" \
    --build-arg "MKOSI_PACKAGE=$mkosi_version" \
    -t sc-linux-builder:local .

docker image inspect sc-linux-builder:local --format '{{.Id}}' > build/builder.id
printf '%s\n' "$base_digest" > build/builder-base.txt
