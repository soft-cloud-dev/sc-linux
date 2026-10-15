#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -n ${SCOS_SIGNING_DIR:-} ]]; then
    printf '%s\n' 'Reproducibility comparison requires unsigned builds.' >&2
    exit 1
fi
bash scripts/build.sh build/repro-a
bash scripts/build.sh build/repro-b
cmp build/repro-a/raw/sc-linux.raw build/repro-b/raw/sc-linux.raw
cmp build/repro-a/sc-linux.iso build/repro-b/sc-linux.iso
printf '%s\n' 'Independent builds produced identical RAW and ISO bytes.'
