#!/usr/bin/env python3
"""Stage image overlays and snapshot repositories without modifying source inputs."""

import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from scos.core import read_identity, verify_ca


def snapshot_sources(snapshot: str) -> str:
    """Use the same signed, dated repositories for the builder and deployed host."""
    entries = []
    archives = (
        ("debian", "trixie trixie-updates"),
        ("debian-security", "trixie-security"),
    )
    for archive, suites in archives:
        entries.append(
            "Types: deb\n"
            f"URIs: https://snapshot.debian.org/archive/{archive}/{snapshot}/\n"
            f"Suites: {suites}\n"
            "Components: main\n"
            "Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg\n"
            "Check-Valid-Until: no\n"
        )
    return "\n".join(entries)


def stage_overlay(root: Path, image: str, metadata: dict) -> Path:
    """Copy one image's filesystem and the shared runtime package into build/."""
    target = root / "build" / f"{image}-overlay"
    if target.exists():
        shutil.rmtree(target)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    shutil.copytree(root / "images" / image / "overlay", target, ignore=ignore)
    shutil.copytree(root / "lib/scos", target / "usr/local/lib/scos", ignore=ignore)

    metadata_directory = target / "usr/local/share/scos"
    metadata_directory.mkdir(parents=True, exist_ok=True)
    (metadata_directory / "build.json").write_text(
        json.dumps(metadata, sort_keys=True, indent=2) + "\n"
    )
    for command in (target / "usr/local/sbin").iterdir():
        if command.is_file():
            command.chmod(0o755)
    return target


def prepare(root: Path, *, source_commit: str, source_date_epoch: int) -> None:
    """Validate trust, then stage all inputs consumed by the two mkosi recipes."""
    read_identity(root / "config/identity.json")
    verify_ca(root / "trust/ipa-ca.crt", (root / "trust/ipa-ca.sha256").read_text())
    configuration = json.loads((root / "config/build.json").read_text())
    sources = snapshot_sources(configuration["snapshot"])
    metadata = {
        "source_commit": source_commit,
        "source_date_epoch": source_date_epoch,
        "configuration": configuration,
    }

    sandbox = root / "build/sandbox/etc/apt/sources.list.d"
    sandbox.mkdir(parents=True, exist_ok=True)
    (sandbox / "mkosi.sources").write_text(sources)
    server = stage_overlay(root, "server", metadata)
    stage_overlay(root, "installer", metadata)

    ca_directory = server / "usr/local/share/ca-certificates"
    ca_directory.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / "trust/ipa-ca.crt", ca_directory / "scos-ipa.crt")
    shutil.copy2(
        root / "trust/ipa-ca.sha256", server / "usr/local/share/scos/ipa-ca.sha256"
    )
    shutil.copy2(
        root / "config/identity.json", server / "usr/local/share/scos/identity.json"
    )

    apt = server / "etc/apt/sources.list.d"
    apt.mkdir(parents=True, exist_ok=True)
    (apt / "trixie.sources").write_text(sources)


def main() -> None:
    prepare(
        ROOT,
        source_commit=os.environ["SOURCE_COMMIT"],
        source_date_epoch=int(os.environ["SOURCE_DATE_EPOCH"]),
    )


if __name__ == "__main__":
    main()
