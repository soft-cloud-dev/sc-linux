#!/usr/bin/env python3
"""Build a UEFI El Torito ISO with a full installer UKI and RAW payload."""

import argparse
import os
import pathlib
import shutil
import subprocess
import tempfile
import time


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("uki", type=pathlib.Path)
    p.add_argument("payload", type=pathlib.Path)
    p.add_argument("output", type=pathlib.Path)
    args = p.parse_args()
    for file in (args.uki, args.payload):
        if not file.is_file() or file.stat().st_size == 0:
            raise ValueError("Missing installer input: " + str(file))
    epoch = int(os.environ["SOURCE_DATE_EPOCH"])
    with tempfile.TemporaryDirectory(prefix="scos-iso-") as tmp:
        stage = pathlib.Path(tmp)
        esp = stage / "esp.img"
        size = (
            (args.uki.stat().st_size + 64 * 1024 * 1024 + 1024 * 1024 - 1)
            // (1024 * 1024)
        ) * (1024 * 1024)
        with esp.open("wb") as f:
            f.truncate(size)
        subprocess.run(
            ["mkfs.vfat", "--invariant", "-F", "32", "-n", "SCOS_EFI", str(esp)],
            check=True,
        )
        subprocess.run(["mmd", "-i", str(esp), "::/EFI", "::/EFI/BOOT"], check=True)
        uki = stage / "BOOTX64.EFI"
        shutil.copyfile(args.uki, uki)
        os.utime(uki, (epoch, epoch))
        subprocess.run(
            ["mcopy", "-m", "-i", str(esp), str(uki), "::/EFI/BOOT/BOOTX64.EFI"],
            check=True,
        )
        uki.unlink()
        shutil.copyfile(args.payload, stage / "sc-linux.raw.zst")
        for file in stage.iterdir():
            os.utime(file, (epoch, epoch))
        stamp = time.strftime("%Y%m%d%H%M%S00", time.gmtime(epoch))
        subprocess.run(
            [
                "xorriso",
                "-as",
                "mkisofs",
                "-iso-level",
                "3",
                "-R",
                "-J",
                "-V",
                "SCOS_INSTALL",
                "--modification-date=" + stamp,
                "-e",
                "esp.img",
                "-no-emul-boot",
                "-o",
                str(args.output.resolve()),
                str(stage),
            ],
            check=True,
        )


if __name__ == "__main__":
    main()
