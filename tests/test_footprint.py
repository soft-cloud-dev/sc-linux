"""Verify footprint parsing and artifact-size reporting without a disk build."""

import json
import tempfile
import unittest
from pathlib import Path

from support import ROOT, load


class FootprintTests(unittest.TestCase):
    def setUp(self):
        self.module = load("footprint", ROOT / "notebooks/footprint.ipynb")

    def test_artifact_sizes_and_largest_packages(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            (output / "raw").mkdir()
            (output / "installer").mkdir()
            for path, size in (
                ("raw/sc-linux.raw", 200),
                ("sc-linux.raw.zst", 50),
                ("sc-linux.iso", 80),
                ("installer/sc-linux-installer.efi", 20),
            ):
                (output / path).write_bytes(b"x" * size)
            (output / "raw/sc-linux.packages-kib.tsv").write_text(
                "8\tsssd-ipa\n25\tlinux-image-amd64\n"
            )
            (output / "raw/sc-linux.directories-bytes.tsv").write_text(
                "400\t/usr\n100\t/etc\n"
            )
            report = self.module.write_footprint(output)
            self.assertEqual(report["artifacts"]["uncompressed_raw_bytes"], 200)
            self.assertEqual(report["artifacts"]["raw_compression_saved_bytes"], 150)
            self.assertEqual(report["packages"]["sum_installed_size_kib"], 33)
            self.assertEqual(
                report["packages"]["largest"][0]["package"], "linux-image-amd64"
            )
            self.assertEqual(report["directories"][0]["bytes"], 400)
            self.assertEqual(
                json.loads((output / "footprint.json").read_text()), report
            )

    def test_invalid_inputs_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            with self.assertRaises(ValueError):
                self.module.write_footprint(output)
            invalid = output / "bad.tsv"
            invalid.write_text("not-a-number\tpackage\n")
            with self.assertRaises(ValueError):
                self.module.read_sizes(invalid)


if __name__ == "__main__":
    unittest.main()
