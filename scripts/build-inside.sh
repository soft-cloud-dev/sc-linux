#!/usr/bin/env bash
# Container entrypoint: stage inputs, build both images, and record provenance.
set -euo pipefail

stage() {
    printf 'SCOS_BUILD_STAGE %s\n' "$1"
}

verify_toolchain() {
    stage verify-toolchain
    [[ $(dpkg-query -W -f='${Version}' mkosi) == 25.3-7 ]]
    : "${SOURCE_DATE_EPOCH:?}" "${SOURCE_COMMIT:?}"
}

prepare_workspace() {
    stage prepare-workspace
    work_directory=$(mktemp -d /var/tmp/sc-linux.XXXXXX)
    trap 'rm -rf "$work_directory"' EXIT

    tar -C /src \
        --exclude=./.git --exclude=./build --exclude=./dist \
        --exclude=__pycache__ --exclude='*.pyc' -cf - . |
        tar -C "$work_directory" -xf -
    cd "$work_directory"
}

validate_and_stage_inputs() {
    stage validate-and-stage-inputs
    bash scripts/notebook.sh notebooks/check.ipynb --require-trust
    bash scripts/notebook.sh notebooks/prepare.ipynb
    partition_seed=$(python3 -c 'import json; print(json.load(open("config/build.json"))["seed"])')
}

configure_efi_signing() {
    stage configure-efi-signing
    signing_arguments=()
    if [[ -d /signing ]]; then
        signing_arguments=(
            --secure-boot=yes
            --secure-boot-key=/signing/private.key
            --secure-boot-certificate=/signing/certificate.pem
            --secure-boot-auto-enroll=no
        )
    fi
}

build_server_raw() {
    stage build-server-raw
    mkdir -p /out/raw /out/installer

    # The server is the payload installed by both deployment paths.
    mkosi -C images/server \
        --output-directory=/out/raw \
        --source-date-epoch="$SOURCE_DATE_EPOCH" \
        --seed="$partition_seed" \
        "${signing_arguments[@]}" build
    test -s /out/raw/sc-linux.raw
}

compress_server_raw() {
    stage compress-server-raw
    zstd -T1 -19 --no-progress /out/raw/sc-linux.raw -o /out/sc-linux.raw.zst
}

record_installer_payload() {
    stage record-installer-payload
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
}

build_installer_uki() {
    stage build-installer-uki
    mkosi -C images/installer \
        --output-directory=/out/installer \
        --source-date-epoch="$SOURCE_DATE_EPOCH" \
        "${signing_arguments[@]}" build
    test -s /out/installer/sc-linux-installer.efi
}

assemble_installer_iso() {
    stage assemble-installer-iso
    bash scripts/notebook.sh notebooks/make-iso.ipynb \
        /out/installer/sc-linux-installer.efi /out/sc-linux.raw.zst /out/sc-linux.iso
}

record_build_evidence() {
    stage record-build-evidence
    bash scripts/notebook.sh notebooks/artifacts.ipynb /out
    bash scripts/notebook.sh notebooks/footprint.ipynb /out
    cp config/build.json /out/build-config.json
    dpkg-query -W -f='${binary:Package}\t${Version}\n' > /out/builder-packages.tsv
    printf '%s\n' "$SOURCE_COMMIT" > /out/source-commit.txt
    printf '%s\n' "$SOURCE_DATE_EPOCH" > /out/source-date-epoch.txt
}
main() {
    verify_toolchain
    prepare_workspace
    validate_and_stage_inputs
    configure_efi_signing
    build_server_raw
    compress_server_raw
    record_installer_payload
    build_installer_uki
    assemble_installer_iso
    record_build_evidence
}

main "$@"
