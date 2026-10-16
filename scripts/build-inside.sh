#!/usr/bin/env bash
# Container entrypoint: stage inputs, build both images, and record provenance.
set -euo pipefail

[[ $(dpkg-query -W -f='${Version}' mkosi) == 25.3-7 ]]
: "${SOURCE_DATE_EPOCH:?}" "${SOURCE_COMMIT:?}"

work_directory=$(mktemp -d /var/tmp/sc-linux.XXXXXX)
trap 'rm -rf "$work_directory"' EXIT

tar -C /src \
    --exclude=./.git --exclude=./build --exclude=./dist \
    --exclude=__pycache__ --exclude='*.pyc' -cf - . |
    tar -C "$work_directory" -xf -
cd "$work_directory"

python3 scripts/check.py --require-trust
python3 scripts/prepare.py
partition_seed=$(python3 -c 'import json; print(json.load(open("config/build.json"))["seed"])')

signing_arguments=()
if [[ -d /signing ]]; then
    signing_arguments=(
        --secure-boot=yes
        --secure-boot-key=/signing/private.key
        --secure-boot-certificate=/signing/certificate.pem
        --secure-boot-auto-enroll=no
    )
fi

mkdir -p /out/raw /out/installer

# The server is the payload installed by both deployment paths.
mkosi -C images/server \
    --output-directory=/out/raw \
    --source-date-epoch="$SOURCE_DATE_EPOCH" \
    --seed="$partition_seed" \
    "${signing_arguments[@]}" build
test -s /out/raw/sc-linux.raw
zstd -T1 -19 --no-progress /out/raw/sc-linux.raw -o /out/sc-linux.raw.zst

# Embed the expected payload digest in the installer before building its UKI.
PYTHONPATH=lib python3 - <<'PY'
import json
from pathlib import Path
from scos.core import describe_file

manifest = {
    'raw': describe_file('/out/raw/sc-linux.raw'),
    'compressed': describe_file('/out/sc-linux.raw.zst'),
}
text = json.dumps(manifest, sort_keys=True, indent=2) + '\n'
Path('build/installer-overlay/usr/local/share/scos/payload.json').write_text(text)
Path('/out/payload.json').write_text(text)
PY

mkosi -C images/installer \
    --output-directory=/out/installer \
    --source-date-epoch="$SOURCE_DATE_EPOCH" \
    "${signing_arguments[@]}" build
test -s /out/installer/sc-linux-installer.efi
python3 scripts/make-iso.py \
    /out/installer/sc-linux-installer.efi /out/sc-linux.raw.zst /out/sc-linux.iso

python3 scripts/artifacts.py /out
python3 scripts/footprint.py /out
cp config/build.json /out/build-config.json
dpkg-query -W -f='${binary:Package}\t${Version}\n' > /out/builder-packages.tsv
printf '%s\n' "$SOURCE_COMMIT" > /out/source-commit.txt
printf '%s\n' "$SOURCE_DATE_EPOCH" > /out/source-date-epoch.txt
