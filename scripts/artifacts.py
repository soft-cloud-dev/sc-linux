#!/usr/bin/env python3
"""Write hashes and sizes for the completed RAW and ISO artifacts."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from scos.core import describe_file

ARTIFACT_NAMES = ("sc-linux.raw.zst", "sc-linux.iso")
MINIMUM_IMAGE_BYTES = 1024 * 1024


def write_manifest(output: Path) -> None:
    manifest = {name: describe_file(output / name) for name in ARTIFACT_NAMES}
    if any(record["size"] < MINIMUM_IMAGE_BYTES for record in manifest.values()):
        raise ValueError("Image artifacts are implausibly small")
    (output / "artifacts.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n"
    )
    checksums = "".join(
        f'{record["sha256"]}  {name}\n' for name, record in manifest.items()
    )
    (output / "SHA256SUMS").write_text(checksums)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output", type=Path, help="Directory containing both completed images"
    )
    arguments = parser.parse_args()
    write_manifest(arguments.output)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        sys.exit(str(error))
