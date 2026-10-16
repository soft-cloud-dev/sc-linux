#!/usr/bin/env python3
"""Report server and installer image footprint from recorded build measurements."""

import argparse
import json
import sys
from pathlib import Path


def artifact_size(path: Path) -> int:
    if not path.is_file() or path.is_symlink() or path.stat().st_size == 0:
        raise ValueError("Missing, empty or nonregular artifact: " + str(path))
    return path.stat().st_size


def read_sizes(path: Path) -> list[tuple[int, str]]:
    artifact_size(path)
    rows = []
    for line in path.read_text().splitlines():
        fields = line.split("\t", 1)
        if len(fields) != 2 or not fields[0].isdigit() or not fields[1]:
            raise ValueError("Invalid size report entry: " + str(path))
        rows.append((int(fields[0]), fields[1]))
    if not rows:
        raise ValueError("Empty size report: " + str(path))
    return sorted(rows, key=lambda entry: (-entry[0], entry[1]))


def write_footprint(output: Path) -> dict:
    raw_size = artifact_size(output / "raw/sc-linux.raw")
    compressed_size = artifact_size(output / "sc-linux.raw.zst")
    iso_size = artifact_size(output / "sc-linux.iso")
    uki_size = artifact_size(output / "installer/sc-linux-installer.efi")
    packages = read_sizes(output / "raw/sc-linux.packages-kib.tsv")
    directories = read_sizes(output / "raw/sc-linux.directories-bytes.tsv")

    report = {
        "artifacts": {
            "uncompressed_raw_bytes": raw_size,
            "compressed_raw_bytes": compressed_size,
            "installer_iso_bytes": iso_size,
            "installer_uki_bytes": uki_size,
            "compressed_to_raw_ratio": round(compressed_size / raw_size, 5),
            "raw_compression_saved_bytes": raw_size - compressed_size,
            "iso_overhead_over_payload_bytes": iso_size - compressed_size,
        },
        "packages": {
            "count": len(packages),
            "sum_installed_size_kib": sum(size for size, _ in packages),
            "largest": [
                {"package": name, "installed_size_kib": size}
                for size, name in packages[:30]
            ],
        },
        "directories": [
            {"path": path, "bytes": size} for size, path in directories
        ],
        "notes": [
            "dpkg Installed-Size is a package metadata estimate in KiB.",
            "Directory sizes were measured in the mkosi rootfs before disk layout.",
            "RAW size includes partitions, file system overhead, and unused space.",
            "ISO size includes the compressed RAW plus its installer boot files.",
        ],
    }
    (output / "footprint.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    sizes = write_footprint(args.output)["artifacts"]
    print(
        "RAW: {uncompressed_raw_bytes} B; zstd: {compressed_raw_bytes} B; "
        "ISO: {installer_iso_bytes} B".format(**sizes)
    )


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        sys.exit(str(error))
